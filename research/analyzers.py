"""
Research analyzers — Claude-powered analysis functions for each research stage.
Each function takes raw data, sends it to Claude with a focused prompt, returns markdown.
"""

import logging
from claude_client import research_analysis
from research.prompts import (
    BRAND_ANALYSIS_PROMPT,
    REVIEW_MINING_PROMPT,
    PERSONA_BUILDING_PROMPT,
    MARKET_SYNTHESIS_PROMPT,
    CONDENSED_SUMMARY_PROMPT,
)

logger = logging.getLogger(__name__)


def analyze_brand(scraped_pages: dict[str, str]) -> str:
    """Analyze scraped brand pages → product info, mechanisms, USPs, voice."""
    # Format scraped content with source URLs
    content_parts = []
    for url, text in scraped_pages.items():
        content_parts.append(f"--- SOURCE: {url} ---\n{text}")

    raw_content = "\n\n".join(content_parts)

    # Truncate if too long (keep first ~80k chars to stay within token limits)
    if len(raw_content) > 80000:
        raw_content = raw_content[:80000] + "\n\n[CONTENT TRUNCATED — analyze what's provided]"

    logger.info(f"Running brand analysis on {len(scraped_pages)} pages ({len(raw_content)} chars)")

    return research_analysis(
        system_prompt=BRAND_ANALYSIS_PROMPT,
        raw_content=raw_content,
        instruction="Analyze this brand's website content and produce a comprehensive brand analysis following the output structure exactly.",
    )


def analyze_reviews(reviews: list[dict]) -> str:
    """Analyze customer reviews → golden nuggets, objections, questions."""
    if not reviews:
        return "# Review Mining\n\nNo customer reviews were found during scraping. Manual review data needed for complete analysis."

    # Format reviews
    review_parts = []
    for i, review in enumerate(reviews, 1):
        source = review.get("source", "unknown")
        text = review.get("text", "")
        rating = review.get("rating")
        rating_str = f" (Rating: {rating}/5)" if rating else ""
        review_parts.append(f"**Review #{i}** [Source: {source}]{rating_str}\n{text}")

    raw_content = "\n\n---\n\n".join(review_parts)

    if len(raw_content) > 80000:
        raw_content = raw_content[:80000] + "\n\n[REVIEWS TRUNCATED — analyze what's provided]"

    logger.info(f"Running review mining on {len(reviews)} reviews ({len(raw_content)} chars)")

    return research_analysis(
        system_prompt=REVIEW_MINING_PROMPT,
        raw_content=raw_content,
        instruction=f"Mine these {len(reviews)} customer reviews and extract golden nuggets, objections, questions, and emotional language following the Skeptic-to-Superfan methodology exactly.",
    )


def build_personas(brand_analysis: str, review_analysis: str) -> str:
    """Build 3-4 complete personas from brand + review data."""
    raw_content = (
        "## BRAND ANALYSIS\n\n"
        f"{brand_analysis}\n\n"
        "---\n\n"
        "## REVIEW MINING RESULTS\n\n"
        f"{review_analysis}"
    )

    if len(raw_content) > 80000:
        raw_content = raw_content[:80000] + "\n\n[CONTENT TRUNCATED]"

    logger.info(f"Building personas from combined research ({len(raw_content)} chars)")

    return research_analysis(
        system_prompt=PERSONA_BUILDING_PROMPT,
        raw_content=raw_content,
        instruction="Build 3-4 complete customer personas using the 5-Category Avatar SOP. Follow the output format exactly. Include full pain layering for each persona.",
    )


def market_synthesis(brand_analysis: str, review_analysis: str, personas: str) -> str:
    """Synthesize all research into market overview."""
    raw_content = (
        "## BRAND ANALYSIS\n\n"
        f"{brand_analysis}\n\n"
        "---\n\n"
        "## REVIEW MINING RESULTS\n\n"
        f"{review_analysis}\n\n"
        "---\n\n"
        "## CUSTOMER PERSONAS\n\n"
        f"{personas}"
    )

    if len(raw_content) > 100000:
        raw_content = raw_content[:100000] + "\n\n[CONTENT TRUNCATED]"

    logger.info(f"Running market synthesis ({len(raw_content)} chars)")

    return research_analysis(
        system_prompt=MARKET_SYNTHESIS_PROMPT,
        raw_content=raw_content,
        instruction="Synthesize all the research data into a strategic market overview. Follow the output structure exactly.",
    )


def generate_condensed_summary(
    brand_analysis: str, review_analysis: str, personas: str, market: str
) -> str:
    """Compress all research into a single dense copywriter's brief."""
    raw_content = (
        "## BRAND ANALYSIS\n\n"
        f"{brand_analysis}\n\n"
        "---\n\n"
        "## REVIEW MINING RESULTS\n\n"
        f"{review_analysis}\n\n"
        "---\n\n"
        "## CUSTOMER PERSONAS\n\n"
        f"{personas}\n\n"
        "---\n\n"
        "## MARKET SYNTHESIS\n\n"
        f"{market}"
    )

    if len(raw_content) > 120000:
        raw_content = raw_content[:120000] + "\n\n[CONTENT TRUNCATED]"

    logger.info(f"Generating condensed summary ({len(raw_content)} chars)")

    return research_analysis(
        system_prompt=CONDENSED_SUMMARY_PROMPT,
        raw_content=raw_content,
        instruction="Compress ALL of this research into a single dense copywriter's brief (4,000-6,000 words). This will be the primary context document for all future creative work for this brand.",
    )
