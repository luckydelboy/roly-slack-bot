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

    Reads like a legitimate editorial publication URL.
    Uses health/wellness journal naming conventions, not brand-first URLs.

    Examples:
        bekynd, scalp psoriasis → "scalp-health-journal"
        bekynd, dating confidence → "womens-confidence-review"
        tao, oral care → "dental-wellness-daily"
    """
    # Editorial publication naming pools — pick based on topic keywords
    niche_publications = {
        # Scalp/hair niche
        "scalp": ["scalp-health-journal", "scalp-care-daily", "the-scalp-review", "dermatology-today"],
        "psoriasis": ["skin-health-journal", "dermatology-today", "chronic-skin-review"],
        "eczema": ["skin-health-journal", "dermatology-today", "the-skin-barrier"],
        "hair": ["hair-health-daily", "the-hair-journal", "strand-science-review"],
        "dandruff": ["scalp-health-journal", "scalp-care-daily"],
        # Beauty / skincare
        "skin": ["the-skin-journal", "clear-skin-daily", "the-beauty-review"],
        "beauty": ["the-beauty-journal", "beauty-insider-review"],
        "anti-aging": ["age-defiance-journal", "the-longevity-review"],
        # Dental
        "dental": ["dental-wellness-daily", "the-smile-journal", "oral-health-today"],
        "teeth": ["dental-wellness-daily", "the-smile-journal"],
        "oral": ["dental-wellness-daily", "oral-health-today"],
        # Pet
        "dog": ["the-canine-wellness-journal", "pet-health-daily", "the-dog-owner-guide"],
        "cat": ["the-feline-wellness-journal", "pet-health-daily"],
        "pet": ["pet-health-daily", "the-pet-wellness-journal"],
        # General health
        "joint": ["joint-health-today", "mobility-matters-journal"],
        "sleep": ["sleep-science-daily", "the-rest-journal"],
        "weight": ["wellness-weekly-review", "metabolic-health-daily"],
        "stress": ["calm-living-journal", "wellness-weekly-review"],
        "supplement": ["wellness-insider-daily", "the-supplement-review"],
        # Fallback general
        "_default": ["wellness-weekly-review", "health-insider-daily", "the-wellness-journal"],
    }

    # Pick the publication name based on topic keywords
    topic_lower = topic_hint.lower() if topic_hint else ""
    selected_pub = None

    for keyword, pubs in niche_publications.items():
        if keyword == "_default":
            continue
        if keyword in topic_lower:
            # Use deterministic selection based on topic hash for consistency
            h = int(hashlib.md5(topic_hint.encode()).hexdigest(), 16)
            selected_pub = pubs[h % len(pubs)]
            break

    if not selected_pub:
        # Default fallback
        h = int(hashlib.md5((topic_hint or brand_slug).encode()).hexdigest(), 16)
        selected_pub = niche_publications["_default"][h % len(niche_publications["_default"])]

    # Add short unique suffix so multiple advertorials don't collide
    ts_hash = hashlib.md5(str(time.time()).encode()).hexdigest()[:4]
    name = f"{selected_pub}-{ts_hash}"

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
