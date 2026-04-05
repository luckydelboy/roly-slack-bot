"""
Slash command handlers — /ask, /summary, /help
"""

import logging

from slack_bolt import App

from claude_client import one_shot, summarize_messages
from config import BOT_NAME

logger = logging.getLogger(__name__)


def register(app: App):
    """Register all slash command listeners."""

    # ── /ask <question> ─────────────────────────────────
    @app.command("/ask")
    def handle_ask(ack, command, respond):
        """Ask Claude a one-off question. Response is only visible to you."""
        ack()
        question = command.get("text", "").strip()

        if not question:
            respond("Usage: `/ask <your question>`")
            return

        logger.info(f"/ask from {command['user_name']}: {question[:80]}...")
        answer = one_shot(question)
        respond(
            response_type="ephemeral",  # only visible to the user
            text=answer,
        )

    # ── /summary ────────────────────────────────────────
    @app.command("/summary")
    def handle_summary(ack, command, respond, client):
        """Summarize the last N messages in the current channel."""
        ack()
        channel = command["channel_id"]
        count_str = command.get("text", "").strip()
        count = int(count_str) if count_str.isdigit() else 20

        # Fetch recent messages from the channel
        try:
            result = client.conversations_history(
                channel=channel,
                limit=min(count, 100),
            )
            messages = [
                m["text"]
                for m in result["messages"]
                if m.get("text") and not m.get("bot_id")
            ]
        except Exception as e:
            respond(f"I couldn't read the channel history: {e}")
            return

        if not messages:
            respond("No messages found to summarize.")
            return

        logger.info(f"/summary in {channel}: summarizing {len(messages)} messages")
        summary = summarize_messages(messages)
        respond(
            response_type="ephemeral",
            text=f"*Summary of last {len(messages)} messages:*\n\n{summary}",
        )

    # ── /help ───────────────────────────────────────────
    @app.command("/help-claude")
    def handle_help(ack, respond):
        """Show what the bot can do."""
        ack()
        respond(
            response_type="ephemeral",
            text=(
                f"*{BOT_NAME} — What I Can Do*\n\n"
                "*Chat with me:*\n"
                f"• Mention me (`@{BOT_NAME}`) in any channel\n"
                "• Send me a direct message\n"
                "• I remember context within a thread\n\n"
                "*General:*\n"
                "• `/ask <question>` — Ask me anything (private reply)\n"
                "• `/summary [N]` — Summarize the last N messages\n"
                "• `/help-claude` — Show this help message\n\n"
                "*Research & Long-Form:*\n"
                "• `/research <url>` — Auto-research a brand (scrape site, mine reviews, build personas)\n"
                "• `/advertorial <brief>` — Generate advertorial HTML + deploy to Vercel\n"
                "• `/listicle <brief>` — Generate listicle HTML + deploy to Vercel\n\n"
                "*Creative Tools:*\n"
                "• `/ad <brief>` — Write a UGC ad script (A.D.A.P.T. framework)\n"
                "• `/lander <brief>` — Write landing page copy\n"
                "• `/vsl <brief>` — Write a VSL script\n"
                "• `/hooks <brief>` — Generate 10 scroll-stopping hooks\n"
                "• `/kb-status` — Check what's loaded in the knowledge base\n\n"
                "*Project Management:*\n"
                "• `/task add <title> [@owner] [due:date]` — Create a task\n"
                "• `/task done <id>` — Complete a task\n"
                "• `/task list` — View all tasks\n"
                "• `/campaign new <name>` — Start a new campaign\n"
                "• `/campaign advance <id>` — Move campaign to next stage\n"
                "• `/campaign pipeline` — View all campaigns\n\n"
                "*Automations:*\n"
                "• Greets new channel members\n"
                "• Reacts to keywords (:bulb: ideas, :rocket: launches, :rotating_light: urgent)\n"
                "• :clipboard: reaction saves a message as a quote in the thread\n"
            ),
        )
