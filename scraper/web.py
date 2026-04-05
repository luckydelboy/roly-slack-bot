"""
Web scraping engine — fetches and extracts content from brand sites and review sources.
Uses httpx for HTTP requests and trafilatura for content extraction.
"""

import logging
import time
import re
from urllib.parse import urljoin, urlparse

import httpx
import trafilatura
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

TIMEOUT = httpx.Timeout(15.0, connect=10.0)


def scrape_url(url: str) -> str:
    """Fetch a URL and extract its main text content."""
    try:
        resp = httpx.get(url, headers=HEADERS, timeout=TIMEOUT, follow_redirects=True)
        resp.raise_for_status()
        extracted = trafilatura.extract(
            resp.text,
            include_comments=False,
            include_tables=True,
            include_links=False,
            favor_recall=True,
        )
        return extracted or ""
    except Exception as e:
        logger.warning(f"Failed to scrape {url}: {e}")
        return ""


def _find_internal_links(html: str, base_url: str, base_domain: str) -> list[str]:
    """Extract internal links from an HTML page."""
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        full_url = urljoin(base_url, href)
        parsed = urlparse(full_url)
        # Only keep same-domain, HTTP(S), no fragments, no query-heavy URLs
        if (
            parsed.netloc == base_domain
            and parsed.scheme in ("http", "https")
            and not parsed.fragment
            and len(parsed.query) < 50
        ):
            clean = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            links.add(clean.rstrip("/"))
    return list(links)


def _is_useful_page(url: str) -> bool:
    """Filter for pages likely to contain useful brand/product info."""
    path = urlparse(url).path.lower()
    # Skip common non-content pages
    skip_patterns = [
        "/cart", "/checkout", "/account", "/login", "/register",
        "/privacy", "/terms", "/cookie", "/refund", "/shipping",
        "/cdn-cgi/", "/wp-admin/", "/wp-json/", ".pdf", ".jpg",
        ".png", ".gif", "/tag/", "/category/", "/page/",
    ]
    for pattern in skip_patterns:
        if pattern in path:
            return False
    # Prioritize content-rich pages
    good_patterns = [
        "/product", "/about", "/ingredient", "/how-it-work",
        "/science", "/review", "/testimon", "/result", "/story",
        "/benefit", "/faq", "/blog/", "/collections/", "/pages/",
    ]
    # Homepage is always useful
    if path in ("", "/"):
        return True
    # Prefer content pages, but allow others up to depth limit
    for pattern in good_patterns:
        if pattern in path:
            return True
    # Allow product pages (common e-commerce pattern)
    if path.count("/") <= 2:
        return True
    return False


def scrape_site(base_url: str, max_pages: int = 20) -> dict[str, str]:
    """Crawl a brand's site starting from base_url.
    Returns {url: extracted_text} for up to max_pages useful pages.
    Also stores raw HTML for review extraction (accessible via _raw_html_cache)."""
    global _raw_html_cache
    _raw_html_cache = {}

    parsed = urlparse(base_url)
    base_domain = parsed.netloc
    visited = set()
    results = {}
    to_visit = [base_url.rstrip("/")]

    while to_visit and len(results) < max_pages:
        url = to_visit.pop(0)
        if url in visited:
            continue
        visited.add(url)

        if not _is_useful_page(url):
            continue

        logger.info(f"Scraping: {url}")
        try:
            resp = httpx.get(url, headers=HEADERS, timeout=TIMEOUT, follow_redirects=True)
            resp.raise_for_status()
        except Exception as e:
            logger.warning(f"Failed to fetch {url}: {e}")
            continue

        # Store raw HTML for review extraction
        _raw_html_cache[url] = resp.text

        # Extract text content
        extracted = trafilatura.extract(
            resp.text,
            include_comments=False,
            include_tables=True,
            include_links=False,
            favor_recall=True,
        )
        if extracted and len(extracted) > 100:
            results[url] = extracted

        # Find more internal links
        new_links = _find_internal_links(resp.text, url, base_domain)
        for link in new_links:
            if link not in visited:
                to_visit.append(link)

        # Be polite
        time.sleep(1.5)

    logger.info(f"Scraped {len(results)} pages from {base_domain}")
    return results


# Cache for raw HTML — used by review extraction
_raw_html_cache: dict[str, str] = {}


def find_review_sources(brand_name: str, product_name: str = "") -> list[str]:
    """Build a list of URLs where we might find customer reviews.
    Returns URLs to try scraping for reviews."""
    sources = []
    # Reddit search URLs (we'll use PRAW separately, but these are fallback)
    search_terms = f"{brand_name} {product_name}".strip()
    encoded = search_terms.replace(" ", "+")
    sources.append(f"https://www.reddit.com/search/?q={encoded}&sort=relevance&t=year")
    return sources


def extract_onsite_reviews(scraped_pages: dict[str, str]) -> list[dict]:
    """Extract reviews from the raw HTML of scraped pages.
    Handles Judge.me, Yotpo, Okendo, Stamped, Loox, and generic review patterns."""
    reviews = []

    # Use raw HTML cache if available, fall back to scraped_pages text
    html_sources = _raw_html_cache if _raw_html_cache else {}

    for url, raw_html in html_sources.items():
        soup = BeautifulSoup(raw_html, "html.parser")

        # ── Judge.me reviews ──────────────────────────────
        jdgm_reviews = soup.find_all(class_="jdgm-rev")
        for rev in jdgm_reviews:
            body_el = rev.find(class_="jdgm-rev__body")
            title_el = rev.find(class_="jdgm-rev__title")
            author_el = rev.find(class_="jdgm-rev__author")
            rating_el = rev.find(class_="jdgm-rev__rating")

            body = body_el.get_text(strip=True) if body_el else ""
            title = title_el.get_text(strip=True) if title_el else ""
            author = author_el.get_text(strip=True) if author_el else ""

            # Extract star rating from data attribute or count stars
            rating = None
            if rating_el:
                rating_attr = rating_el.get("data-score")
                if rating_attr:
                    try:
                        rating = int(float(rating_attr))
                    except ValueError:
                        pass

            full_text = f"{title}. {body}".strip(". ") if title and title != body else body
            if full_text and len(full_text) > 10:
                reviews.append({
                    "source": "judge.me",
                    "url": url,
                    "text": full_text,
                    "rating": rating,
                    "author": author,
                })

        # ── Yotpo reviews ─────────────────────────────────
        yotpo_reviews = soup.find_all(class_="yotpo-review")
        for rev in yotpo_reviews:
            body_el = rev.find(class_="content-review")
            title_el = rev.find(class_="content-title")
            author_el = rev.find(class_="yotpo-user-name")

            body = body_el.get_text(strip=True) if body_el else ""
            title = title_el.get_text(strip=True) if title_el else ""
            author = author_el.get_text(strip=True) if author_el else ""

            full_text = f"{title}. {body}".strip(". ") if title else body
            if full_text and len(full_text) > 10:
                reviews.append({
                    "source": "yotpo",
                    "url": url,
                    "text": full_text,
                    "rating": None,
                    "author": author,
                })

        # ── Okendo reviews ────────────────────────────────
        okendo_reviews = soup.find_all(attrs={"data-oke-review": True})
        for rev in okendo_reviews:
            body_el = rev.find(class_="oke-w-review-body") or rev.find(class_="oke-review-body")
            body = body_el.get_text(strip=True) if body_el else ""
            if body and len(body) > 10:
                reviews.append({
                    "source": "okendo",
                    "url": url,
                    "text": body,
                    "rating": None,
                })

        # ── Generic review patterns (fallback) ────────────
        # Look for common review CSS classes
        for class_name in ["review-text", "review-body", "review-content", "testimonial-text", "testimonial-body"]:
            for el in soup.find_all(class_=class_name):
                text = el.get_text(strip=True)
                if text and len(text) > 20 and text not in [r["text"] for r in reviews]:
                    reviews.append({
                        "source": "brand_site",
                        "url": url,
                        "text": text,
                        "rating": None,
                    })

    # Also try regex patterns on the extracted text as a last resort
    if not reviews:
        for url, text in scraped_pages.items():
            quote_patterns = [
                r'"([^"]{30,300})"[\s\-–—]+([A-Z][a-z]+ [A-Z]\.?)',
            ]
            for pattern in quote_patterns:
                matches = re.findall(pattern, text)
                for match in matches:
                    review_text = match[0] if isinstance(match, tuple) else match
                    reviews.append({
                        "source": "brand_site",
                        "url": url,
                        "text": review_text.strip(),
                        "rating": None,
                    })

    logger.info(f"Extracted {len(reviews)} on-site reviews")
    return reviews


def scrape_judgeme_pages(base_url: str, max_pages: int = 5) -> list[dict]:
    """Fetch additional Judge.me review pages by hitting the paginated widget.
    Judge.me loads page 1 server-side, but additional pages via AJAX.
    We can hit the same endpoint with page=2,3,etc."""
    reviews = []

    # Find the Shopify domain from the raw HTML cache
    shopify_domain = None
    for url, html in _raw_html_cache.items():
        match = re.search(r'([a-z0-9-]+\.myshopify\.com)', html)
        if match:
            shopify_domain = match.group(1)
            break

    if not shopify_domain:
        logger.info("Could not find Shopify domain for Judge.me pagination")
        return reviews

    logger.info(f"Fetching additional Judge.me pages for {shopify_domain}")

    for page in range(2, max_pages + 1):
        try:
            resp = httpx.get(
                f"https://judge.me/reviews/reviews_for_widget",
                params={
                    "url": shopify_domain,
                    "shop_domain": shopify_domain,
                    "platform": "shopify",
                    "page": page,
                    "per_page": 10,
                },
                headers=HEADERS,
                timeout=TIMEOUT,
            )
            if resp.status_code != 200:
                break

            # Parse the HTML fragment returned
            soup = BeautifulSoup(resp.text, "html.parser")
            jdgm_reviews = soup.find_all(class_="jdgm-rev")

            if not jdgm_reviews:
                break

            for rev in jdgm_reviews:
                body_el = rev.find(class_="jdgm-rev__body")
                title_el = rev.find(class_="jdgm-rev__title")
                author_el = rev.find(class_="jdgm-rev__author")
                rating_el = rev.find(class_="jdgm-rev__rating")

                body = body_el.get_text(strip=True) if body_el else ""
                title = title_el.get_text(strip=True) if title_el else ""
                author = author_el.get_text(strip=True) if author_el else ""
                rating = None
                if rating_el:
                    rating_attr = rating_el.get("data-score")
                    if rating_attr:
                        try:
                            rating = int(float(rating_attr))
                        except ValueError:
                            pass

                full_text = f"{title}. {body}".strip(". ") if title and title != body else body
                if full_text and len(full_text) > 10:
                    reviews.append({
                        "source": "judge.me",
                        "url": f"judge.me/page/{page}",
                        "text": full_text,
                        "rating": rating,
                        "author": author,
                    })

            time.sleep(1)

        except Exception as e:
            logger.warning(f"Judge.me page {page} fetch failed: {e}")
            break

    logger.info(f"Fetched {len(reviews)} additional Judge.me reviews")
    return reviews


def scrape_reddit_reviews(brand_name: str, product_name: str = "") -> list[dict]:
    """Scrape Reddit for reviews/discussions using PRAW.
    Returns empty list if Reddit credentials aren't configured."""
    try:
        from config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT
        if not REDDIT_CLIENT_ID or not REDDIT_CLIENT_SECRET:
            logger.info("Reddit credentials not configured — skipping Reddit reviews")
            return []

        import praw
        reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT,
        )

        reviews = []
        search_query = f"{brand_name} {product_name}".strip()

        # Search relevant subreddits
        subreddits = ["SkincareAddiction", "HaircareScience", "beauty", "Skincare_Addiction"]
        for sub_name in subreddits:
            try:
                subreddit = reddit.subreddit(sub_name)
                for submission in subreddit.search(search_query, limit=5, time_filter="year"):
                    # Get the post text
                    if submission.selftext and len(submission.selftext) > 50:
                        reviews.append({
                            "source": f"reddit/r/{sub_name}",
                            "url": f"https://reddit.com{submission.permalink}",
                            "text": submission.selftext[:2000],
                            "rating": None,
                        })
                    # Get top comments
                    submission.comments.replace_more(limit=0)
                    for comment in submission.comments[:10]:
                        if hasattr(comment, "body") and len(comment.body) > 50:
                            reviews.append({
                                "source": f"reddit/r/{sub_name}",
                                "url": f"https://reddit.com{submission.permalink}",
                                "text": comment.body[:1000],
                                "rating": None,
                            })
            except Exception as e:
                logger.warning(f"Reddit search in r/{sub_name} failed: {e}")
                continue

        logger.info(f"Found {len(reviews)} Reddit reviews for '{search_query}'")
        return reviews

    except ImportError:
        logger.info("praw not installed — skipping Reddit reviews")
        return []
    except Exception as e:
        logger.warning(f"Reddit scraping failed: {e}")
        return []
