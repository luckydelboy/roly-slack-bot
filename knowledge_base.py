"""
Knowledge Base — loads brand docs, customer research, past ads, and frameworks
from the knowledge/ directory and makes them available as context for Claude.

Directory structure:
    knowledge/
        brand/          ← brand guidelines, tone of voice, product info
        customers/      ← avatars, personas, pain points, review mining
        ads/            ← winning ad scripts, landers, VSLs
        frameworks/     ← creative frameworks (auto-populated on first run)
"""

import os
import glob
import logging

logger = logging.getLogger(__name__)

KNOWLEDGE_DIR = os.path.join(os.path.dirname(__file__), "knowledge")

# Subdirectories and their descriptions (used in context headers)
SECTIONS = {
    "clients": "Client Summaries (Condensed)",
    "brand": "Brand & Product Information",
    "customers": "Customer Research & Avatars",
    "ads": "Winning Ads & Creative Examples",
    "frameworks": "Creative Frameworks & Methodology",
}


def init():
    """Create the knowledge directory structure if it doesn't exist."""
    for section in SECTIONS:
        path = os.path.join(KNOWLEDGE_DIR, section)
        os.makedirs(path, exist_ok=True)

    # Create placeholder files so the user knows what to put where
    _write_placeholder(
        "brand/README.txt",
        "Put your brand documents here.\n\n"
        "Examples:\n"
        "  - brand-guidelines.txt\n"
        "  - product-catalog.txt\n"
        "  - tone-of-voice.txt\n"
        "  - pricing.txt\n"
        "  - USPs.txt\n\n"
        "Supported formats: .txt, .md\n"
        "The bot reads ALL files in this folder and uses them as context.\n",
    )
    _write_placeholder(
        "customers/README.txt",
        "Put your customer research here.\n\n"
        "Examples:\n"
        "  - avatar-women-35-55.txt\n"
        "  - pain-points.txt\n"
        "  - review-mining-output.txt\n"
        "  - objections.txt\n"
        "  - testimonials.txt\n\n"
        "Supported formats: .txt, .md\n",
    )
    _write_placeholder(
        "ads/README.txt",
        "Put your winning ad scripts and creative examples here.\n\n"
        "Examples:\n"
        "  - facebook-winner-q4.txt\n"
        "  - tiktok-top-performers.txt\n"
        "  - landing-page-v2.txt\n"
        "  - vsl-script-main.txt\n\n"
        "Supported formats: .txt, .md\n",
    )
    logger.info(f"Knowledge base initialized at {KNOWLEDGE_DIR}")


def _write_placeholder(rel_path: str, content: str):
    """Write a placeholder file if it doesn't already exist."""
    full = os.path.join(KNOWLEDGE_DIR, rel_path)
    if not os.path.exists(full):
        with open(full, "w") as f:
            f.write(content)


def load_section(section: str) -> str:
    """Load all .txt and .md files from a knowledge section into a single string."""
    path = os.path.join(KNOWLEDGE_DIR, section)
    if not os.path.isdir(path):
        return ""

    parts = []
    for ext in ("**/*.txt", "**/*.md"):
        for filepath in sorted(glob.glob(os.path.join(path, ext), recursive=True)):
            name = os.path.basename(filepath)
            if name == "README.txt":
                continue
            try:
                with open(filepath, "r") as f:
                    content = f.read().strip()
                if content:
                    parts.append(f"### {name}\n{content}")
            except Exception as e:
                logger.warning(f"Could not read {filepath}: {e}")

    return "\n\n".join(parts)


def load_all() -> str:
    """Load the entire knowledge base as a formatted context block."""
    blocks = []
    for section, title in SECTIONS.items():
        content = load_section(section)
        if content:
            blocks.append(f"## {title}\n\n{content}")

    if not blocks:
        return ""

    return (
        "=== KNOWLEDGE BASE ===\n"
        "Use the following information as context. Reference it when relevant.\n\n"
        + "\n\n---\n\n".join(blocks)
        + "\n\n=== END KNOWLEDGE BASE ==="
    )


def load_for_creative() -> str:
    """Load condensed client summaries + ads for creative writing.
    Uses the small summary files, NOT the huge raw research docs."""
    blocks = []

    # Primary source: condensed client summaries (~16k chars)
    clients = load_section("clients")
    if clients:
        blocks.append(f"## Client Context\n\n{clients}")

    # Also load ads for reference scripts (~5k chars)
    ads = load_section("ads")
    if ads:
        blocks.append(f"## Past Winning Ads\n\n{ads}")

    if not blocks:
        return (
            "No knowledge base found. The user hasn't added brand/customer docs yet. "
            "Ask them about the product, audience, and goals before writing."
        )

    return (
        "=== CLIENT CONTEXT ===\n"
        + "\n\n---\n\n".join(blocks)
        + "\n\n=== END CLIENT CONTEXT ==="
    )


def save_research_file(section: str, client_slug: str, filename: str, content: str):
    """Save a research output file for a specific client.
    Creates the directory structure if needed. Uses write-to-temp-then-rename
    for atomic writes."""
    dir_path = os.path.join(KNOWLEDGE_DIR, section, client_slug)
    os.makedirs(dir_path, exist_ok=True)
    final_path = os.path.join(dir_path, filename)
    tmp_path = final_path + ".tmp"
    with open(tmp_path, "w") as f:
        f.write(content)
    os.replace(tmp_path, final_path)
    logger.info(f"Saved research file: {section}/{client_slug}/{filename}")


def save_client_summary(client_slug: str, content: str):
    """Save the condensed client summary to clients/ (top-level, not in a subfolder)."""
    dir_path = os.path.join(KNOWLEDGE_DIR, "clients")
    os.makedirs(dir_path, exist_ok=True)
    filename = f"{client_slug}-summary.md"
    final_path = os.path.join(dir_path, filename)
    tmp_path = final_path + ".tmp"
    with open(tmp_path, "w") as f:
        f.write(content)
    os.replace(tmp_path, final_path)
    logger.info(f"Saved client summary: clients/{filename}")


def load_client_research(client_slug: str) -> str:
    """Load ALL research for a specific client across brand/, customers/, and clients/.
    Used by advertorial/listicle commands for maximum context."""
    blocks = []

    # Client summary
    summary_path = os.path.join(KNOWLEDGE_DIR, "clients", f"{client_slug}-summary.md")
    if os.path.isfile(summary_path):
        with open(summary_path, "r") as f:
            content = f.read().strip()
        if content:
            blocks.append(f"## Client Summary\n\n{content}")

    # Brand research
    brand_dir = os.path.join(KNOWLEDGE_DIR, "brand", client_slug)
    if os.path.isdir(brand_dir):
        brand_content = _load_dir(brand_dir)
        if brand_content:
            blocks.append(f"## Brand & Product Research\n\n{brand_content}")

    # Customer research
    cust_dir = os.path.join(KNOWLEDGE_DIR, "customers", client_slug)
    if os.path.isdir(cust_dir):
        cust_content = _load_dir(cust_dir)
        if cust_content:
            blocks.append(f"## Customer Research & Avatars\n\n{cust_content}")

    if not blocks:
        return ""

    return (
        f"=== RESEARCH CONTEXT: {client_slug.upper()} ===\n\n"
        + "\n\n---\n\n".join(blocks)
        + f"\n\n=== END RESEARCH CONTEXT ==="
    )


def _load_dir(dir_path: str) -> str:
    """Load all .txt and .md files from a directory recursively."""
    parts = []
    for ext in ("**/*.txt", "**/*.md"):
        for filepath in sorted(glob.glob(os.path.join(dir_path, ext), recursive=True)):
            name = os.path.basename(filepath)
            if name == "README.txt":
                continue
            try:
                with open(filepath, "r") as f:
                    content = f.read().strip()
                if content:
                    parts.append(f"### {name}\n{content}")
            except Exception as e:
                logger.warning(f"Could not read {filepath}: {e}")
    return "\n\n".join(parts)


def client_exists(client_slug: str) -> bool:
    """Check if any research files exist for this client."""
    for section in ("brand", "customers", "clients"):
        if section == "clients":
            if os.path.isfile(os.path.join(KNOWLEDGE_DIR, "clients", f"{client_slug}-summary.md")):
                return True
        else:
            dir_path = os.path.join(KNOWLEDGE_DIR, section, client_slug)
            if os.path.isdir(dir_path) and any(
                glob.glob(os.path.join(dir_path, "**/*.md"), recursive=True)
            ):
                return True
    return False


def list_clients() -> list[str]:
    """Return slugs of all clients that have research files."""
    clients = set()
    # Check clients/ for summary files
    clients_dir = os.path.join(KNOWLEDGE_DIR, "clients")
    if os.path.isdir(clients_dir):
        for f in os.listdir(clients_dir):
            if f.endswith("-summary.md"):
                clients.add(f.replace("-summary.md", ""))
    # Check brand/ subdirectories
    brand_dir = os.path.join(KNOWLEDGE_DIR, "brand")
    if os.path.isdir(brand_dir):
        for d in os.listdir(brand_dir):
            if os.path.isdir(os.path.join(brand_dir, d)):
                clients.add(d)
    # Check customers/ subdirectories
    cust_dir = os.path.join(KNOWLEDGE_DIR, "customers")
    if os.path.isdir(cust_dir):
        for d in os.listdir(cust_dir):
            if os.path.isdir(os.path.join(cust_dir, d)):
                clients.add(d)
    return sorted(clients)


def list_files() -> dict[str, list[str]]:
    """Return a dict of section → list of filenames (for /kb-status command)."""
    result = {}
    for section in SECTIONS:
        path = os.path.join(KNOWLEDGE_DIR, section)
        if os.path.isdir(path):
            files = []
            for ext in ("**/*.txt", "**/*.md"):
                for fp in glob.glob(os.path.join(path, ext), recursive=True):
                    name = os.path.relpath(fp, path)
                    if name != "README.txt":
                        files.append(name)
            result[section] = sorted(files)
        else:
            result[section] = []
    return result
