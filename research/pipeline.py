"""
Research pipeline — orchestrates the full brand research flow.
Scrape → Analyze → Build Personas → Market Synthesis → Save to Knowledge Base.
"""

import logging
import re
from urllib.parse import urlparse
from typing import Callable, Optional

import knowledge_base
from scraper.web import scrape_site, extract_onsite_reviews, scrape_reddit_reviews, scrape_judgeme_pages
from research.analyzers import (
    analyze_brand,
    analyze_reviews,
    build_personas,
    market_synthesis,
    generate_condensed_summary,
)

logger = logging.getLogger(__name__)


def _slug_from_url(url: str) -> str:
    """Extract a clean client slug from a URL domain.
    e.g., 'https://www.bekynd.com/products/scrub' → 'bekynd'
    """
    domain = urlparse(url).netloc
    # Remove www. and TLD
    domain = re.sub(r"^www\.", "", domain)
    slug = domain.split(".")[0]
    # Clean to lowercase alphanumeric + hyphens
    slug = re.sub(r"[^a-z0-9-]", "", slug.lower())
    return slug or "unknown-brand"


def _extract_brand_name(scraped_pages: dict[str, str], slug: str) -> str:
    """Try to extract the actual brand name from scraped content."""
    # Look in the first page's content for the brand name
    for url, text in scraped_pages.items():
        # Common patterns: title-case words near the beginning
        lines = text.split("\n")[:5]
        for line in lines:
            line = line.strip()
            if line and len(line) < 50 and not line.startswith("http"):
                return line
    # Fallback: capitalize the slug
    return slug.replace("-", " ").title()


def run_research(url: str, progress: Optional[Callable] = None) -> dict:
    """Run the full research pipeline for a brand URL.

    Args:
        url: The brand's website URL
        progress: Optional callback(emoji, message) for progress updates

    Returns:
        dict with keys: slug, brand_name, brand_analysis, review_analysis,
                        personas, market, summary, stats
    """
    def _progress(emoji: str, message: str):
        if progress:
            progress(emoji, message)
        logger.info(message)

    slug = _slug_from_url(url)
    _progress("mag", f"Starting research on `{slug}` — scraping {url}")

    # ── Stage 1: Scrape the brand's website ──────────────
    scraped_pages = scrape_site(url, max_pages=20)
    if not scraped_pages:
        raise ValueError(f"Could not scrape any pages from {url}. Check the URL and try again.")

    brand_name = _extract_brand_name(scraped_pages, slug)
    _progress("white_check_mark", f"Scraped {len(scraped_pages)} pages from {slug}")

    # ── Stage 2: Find and scrape reviews ─────────────────
    _progress("mag", "Hunting for customer reviews...")

    all_reviews = []

    # On-site reviews found during crawl (Judge.me, Yotpo, Okendo, etc.)
    onsite_reviews = extract_onsite_reviews(scraped_pages)
    all_reviews.extend(onsite_reviews)

    # Fetch additional Judge.me review pages (if Judge.me is detected)
    judgeme_reviews = scrape_judgeme_pages(url, max_pages=5)
    all_reviews.extend(judgeme_reviews)

    # Reddit reviews (if configured)
    reddit_reviews = scrape_reddit_reviews(brand_name)
    all_reviews.extend(reddit_reviews)

    if all_reviews:
        sources = set(r.get("source", "unknown") for r in all_reviews)
        _progress("white_check_mark", f"Found {len(all_reviews)} reviews from {len(sources)} source(s)")
    else:
        _progress("warning", "No reviews found — research will continue with site content only")

    # ── Stage 3: Brand analysis (Claude) ─────────────────
    _progress("brain", "Analyzing brand — extracting mechanisms, USPs, positioning...")
    brand_analysis = analyze_brand(scraped_pages)
    _progress("white_check_mark", "Brand analysis complete")

    # Save immediately (partial results are still useful)
    knowledge_base.save_research_file("brand", slug, "product-info.md", brand_analysis)

    # ── Stage 4: Review mining (Claude) ──────────────────
    _progress("brain", "Mining reviews — extracting golden nuggets, objections, emotional language...")
    review_analysis = analyze_reviews(all_reviews)
    nugget_count = review_analysis.count("**Review") or review_analysis.count("Hook potential")
    _progress("white_check_mark", f"Review mining complete")

    knowledge_base.save_research_file("customers", slug, "review-mining.md", review_analysis)

    # ── Stage 5: Persona building (Claude) ───────────────
    _progress("brain", "Building customer personas — 5-category avatar SOP with pain layering...")
    personas = build_personas(brand_analysis, review_analysis)
    # Count personas built
    persona_count = personas.count("## Persona") or personas.count("### CATEGORY 1") or 3
    _progress("white_check_mark", f"Persona building complete")

    knowledge_base.save_research_file("customers", slug, "avatars.md", personas)

    # ── Stage 6: Market synthesis (Claude) ───────────────
    _progress("brain", "Synthesizing market research — sophistication, positioning, angles...")
    market = market_synthesis(brand_analysis, review_analysis, personas)
    _progress("white_check_mark", "Market synthesis complete")

    knowledge_base.save_research_file("customers", slug, "market-research.md", market)

    # ── Stage 7: Condensed summary (Claude) ──────────────
    _progress("brain", "Generating condensed copywriter's brief...")
    summary = generate_condensed_summary(brand_analysis, review_analysis, personas, market)
    _progress("white_check_mark", "Condensed brief generated")

    knowledge_base.save_client_summary(slug, summary)

    # ── Done ─────────────────────────────────────────────
    stats = {
        "pages_scraped": len(scraped_pages),
        "reviews_found": len(all_reviews),
        "review_sources": len(set(r.get("source", "") for r in all_reviews)),
    }

    _progress(
        "rocket",
        f"*Research complete for {brand_name}!*\n\n"
        f"• {stats['pages_scraped']} pages scraped\n"
        f"• {stats['reviews_found']} reviews mined\n"
        f"• Full personas, market research, and copywriter's brief saved\n\n"
        f"All creative commands (`/ad`, `/advertorial`, `/listicle`, `/vsl`, `/hooks`) "
        f"now have access to `{slug}` research."
    )

    return {
        "slug": slug,
        "brand_name": brand_name,
        "brand_analysis": brand_analysis,
        "review_analysis": review_analysis,
        "personas": personas,
        "market": market,
        "summary": summary,
        "stats": stats,
    }
