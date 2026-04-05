"""
Vercel deployment engine — deploys self-contained HTML files via the Vercel REST API.
No GitHub needed. Just POST the HTML and get a live URL back.
"""

import hashlib
import logging
import re
import time

import httpx

from config import VERCEL_API_TOKEN

logger = logging.getLogger(__name__)

VERCEL_API_BASE = "https://api.vercel.com"
DEPLOY_TIMEOUT = httpx.Timeout(60.0, connect=15.0)


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {VERCEL_API_TOKEN}",
        "Content-Type": "application/json",
    }


def generate_project_name(brand_slug: str, topic_hint: str = "") -> str:
    """Generate a clean, editorial-style project name for Vercel.

    NOT clickbait. Reads like a legitimate editorial publication.

    Examples:
        bekynd, "scalp care guide" → "bekynd-scalp-care-guide"
        tao, "daily routine" → "tao-daily-routine"
        bekynd, "" → "bekynd-article-a7f3"
    """
    if topic_hint:
        # Clean the topic hint into a slug
        slug_parts = re.sub(r"[^a-z0-9\s-]", "", topic_hint.lower()).split()
        # Take first 4-5 meaningful words
        stop_words = {"the", "a", "an", "for", "and", "or", "of", "to", "in", "on", "is", "are", "with"}
        meaningful = [w for w in slug_parts if w not in stop_words][:5]
        topic_slug = "-".join(meaningful) if meaningful else ""
    else:
        topic_slug = ""

    if topic_slug:
        name = f"{brand_slug}-{topic_slug}"
    else:
        # Fallback: brand + short hash for uniqueness
        ts_hash = hashlib.md5(str(time.time()).encode()).hexdigest()[:4]
        name = f"{brand_slug}-article-{ts_hash}"

    # Sanitize: lowercase, alphanumeric + hyphens, max 63 chars
    name = re.sub(r"[^a-z0-9-]", "", name.lower())
    name = re.sub(r"-+", "-", name).strip("-")
    return name[:63]


def deploy_html(html_content: str, project_name: str) -> str:
    """Deploy a self-contained HTML file to Vercel.

    Args:
        html_content: Complete HTML string (all CSS inline, no external deps)
        project_name: Clean project name (becomes the subdomain)

    Returns:
        The production URL (e.g., "https://bekynd-scalp-care-guide.vercel.app")

    Raises:
        RuntimeError: If deployment fails
    """
    if not VERCEL_API_TOKEN:
        raise RuntimeError(
            "VERCEL_API_TOKEN not configured. Add it to your .env file to enable auto-deployment."
        )

    # Vercel Files API: POST /v13/deployments
    payload = {
        "name": project_name,
        "files": [
            {
                "file": "index.html",
                "data": html_content,
            }
        ],
        "projectSettings": {
            "framework": None,  # Static site, no framework
        },
        "target": "production",
    }

    logger.info(f"Deploying to Vercel as '{project_name}'...")

    try:
        resp = httpx.post(
            f"{VERCEL_API_BASE}/v13/deployments",
            headers=_headers(),
            json=payload,
            timeout=DEPLOY_TIMEOUT,
        )

        if resp.status_code == 402:
            raise RuntimeError("Vercel plan limit reached. Check your Vercel account.")

        if resp.status_code not in (200, 201):
            error_body = resp.text[:500]
            raise RuntimeError(f"Vercel deployment failed ({resp.status_code}): {error_body}")

        data = resp.json()

        # The 'url' field is the build URL with a hash — NOT the clean production URL.
        # The 'alias' array contains the clean URLs. First one is typically {name}.vercel.app
        aliases = data.get("alias", [])

        # Find the cleanest alias (shortest one, which is {name}.vercel.app)
        if aliases:
            # Sort by length — shortest is the clean one
            clean_alias = sorted(aliases, key=len)[0]
            production_url = f"https://{clean_alias}"
        else:
            # Fallback to constructing it ourselves
            production_url = f"https://{project_name}.vercel.app"

        logger.info(f"Deployed successfully: {production_url}")
        return production_url

    except httpx.TimeoutException:
        raise RuntimeError("Vercel deployment timed out. Try again.")
    except httpx.HTTPError as e:
        raise RuntimeError(f"HTTP error during deployment: {e}")
