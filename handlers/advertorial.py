"""
Advertorial & Listicle handlers — generate full HTML advertorials and deploy to Vercel.

Slash commands:
    /advertorial <brief>  — Generate a full advertorial, deploy to Vercel
    /listicle <brief>     — Generate a listicle-format advertorial, deploy to Vercel
"""

from __future__ import annotations

import logging
import os
import threading
import traceback

from slack_bolt import App

import knowledge_base
from claude_client import long_creative_request
from config import ADVERTORIAL_MAX_TOKENS, LISTICLE_MAX_TOKENS
from deployer.vercel import deploy_html, generate_project_name
from utils.slack_helpers import post_progress, post_long_message

logger = logging.getLogger(__name__)


def _load_framework_file(filename: str) -> str:
    """Load a framework file from knowledge/frameworks/."""
    path = os.path.join(os.path.dirname(__file__), "..", "knowledge", "frameworks", filename)
    try:
        with open(path, "r") as f:
            return f.read().strip()
    except Exception:
        return ""


# Load the REAL skill files — not summaries
_ADVERTORIAL_SKILL = _load_framework_file("advertorial-skill.md")
_COPY_FRAMEWORKS = _load_framework_file("advertorial-copy-frameworks.md")
_HTML_TEMPLATE_GUIDE = _load_framework_file("advertorial-html-template-guide.md")
_COPY_QUALITY_RULES = _load_framework_file("copy-quality-rules.md")


def _detect_format(brief: str) -> str:
    """Detect advertorial format from keywords in the brief."""
    brief_lower = brief.lower()
    if "authority" in brief_lower or "confession" in brief_lower or "doctor" in brief_lower:
        return "authority-confession"
    if "editorial" in brief_lower or "journal" in brief_lower or "news" in brief_lower:
        return "editorial"
    if "listicle" in brief_lower or "reasons" in brief_lower or "list" in brief_lower:
        return "listicle"
    return "personal-story"


def _detect_client(brief: str) -> str | None:
    """Try to match a client name from the brief against known clients.
    Prefers the longest match to avoid 'bekynd' matching before 'bekyndbeauty'.
    Also handles partial matches like 'bekynd beauty' -> 'bekyndbeauty'."""
    clients = knowledge_base.list_clients()
    brief_lower = brief.lower().replace(" ", "")  # "bekynd beauty" -> "bekyndbeauty"
    brief_words = brief.lower()

    matches = []
    for client_slug in clients:
        # Direct match in the brief text
        if client_slug in brief_words or client_slug in brief_lower:
            matches.append(client_slug)

    if not matches:
        return None

    # Return the longest match — "bekyndbeauty" over "bekynd"
    return max(matches, key=len)


def _extract_topic_hint(brief: str) -> str:
    """Extract a topic hint from the brief for Vercel naming."""
    # Take the first few meaningful words, skip the client name and format
    skip_words = {
        "advertorial", "listicle", "personal-story", "authority-confession",
        "editorial", "for", "about", "write", "create", "generate", "build",
        "please", "the", "a", "an",
    }
    words = brief.lower().split()
    meaningful = [w for w in words if w not in skip_words and len(w) > 2][:5]
    return " ".join(meaningful)


def _build_advertorial_system(format_type: str) -> str:
    """Build the full system prompt for advertorial generation."""
    format_instructions = {
        "personal-story": (
            "Write in PERSONAL STORY format. First-person 'I' voice throughout. "
            "The writer IS the customer telling their story. "
            "Structure: My problem → What I tried → Why it failed → How I discovered this → My results → Why you should try it."
        ),
        "authority-confession": (
            "Write in AUTHORITY CONFESSION format. A professional confesses they were wrong. "
            "Structure: My credentials → What I used to recommend → Why I was wrong → The real root cause → What I recommend now → The proof. "
            "The professional takes blame and shifts it AWAY from the reader."
        ),
        "editorial": (
            "Write in EDITORIAL/JOURNAL format. Third-person news-style reporting. "
            "Structure: News hook → The problem millions face → The hidden cause → The breakthrough → How it works → Where to get it. "
            "Should read like a legitimate health/lifestyle article."
        ),
        "listicle": (
            "Write in LISTICLE format. Numbered reasons or discoveries (7-10 points). "
            "Each point builds the case. Product reveal around point 4-5. "
            "Remaining points stack proof. Final point transitions to CTA."
        ),
    }

    format_note = format_instructions.get(format_type, format_instructions["personal-story"])

    return (
        f"## FORMAT FOR THIS ADVERTORIAL: {format_type.upper()}\n{format_note}\n\n"
        "---\n\n"
        f"## ADVERTORIAL SKILL (Follow this EXACTLY):\n{_ADVERTORIAL_SKILL}\n\n"
        "---\n\n"
        f"## COPY FRAMEWORKS REFERENCE:\n{_COPY_FRAMEWORKS}\n\n"
        "---\n\n"
        f"## HTML TEMPLATE GUIDE (Follow this EXACTLY for all HTML output):\n{_HTML_TEMPLATE_GUIDE}\n\n"
        "---\n\n"
        f"## COPY QUALITY RULES (MANDATORY — self-audit before delivering):\n{_COPY_QUALITY_RULES}\n\n"
        "---\n\n"
        "## CRITICAL OUTPUT INSTRUCTION:\n"
        "Output a COMPLETE, SELF-CONTAINED HTML FILE following the HTML Template Guide above exactly. "
        "Use the typography system, color system, and required page elements specified. "
        "Include ALL 15 required elements (category bar, site header, nav, headline, byline, hero image, "
        "body copy, pull quotes, product images, stats bar, testimonial cards, CTA buttons, sticky mobile CTA, "
        "comparison table if relevant, footer with disclosure). "
        "Use Lora for body copy, Inter for UI. Use the accent color that matches the niche.\n\n"
        "Use [IMAGE PLACEHOLDER: description] for any images you don't have URLs for.\n"
        "Use https://www.bekyndbeauty.com/products/scalp-scrub as the default CTA link if no URL is provided.\n\n"
        "ABSOLUTE RULE: Your response must start with <!DOCTYPE html> as the VERY FIRST CHARACTER. "
        "Do NOT write any introduction, explanation, notes, or commentary before or after the HTML. "
        "Do NOT wrap in markdown code fences. Do NOT say 'here is the advertorial'. "
        "JUST THE RAW HTML. Nothing else. First character = <, last character = >"
    )


def _build_listicle_system() -> str:
    """Build the system prompt specifically for listicle format."""
    return _build_advertorial_system("listicle")


def register(app: App):
    """Register advertorial and listicle slash commands."""

    @app.command("/advertorial")
    def handle_advertorial(ack, command, respond, client):
        """Generate a full advertorial and deploy to Vercel."""
        ack()

        brief = command.get("text", "").strip()
        if not brief:
            respond(
                "Usage: `/advertorial <brief>`\n\n"
                "Example: `/advertorial bekynd personal-story scalp scrub for women 35-55 with psoriasis`\n\n"
                "Formats: `personal-story` (default), `authority-confession`, `editorial`\n\n"
                "If the client has been researched (via `/research`), I'll auto-load their data."
            )
            return

        channel = command["channel_id"]
        user = command["user_id"]
        format_type = _detect_format(brief)
        client_slug = _detect_client(brief)

        initial = client.chat_postMessage(
            channel=channel,
            text=(
                f":pencil2: <@{user}> requested a *{format_type}* advertorial\n"
                f"{'Using `' + client_slug + '` research' if client_slug else 'No client research found — using general context'}\n"
                "This takes 60-120 seconds."
            ),
        )
        thread_ts = initial["ts"]

        def _run():
            try:
                # Load context
                if client_slug:
                    context = knowledge_base.load_client_research(client_slug)
                else:
                    context = knowledge_base.load_for_creative()

                post_progress(client, channel, thread_ts, "brain", "Generating advertorial copy + HTML...")

                # Generate the advertorial
                system = _build_advertorial_system(format_type)
                html_output = long_creative_request(system, context, brief, ADVERTORIAL_MAX_TOKENS)

                # Clean any markdown wrapper if Claude added one
                html_output = _clean_html_output(html_output)

                if not html_output.strip().startswith("<!DOCTYPE") and not html_output.strip().startswith("<html"):
                    post_progress(client, channel, thread_ts, "warning",
                                  "Output wasn't valid HTML. Posting as text instead.")
                    post_long_message(client, channel, thread_ts, html_output)
                    return

                # Deploy to Vercel
                post_progress(client, channel, thread_ts, "rocket", "Deploying to Vercel...")

                topic_hint = _extract_topic_hint(brief)
                project_name = generate_project_name(client_slug or "roly", topic_hint)
                live_url = deploy_html(html_output, project_name)

                post_progress(
                    client, channel, thread_ts, "white_check_mark",
                    f"*Advertorial is live!*\n\n"
                    f":link: {live_url}\n\n"
                    f"Format: {format_type} | Project: `{project_name}`"
                )

            except RuntimeError as e:
                # Vercel deployment failed — still post the HTML as text
                post_progress(client, channel, thread_ts, "warning",
                              f"Vercel deployment failed: {e}\nPosting the HTML as text so you still have it.")
                post_long_message(client, channel, thread_ts, f"```{html_output[:3800]}```")
            except Exception as e:
                logger.error(f"Advertorial error: {traceback.format_exc()}")
                post_progress(client, channel, thread_ts, "x",
                              f"Advertorial generation failed: {type(e).__name__}: {e}")

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()

    @app.command("/listicle")
    def handle_listicle(ack, command, respond, client):
        """Generate a listicle-format advertorial and deploy to Vercel."""
        ack()

        brief = command.get("text", "").strip()
        if not brief:
            respond(
                "Usage: `/listicle <brief>`\n\n"
                "Example: `/listicle bekynd 7 reasons women are ditching prescriptions for this scalp scrub`\n\n"
                "If the client has been researched (via `/research`), I'll auto-load their data."
            )
            return

        channel = command["channel_id"]
        user = command["user_id"]
        client_slug = _detect_client(brief)

        initial = client.chat_postMessage(
            channel=channel,
            text=(
                f":pencil2: <@{user}> requested a *listicle* advertorial\n"
                f"{'Using `' + client_slug + '` research' if client_slug else 'No client research found — using general context'}\n"
                "This takes 60-120 seconds."
            ),
        )
        thread_ts = initial["ts"]

        def _run():
            try:
                if client_slug:
                    context = knowledge_base.load_client_research(client_slug)
                else:
                    context = knowledge_base.load_for_creative()

                post_progress(client, channel, thread_ts, "brain", "Generating listicle copy + HTML...")

                system = _build_listicle_system()
                html_output = long_creative_request(system, context, brief, LISTICLE_MAX_TOKENS)
                html_output = _clean_html_output(html_output)

                if not html_output.strip().startswith("<!DOCTYPE") and not html_output.strip().startswith("<html"):
                    post_progress(client, channel, thread_ts, "warning",
                                  "Output wasn't valid HTML. Posting as text instead.")
                    post_long_message(client, channel, thread_ts, html_output)
                    return

                post_progress(client, channel, thread_ts, "rocket", "Deploying to Vercel...")

                topic_hint = _extract_topic_hint(brief)
                project_name = generate_project_name(client_slug or "roly", topic_hint)
                live_url = deploy_html(html_output, project_name)

                post_progress(
                    client, channel, thread_ts, "white_check_mark",
                    f"*Listicle is live!*\n\n"
                    f":link: {live_url}\n\n"
                    f"Project: `{project_name}`"
                )

            except RuntimeError as e:
                post_progress(client, channel, thread_ts, "warning",
                              f"Vercel deployment failed: {e}\nPosting the HTML as text.")
                post_long_message(client, channel, thread_ts, f"```{html_output[:3800]}```")
            except Exception as e:
                logger.error(f"Listicle error: {traceback.format_exc()}")
                post_progress(client, channel, thread_ts, "x",
                              f"Listicle generation failed: {type(e).__name__}: {e}")

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()


def _clean_html_output(html: str) -> str:
    """Strip any preamble text, markdown fences, or other junk Claude adds around the HTML."""
    html = html.strip()

    # Strip markdown code fences
    if html.startswith("```html"):
        html = html[7:]
    elif html.startswith("```"):
        html = html[3:]
    if html.endswith("```"):
        html = html[:-3]
    html = html.strip()

    # Strip any preamble text before <!DOCTYPE or <html
    # Claude sometimes adds "I'll create a listicle..." before the HTML
    import re
    doctype_match = re.search(r'<!DOCTYPE\s+html', html, re.IGNORECASE)
    html_match = re.search(r'<html', html, re.IGNORECASE)

    if doctype_match:
        html = html[doctype_match.start():]
    elif html_match:
        html = html[html_match.start():]

    return html.strip()
