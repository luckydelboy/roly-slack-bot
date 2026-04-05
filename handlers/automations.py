"""
Event-based automations — keyword reactions, welcome messages, etc.
"""

import logging
import re

from slack_bolt import App

from config import BOT_NAME

logger = logging.getLogger(__name__)

# ── Keyword → emoji reaction map ────────────────────────
KEYWORD_REACTIONS = {
    r"\b(idea|suggestion|proposal)\b": "bulb",
    r"\b(urgent|critical|emergency|asap)\b": "rotating_light",
    r"\b(ship(ped)?|launch(ed)?|deploy(ed)?|released?)\b": "rocket",
    r"\b(thank(s| you)|appreciate)\b": "heart",
    r"\b(bug|broken|issue|error)\b": "bug",
    r"\b(lgtm|looks good)\b": "white_check_mark",
}


def register(app: App):
    """Register all automation listeners."""

    # ── Welcome new channel members ─────────────────────
    @app.event("member_joined_channel")
    def handle_member_join(event, say, client):
        """Send a friendly welcome when someone joins a channel."""
        user = event["user"]
        channel = event["channel"]

        # Look up the user's display name
        try:
            info = client.users_info(user=user)
            name = info["user"]["profile"].get("display_name") or info["user"]["real_name"]
        except Exception:
            name = "there"

        say(
            text=(
                f"Welcome to the channel, *{name}*! :wave:\n"
                f"I'm {BOT_NAME} — mention me anytime if you have a question, "
                f"or type `/help-claude` to see what I can do."
            ),
            channel=channel,
        )
        logger.info(f"Welcomed {user} to {channel}")

    # ── Keyword-triggered reactions ─────────────────────
    @app.event(
        event="message",
        matchers=[
            lambda event: (
                event.get("channel_type") != "im"
                and not event.get("bot_id")
                and not event.get("subtype")
            )
        ],
    )
    def handle_keyword_reactions(event, client):
        """Add emoji reactions when messages match keyword patterns."""
        text = (event.get("text") or "").lower()
        channel = event["channel"]
        ts = event["ts"]

        for pattern, emoji in KEYWORD_REACTIONS.items():
            if re.search(pattern, text, re.IGNORECASE):
                try:
                    client.reactions_add(channel=channel, name=emoji, timestamp=ts)
                    logger.info(f"Reacted :{emoji}: in {channel}")
                except Exception:
                    pass  # Already reacted or missing permission

    # ── Emoji-triggered actions ─────────────────────────
    @app.event("reaction_added")
    def handle_reaction_added(event, client):
        """
        When someone adds a :clipboard: reaction to a message,
        the bot reposts it to the thread as a formatted quote.
        Useful for "save this" workflows.
        """
        if event.get("reaction") != "clipboard":
            return

        channel = event["item"]["channel"]
        ts = event["item"]["ts"]

        try:
            result = client.conversations_history(
                channel=channel,
                latest=ts,
                inclusive=True,
                limit=1,
            )
            if result["messages"]:
                original = result["messages"][0]
                client.chat_postMessage(
                    channel=channel,
                    thread_ts=ts,
                    text=f":clipboard: *Saved note:*\n> {original['text']}",
                )
        except Exception as e:
            logger.error(f"Clipboard automation failed: {e}")
