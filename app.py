"""
Claude Slack Bot — main entry point.

Starts the bot in Socket Mode (no public URL needed).
Initializes the knowledge base and project manager on startup.
"""

import logging

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from config import SLACK_BOT_TOKEN, SLACK_APP_TOKEN, BOT_NAME
import knowledge_base
import project_manager
from handlers import conversations, commands, automations, creative, projects, research, advertorial

# ── Logging ──────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(name)-28s  %(levelname)-5s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── Initialize data stores ───────────────────────────────
knowledge_base.init()
project_manager.init()

# ── Create the Bolt app ─────────────────────────────────
app = App(token=SLACK_BOT_TOKEN)

# ── Register all handler modules ─────────────────────────
conversations.register(app)
commands.register(app)
automations.register(app)
creative.register(app)
projects.register(app)
research.register(app)
advertorial.register(app)

# ── Start ────────────────────────────────────────────────
if __name__ == "__main__":
    kb_files = knowledge_base.list_files()
    total = sum(len(v) for v in kb_files.values())
    logger.info(f"Knowledge base: {total} files loaded")
    logger.info(f"Starting {BOT_NAME}...")
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()
