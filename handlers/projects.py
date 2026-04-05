"""
Project management handlers — tasks and campaign workflows.

Slash commands:
    /task     — Manage tasks (add, done, list, assign)
    /campaign — Manage campaigns (new, advance, stage, list, pipeline)
"""

import logging
import re

from slack_bolt import App

import project_manager as pm

logger = logging.getLogger(__name__)


def register(app: App):
    """Register all project management slash commands."""

    # ── /task ────────────────────────────────────────────
    @app.command("/task")
    def handle_task(ack, command, respond):
        """
        Manage tasks.
            /task add Fix the hero section copy @jane due:friday
            /task done 3
            /task list
            /task list done
            /task assign 3 @jane
        """
        ack()
        text = command.get("text", "").strip()
        parts = text.split(maxsplit=1)
        action = parts[0].lower() if parts else "list"
        rest = parts[1] if len(parts) > 1 else ""

        if action == "add":
            # Parse owner (@ mention) and due date
            owner_match = re.search(r"<@([A-Z0-9]+)(?:\|[^>]*)?>", rest)
            owner = owner_match.group(1) if owner_match else None
            due_match = re.search(r"due:(\S+)", rest)
            due = due_match.group(1) if due_match else None

            # Clean title
            title = rest
            if owner_match:
                title = title.replace(owner_match.group(0), "")
            if due_match:
                title = title.replace(due_match.group(0), "")
            title = title.strip()

            if not title:
                respond("Usage: `/task add <title> [@owner] [due:date]`")
                return

            task = pm.add_task(title, owner=owner, due=due)
            owner_str = f" → <@{owner}>" if owner else ""
            due_str = f" (due: {due})" if due else ""
            respond(f":white_check_mark: Task *#{task['id']}* created: {title}{owner_str}{due_str}")

        elif action == "done":
            try:
                task_id = int(rest.strip())
            except ValueError:
                respond("Usage: `/task done <task_id>`")
                return

            task = pm.complete_task(task_id)
            if task:
                respond(f":tada: Task *#{task_id}* marked done: _{task['title']}_")
            else:
                respond(f"Task #{task_id} not found.")

        elif action == "assign":
            assign_parts = rest.split()
            if len(assign_parts) < 2:
                respond("Usage: `/task assign <task_id> @person`")
                return
            try:
                task_id = int(assign_parts[0])
            except ValueError:
                respond("Usage: `/task assign <task_id> @person`")
                return

            owner_match = re.search(r"<@([A-Z0-9]+)(?:\|[^>]*)?>", rest)
            if not owner_match:
                respond("Please mention a user: `/task assign 3 @jane`")
                return

            task = pm.assign_task(task_id, owner_match.group(1))
            if task:
                respond(f"Task *#{task_id}* assigned to <@{owner_match.group(1)}>")
            else:
                respond(f"Task #{task_id} not found.")

        elif action == "list":
            status_filter = rest.strip().lower() if rest.strip() else None
            tasks = pm.list_tasks(status=status_filter)

            if not tasks:
                respond("_No tasks found._")
                return

            lines = ["*Tasks*\n"]
            for t in tasks:
                icon = ":white_check_mark:" if t["status"] == "done" else ":black_square_button:"
                owner = f" → <@{t['owner']}>" if t.get("owner") else ""
                due = f" (due: {t['due']})" if t.get("due") else ""
                lines.append(f"{icon} *#{t['id']}* {t['title']}{owner}{due}")

            respond(text="\n".join(lines))

        else:
            respond(
                "*Task commands:*\n"
                "• `/task add <title> [@owner] [due:date]` — Create a task\n"
                "• `/task done <id>` — Complete a task\n"
                "• `/task assign <id> @person` — Assign a task\n"
                "• `/task list [todo|done]` — List tasks"
            )

    # ── /campaign ────────────────────────────────────────
    @app.command("/campaign")
    def handle_campaign(ack, command, respond):
        """
        Manage campaign workflows.
            /campaign new Holiday Sale Facebook Ads @harry
            /campaign advance 1
            /campaign stage 1 review
            /campaign list
            /campaign pipeline
        """
        ack()
        text = command.get("text", "").strip()
        parts = text.split(maxsplit=1)
        action = parts[0].lower() if parts else "pipeline"
        rest = parts[1] if len(parts) > 1 else ""

        if action == "new":
            # Parse owner and campaign type
            owner_match = re.search(r"<@([A-Z0-9]+)(?:\|[^>]*)?>", rest)
            owner = owner_match.group(1) if owner_match else None
            type_match = re.search(r"type:(\S+)", rest)
            campaign_type = type_match.group(1) if type_match else "ad"

            name = rest
            if owner_match:
                name = name.replace(owner_match.group(0), "")
            if type_match:
                name = name.replace(type_match.group(0), "")
            name = name.strip()

            if not name:
                respond(
                    "Usage: `/campaign new <name> [@owner] [type:ad|lander|vsl|email|full-funnel]`"
                )
                return

            c = pm.create_campaign(name, owner=owner, campaign_type=campaign_type)
            respond(
                f":memo: Campaign *#{c['id']}* created: *{name}* [{campaign_type}]\n"
                f"Stage: `brief` → Next: use `/campaign advance {c['id']}` to move it forward"
            )

        elif action == "advance":
            parts2 = rest.split(maxsplit=1)
            try:
                cid = int(parts2[0])
            except (ValueError, IndexError):
                respond("Usage: `/campaign advance <id> [note]`")
                return

            note = parts2[1] if len(parts2) > 1 else None
            c = pm.advance_campaign(cid, note=note)
            if c:
                emoji = pm.STAGE_EMOJI.get(c["stage"], "")
                respond(f"{emoji} Campaign *#{cid}* → `{c['stage']}`")
            else:
                respond(f"Campaign #{cid} not found.")

        elif action == "stage":
            parts2 = rest.split(maxsplit=2)
            if len(parts2) < 2:
                stages = " | ".join(pm.CAMPAIGN_STAGES)
                respond(f"Usage: `/campaign stage <id> <stage>`\nStages: `{stages}`")
                return

            try:
                cid = int(parts2[0])
            except ValueError:
                respond("Usage: `/campaign stage <id> <stage>`")
                return

            stage = parts2[1].lower()
            note = parts2[2] if len(parts2) > 2 else None
            c = pm.set_campaign_stage(cid, stage, note=note)
            if c:
                emoji = pm.STAGE_EMOJI.get(stage, "")
                respond(f"{emoji} Campaign *#{cid}* set to `{stage}`")
            elif stage not in pm.CAMPAIGN_STAGES:
                stages = " | ".join(pm.CAMPAIGN_STAGES)
                respond(f"Invalid stage. Options: `{stages}`")
            else:
                respond(f"Campaign #{cid} not found.")

        elif action in ("list", "pipeline"):
            respond(text=pm.format_pipeline())

        else:
            stages = " → ".join(
                f"{pm.STAGE_EMOJI[s]} `{s}`" for s in pm.CAMPAIGN_STAGES
            )
            respond(
                "*Campaign commands:*\n"
                f"• `/campaign new <name> [@owner] [type:ad|lander|vsl|email|full-funnel]`\n"
                f"• `/campaign advance <id> [note]` — Move to next stage\n"
                f"• `/campaign stage <id> <stage>` — Jump to a specific stage\n"
                f"• `/campaign pipeline` — View all campaigns\n\n"
                f"*Stages:* {stages}"
            )
