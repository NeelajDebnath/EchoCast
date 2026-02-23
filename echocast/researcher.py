"""
EchoCast 2 — Research Agent
Uses Apify actors (Google Search Scraper + Website Content Crawler)
to perform deep web research on a list of search queries.
"""

from __future__ import annotations

import time
from typing import Any

from apify_client import ApifyClient

from echocast.config import APIFY_API_TOKEN, APIFY_GOOGLE_SEARCH, APIFY_WEB_CRAWLER

# ── Lazy Apify client ────────────────────────────────────────────────────────
_apify: ApifyClient | None = None

# How many top URLs to crawl per search query
_TOP_RESULTS_PER_QUERY = 3
# Max pages to crawl per website-content-crawler run
_MAX_CRAWL_PAGES = 3


def _get_apify() -> ApifyClient:
    global _apify
    if _apify is None:
        if not APIFY_API_TOKEN:
            raise RuntimeError(
                "APIFY_API_TOKEN is not set. "
                "Copy .env.example → .env and fill in your token."
            )
        _apify = ApifyClient(APIFY_API_TOKEN)
    return _apify


def _search_google(query: str) -> list[str]:
    """
    Run the Google Search Scraper actor and return the top result URLs.
    """
    print(f"  🔍  Searching Google: {query!r}")
    client = _get_apify()
    run = client.actor(APIFY_GOOGLE_SEARCH).call(
        run_input={
            "queries": query,
            "maxPagesPerQuery": 1,
            "resultsPerPage": _TOP_RESULTS_PER_QUERY,
            "languageCode": "en",
            "countryCode": "us",
        },
        timeout_secs=120,
    )
    if run is None:
        print("    ⚠️  Google search run failed.")
        return []

    dataset_items = client.dataset(run["defaultDatasetId"]).list_items().items
    urls: list[str] = []
    for item in dataset_items:
        organic = item.get("organicResults", [])
        for result in organic[:_TOP_RESULTS_PER_QUERY]:
            url = result.get("url")
            if url:
                urls.append(url)
    print(f"    ✅  Found {len(urls)} URLs")
    return urls


def _crawl_urls(urls: list[str]) -> list[dict[str, str]]:
    """
    Run the Website Content Crawler actor on a list of URLs
    and return a list of {url, title, text} dicts.
    """
    if not urls:
        return []

    print(f"  🌐  Crawling {len(urls)} URLs …")
    client = _get_apify()
    run = client.actor(APIFY_WEB_CRAWLER).call(
        run_input={
            "startUrls": [{"url": u} for u in urls],
            "maxCrawlPages": _MAX_CRAWL_PAGES,
            "crawlerType": "cheerio",          # fast HTTP-based scraper
            "maxCrawlDepth": 0,                # only the given pages
            "outputFormat": "markdown",        # clean text via markdown
            "removeElementsCssSelector": (
                "nav, header, footer, aside, "
                "[role='navigation'], [role='banner'], "
                ".cookie-banner, .ad, .ads, .sidebar"
            ),
        },
        timeout_secs=180,
    )
    if run is None:
        print("    ⚠️  Crawl run failed.")
        return []

    dataset_items = client.dataset(run["defaultDatasetId"]).list_items().items
    results: list[dict[str, str]] = []
    for item in dataset_items:
        text = item.get("text") or item.get("markdown") or ""
        # Truncate very long pages to ~15 000 chars to manage Gemini context
        if len(text) > 15_000:
            text = text[:15_000] + "\n\n[… truncated …]"
        results.append({
            "url": item.get("url", ""),
            "title": item.get("metadata", {}).get("title", item.get("url", "")),
            "text": text,
        })
    print(f"    ✅  Crawled {len(results)} pages")
    return results


def research(queries: list[str]) -> list[dict[str, str]]:
    """
    Main entry-point for the Research Agent.
    Takes a list of search queries and returns a list of
    {url, title, text} dicts from deep web crawling.
    """
    print("\n📚  RESEARCH AGENT — Starting deep research …")
    all_urls: list[str] = []
    seen: set[str] = set()

    # Step 1: Gather URLs from Google Search for each query
    for query in queries:
        urls = _search_google(query)
        for url in urls:
            if url not in seen:
                seen.add(url)
                all_urls.append(url)
        # Small delay to be polite to APIs
        time.sleep(1)

    print(f"\n  📋  Total unique URLs to crawl: {len(all_urls)}")

    # Step 2: Crawl all collected URLs
    results = _crawl_urls(all_urls)

    total_chars = sum(len(r["text"]) for r in results)
    print(f"  📊  Total research text: {total_chars:,} characters across {len(results)} pages")
    print("📚  RESEARCH AGENT — Complete.\n")
    return results
