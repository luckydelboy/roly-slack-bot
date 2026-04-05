"""
Conversation handlers — respond when the bot is @mentioned or DM'd.

Detects intent from natural language and routes to the real pipelines
(research, advertorial, listicle) instead of just chatting.
"""

import logging
import re
import threading
import traceback

from slack_bolt import App

from claude_client import chat
from utils.slack_helpers import post_progress, post_long_message
import knowledge_base

logger = logging.getLogger(__name__)


def _detect_intent(text: str) -> dict:
    """Detect if the message is asking for research, advertorial, or listicle.
    Returns {'intent': str, 'url': str|None, 'brief': str} or None for regular chat."""
    text_lower = text.lower()

    # Detect research intent — look for URLs + research-related words
    # Slack wraps URLs in angle brackets: <https://example.com> or <https://example.com|example.com>
    url_match = re.search(r'<?(https?://[^\s>|]+)', text)
    url = url_match.group(1) if url_match else None

    research_words = ["research", "scrape", "analyze", "look into", "check out", "dig into", "investigate"]
    if url and any(w in text_lower for w in research_words):
        return {"intent": "research", "url": url, "brief": text}

    # Also catch "research <url>" even without explicit research words
    if url and ("research" in text_lower or "brand" in text_lower):
        return {"intent": "research", "url": url, "brief": text}

    # If someone just drops a URL with "research", catch it
    if url and text_lower.strip().startswith("research"):
        return {"intent": "research", "url": url, "brief": text}

    # Detect advertorial intent — but NOT questions about status like "are you writing the advertorial?"
    advertorial_words = ["advertorial", "story page", "presell", "pre-sell", "editorial page", "native ad", "landing page"]
    status_words = ["are you", "is it", "how's the", "status", "done yet", "finished"]
    is_status_question = any(w in text_lower for w in status_words)

    if any(w in text_lower for w in advertorial_words) and not is_status_question:
        # Check if it's specifically a listicle
        listicle_words = ["listicle", "list of reasons", "reasons why", "numbered list", "top 5", "top 7", "top 10"]
        if any(w in text_lower for w in listicle_words):
            return {"intent": "listicle", "url": None, "brief": text}
        return {"intent": "advertorial", "url": None, "brief": text}

    # Detect listicle intent
    listicle_words = ["listicle", "list of reasons", "reasons why", "write a list", "numbered article"]
    if any(w in text_lower for w in listicle_words):
        return {"intent": "listicle", "url": None, "brief": text}

    return None


def _run_research_from_chat(client, channel, thread_ts, user, url):
    """Run the research pipeline triggered from a chat message."""
    from research.pipeline import run_research

    post_progress(client, channel, thread_ts, "mag",
                  f"<@{user}> On it — running full research on `{url}`\n"
                  "This takes 2-5 minutes. I'll post updates as I go.")

    try:
        def progress_callback(emoji, message):
            post_progress(client, channel, thread_ts, emoji, message)

        run_research(url, progress=progress_callback)

    except ValueError as e:
        post_progress(client, channel, thread_ts, "x", f"Research failed: {e}")
    except Exception as e:
        logger.error(f"Research pipeline error: {traceback.format_exc()}")
        post_progress(client, channel, thread_ts, "x",
                      f"Research failed: {type(e).__name__}: {e}")


def _run_advertorial_from_chat(client, channel, thread_ts, user, brief, is_listicle=False):
    """Run the advertorial/listicle pipeline triggered from a chat message."""
    from handlers.advertorial import (
        _detect_format, _detect_client, _extract_topic_hint,
        _build_advertorial_system, _build_listicle_system, _clean_html_output,
    )
    from claude_client import long_creative_request
    from config import ADVERTORIAL_MAX_TOKENS, LISTICLE_MAX_TOKENS
    from deployer.vercel import deploy_html, generate_project_name

    format_type = "listicle" if is_listicle else _detect_format(brief)
    client_slug = _detect_client(brief)
    label = "listicle" if is_listicle else f"{format_type} advertorial"

    logger.info(f"PIPELINE TRIGGERED: {label} | client={client_slug} | brief={brief[:80]}")

    post_progress(client, channel, thread_ts, "pencil2",
                  f"Building a *{label}*"
                  f"{'  — using `' + client_slug + '` research' if client_slug else ''}")

    try:
        # Load context
        if client_slug:
            context = knowledge_base.load_client_research(client_slug)
        else:
            context = knowledge_base.load_for_creative()

        post_progress(client, channel, thread_ts, "brain", "Generating copy + HTML...")

        # Generate
        if is_listicle:
            system = _build_listicle_system()
            max_tokens = LISTICLE_MAX_TOKENS
        else:
            system = _build_advertorial_system(format_type)
            max_tokens = ADVERTORIAL_MAX_TOKENS

        html_output = long_creative_request(system, context, brief, max_tokens)
        html_output = _clean_html_output(html_output)

        if not html_output.strip().startswith("<!DOCTYPE") and not html_output.strip().startswith("<html"):
            post_progress(client, channel, thread_ts, "warning",
                          "Output wasn't valid HTML. Posting as text instead.")
            post_long_message(client, channel, thread_ts, html_output)
            return

        # Deploy
        post_progress(client, channel, thread_ts, "rocket", "Deploying to Vercel...")
        topic_hint = _extract_topic_hint(brief)
        project_name = generate_project_name(client_slug or "roly", topic_hint)
        live_url = deploy_html(html_output, project_name)

        post_progress(client, channel, thread_ts, "white_check_mark",
                      f"*{label.title()} is live!*\n\n"
                      f":link: {live_url}\n\n"
                      f"Project: `{project_name}`")

    except RuntimeError as e:
        post_progress(client, channel, thread_ts, "warning",
                      f"Vercel deployment failed: {e}\nPosting the HTML as text.")
        try:
            post_long_message(client, channel, thread_ts, f"```{html_output[:3800]}```")
        except Exception:
            pass
    except Exception as e:
        logger.error(f"Advertorial error: {traceback.format_exc()}")
        post_progress(client, channel, thread_ts, "x",
                      f"Generation failed: {type(e).__name__}: {e}")


def register(app: App):
    """Register all conversation-related listeners."""

    @app.event("app_mention")
    def handle_mention(event, say, client):
        """Respond when someone @mentions the bot in a channel."""
        user = event["user"]
        text = event.get("text", "")
        channel = event["channel"]
        thread_ts = event.get("thread_ts", event["ts"])

        # Strip the bot mention from the message text
        text = re.sub(r"<@[A-Z0-9]+>", "", text).strip()

        if not text:
            say(
                text=f"Hey <@{user}>! Ask me anything — I'm powered by Claude.",
                thread_ts=thread_ts,
            )
            return

        # Show a typing indicator while Claude thinks
        client.reactions_add(channel=channel, name="thinking_face", timestamp=event["ts"])

        # Check if this is a pipeline request (research, advertorial, listicle)
        intent = _detect_intent(text)
        logger.info(f"Intent detection for '{text[:50]}...': {intent}")

        if intent:
            # Remove thinking face — pipeline will post its own progress
            try:
                client.reactions_remove(channel=channel, name="thinking_face", timestamp=event["ts"])
            except Exception:
                pass

            if intent["intent"] == "research":
                thread = threading.Thread(
                    target=_run_research_from_chat,
                    args=(client, channel, thread_ts, user, intent["url"]),
                    daemon=True,
                )
                thread.start()

            elif intent["intent"] == "advertorial":
                thread = threading.Thread(
                    target=_run_advertorial_from_chat,
                    args=(client, channel, thread_ts, user, intent["brief"], False),
                    daemon=True,
                )
                thread.start()

            elif intent["intent"] == "listicle":
                thread = threading.Thread(
                    target=_run_advertorial_from_chat,
                    args=(client, channel, thread_ts, user, intent["brief"], True),
                    daemon=True,
                )
                thread.start()

            return

        # Regular chat — no pipeline detected
        response = chat(channel, thread_ts, text)
        say(text=response, thread_ts=thread_ts)

        # Remove the thinking indicator
        try:
            client.reactions_remove(channel=channel, name="thinking_face", timestamp=event["ts"])
        except Exception:
            pass

    @app.event("message")
    def handle_dm(event, say, client):
        """Respond to direct messages (DMs) to the bot."""
        # Only handle DMs (channel type 'im'), ignore bot messages
        if event.get("channel_type") != "im":
            return
        if event.get("bot_id") or event.get("subtype"):
            return

        user = event["user"]
        text = event.get("text", "")
        channel = event["channel"]
        thread_ts = event.get("thread_ts", event["ts"])

        if not text:
            return

        # Check for pipeline intents in DMs too
        intent = _detect_intent(text)

        if intent:
            if intent["intent"] == "research":
                thread = threading.Thread(
                    target=_run_research_from_chat,
                    args=(client, channel, thread_ts, user, intent["url"]),
                    daemon=True,
                )
                thread.start()
            elif intent["intent"] == "advertorial":
                thread = threading.Thread(
                    target=_run_advertorial_from_chat,
                    args=(client, channel, thread_ts, user, intent["brief"], False),
                    daemon=True,
                )
                thread.start()
            elif intent["intent"] == "listicle":
                thread = threading.Thread(
                    target=_run_advertorial_from_chat,
                    args=(client, channel, thread_ts, user, intent["brief"], True),
                    daemon=True,
                )
                thread.start()
            return

        # Regular chat
        logger.info(f"DM from {user}: {text[:80]}...")
        response = chat(channel, thread_ts, text)
        say(text=response, thread_ts=thread_ts)
