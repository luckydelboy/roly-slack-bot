"""
Project Manager — handles tasks and campaign workflows.

Data is stored as JSON files in the data/ directory so it persists across restarts.

    data/
        tasks.json      ← simple task list
        campaigns.json  ← campaign pipeline tracker
"""

import json
import os
import logging
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
TASKS_FILE = os.path.join(DATA_DIR, "tasks.json")
CAMPAIGNS_FILE = os.path.join(DATA_DIR, "campaigns.json")


def init():
    """Create data directory and files if they don't exist."""
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(TASKS_FILE):
        _save(TASKS_FILE, [])
    if not os.path.exists(CAMPAIGNS_FILE):
        _save(CAMPAIGNS_FILE, [])


def _load(path: str) -> list:
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def _save(path: str, data: list):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ─── TASKS ───────────────────────────────────────────────

def add_task(title: str, owner: Optional[str] = None, due: Optional[str] = None) -> dict:
    """Add a new task. Returns the created task."""
    tasks = _load(TASKS_FILE)
    task = {
        "id": len(tasks) + 1,
        "title": title,
        "owner": owner,
        "due": due,
        "status": "todo",
        "created": _now(),
        "completed_at": None,
    }
    tasks.append(task)
    _save(TASKS_FILE, tasks)
    return task


def complete_task(task_id: int) -> Optional[dict]:
    """Mark a task as done. Returns the task, or None if not found."""
    tasks = _load(TASKS_FILE)
    for t in tasks:
        if t["id"] == task_id:
            t["status"] = "done"
            t["completed_at"] = _now()
            _save(TASKS_FILE, tasks)
            return t
    return None


def list_tasks(status: Optional[str] = None) -> list[dict]:
    """List tasks, optionally filtered by status."""
    tasks = _load(TASKS_FILE)
    if status:
        return [t for t in tasks if t["status"] == status]
    return tasks


def assign_task(task_id: int, owner: str) -> Optional[dict]:
    """Assign a task to someone."""
    tasks = _load(TASKS_FILE)
    for t in tasks:
        if t["id"] == task_id:
            t["owner"] = owner
            _save(TASKS_FILE, tasks)
            return t
    return None


# ─── CAMPAIGNS ───────────────────────────────────────────

CAMPAIGN_STAGES = ["brief", "research", "copy", "review", "revision", "approved", "live"]

STAGE_EMOJI = {
    "brief": ":memo:",
    "research": ":mag:",
    "copy": ":pencil2:",
    "review": ":eyes:",
    "revision": ":arrows_counterclockwise:",
    "approved": ":white_check_mark:",
    "live": ":rocket:",
}


def create_campaign(name: str, owner: Optional[str] = None, campaign_type: str = "ad") -> dict:
    """Create a new campaign. Type can be: ad, lander, vsl, email, full-funnel."""
    campaigns = _load(CAMPAIGNS_FILE)
    campaign = {
        "id": len(campaigns) + 1,
        "name": name,
        "type": campaign_type,
        "owner": owner,
        "stage": "brief",
        "created": _now(),
        "updated": _now(),
        "notes": [],
    }
    campaigns.append(campaign)
    _save(CAMPAIGNS_FILE, campaigns)
    return campaign


def advance_campaign(campaign_id: int, note: Optional[str] = None) -> Optional[dict]:
    """Move a campaign to the next stage."""
    campaigns = _load(CAMPAIGNS_FILE)
    for c in campaigns:
        if c["id"] == campaign_id:
            current_idx = CAMPAIGN_STAGES.index(c["stage"])
            if current_idx < len(CAMPAIGN_STAGES) - 1:
                c["stage"] = CAMPAIGN_STAGES[current_idx + 1]
                c["updated"] = _now()
                if note:
                    c["notes"].append({"stage": c["stage"], "note": note, "time": _now()})
                _save(CAMPAIGNS_FILE, campaigns)
            return c
    return None


def set_campaign_stage(campaign_id: int, stage: str, note: Optional[str] = None) -> Optional[dict]:
    """Set a campaign to a specific stage."""
    if stage not in CAMPAIGN_STAGES:
        return None
    campaigns = _load(CAMPAIGNS_FILE)
    for c in campaigns:
        if c["id"] == campaign_id:
            c["stage"] = stage
            c["updated"] = _now()
            if note:
                c["notes"].append({"stage": stage, "note": note, "time": _now()})
            _save(CAMPAIGNS_FILE, campaigns)
            return c
    return None


def list_campaigns(stage: Optional[str] = None) -> list[dict]:
    """List campaigns, optionally filtered by stage."""
    campaigns = _load(CAMPAIGNS_FILE)
    if stage:
        return [c for c in campaigns if c["stage"] == stage]
    return campaigns


def format_campaign(c: dict) -> str:
    """Format a single campaign for Slack display."""
    emoji = STAGE_EMOJI.get(c["stage"], ":grey_question:")
    owner = f" — <@{c['owner']}>" if c.get("owner") else ""
    return f"{emoji} *#{c['id']} {c['name']}* [{c['type']}] → `{c['stage']}`{owner}"


def format_pipeline() -> str:
    """Format the full campaign pipeline as a Slack message."""
    campaigns = _load(CAMPAIGNS_FILE)
    if not campaigns:
        return "_No campaigns yet. Create one with `/campaign new <name>`_"

    active = [c for c in campaigns if c["stage"] != "live"]
    live = [c for c in campaigns if c["stage"] == "live"]

    lines = ["*Campaign Pipeline*\n"]

    if active:
        lines.append("*Active:*")
        for c in active:
            lines.append(f"  {format_campaign(c)}")
        lines.append("")

    if live:
        lines.append("*Live:*")
        for c in live:
            lines.append(f"  {format_campaign(c)}")

    # Stage summary
    lines.append("\n*Stage Summary:*")
    for stage in CAMPAIGN_STAGES:
        count = len([c for c in campaigns if c["stage"] == stage])
        if count:
            emoji = STAGE_EMOJI[stage]
            lines.append(f"  {emoji} `{stage}`: {count}")

    return "\n".join(lines)
