"""
Research handler — /research <url> slash command.
Runs the full brand research pipeline in a background thread.
"""

import logging
import threading
import traceback

from slack_bolt import App

from research.pipeline import run_research
from utils.slack_helpers import post_progress

logger = logging.getLogger(__name__)


def register(app: App):
    """Register the /research slash command."""

    @app.command("/research")
    def handle_research(ack, command, respond, client):
        """Run full brand research from a URL."""
        ack()

        url = command.get("text", "").strip()
        if not url:
            respond(
                "Usage: `/research <brand-url>`\n\n"
                "Example: `/research https://bekynd.com`\n\n"
                "I'll scrape the site, mine reviews, build personas, "
                "and save everything to the knowledge base."
            )
            return

        # Ensure URL has a scheme
        if not url.startswith("http"):
            url = f"https://{url}"

        channel = command["channel_id"]
        user = command["user_id"]

        # Post initial message and capture its timestamp for threading
        initial = client.chat_postMessage(
            channel=channel,
            text=(
                f":mag: <@{user}> kicked off research on `{url}`\n"
                "This will take 2-5 minutes. I'll post updates as I go."
            ),
        )
        thread_ts = initial["ts"]

        def _run():
            """Background thread that runs the research pipeline."""
            try:
                def progress_callback(emoji, message):
                    post_progress(client, channel, thread_ts, emoji, message)

                run_research(url, progress=progress_callback)

            except ValueError as e:
                post_progress(client, channel, thread_ts, "x", f"Research failed: {e}")
            except Exception as e:
                logger.error(f"Research pipeline error: {traceback.format_exc()}")
                post_progress(
                    client, channel, thread_ts, "x",
                    f"Research failed with an unexpected error: {type(e).__name__}: {e}"
                )

        # Run in background thread so we don't block the handler
        thread = threading.Thread(target=_run, daemon=True)
        thread.start()
