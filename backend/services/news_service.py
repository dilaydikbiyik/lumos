"""
Calm news digest — raw headlines are fear machines for beginners.

We fetch RSS ourselves, then have the AI pick at most 3 items relevant to
the user's journey and rewrite each as: what happened (no jargon), does it
affect you, and a calmness note. Cached per day+path so the whole userbase
costs a handful of AI calls daily.
"""
import logging
import xml.etree.ElementTree as ET
from datetime import date

import httpx

from backend.services import cache as cache_service
from backend.services.ai_service import generate_text

logger = logging.getLogger("lumos.news")

RSS_FEEDS = [
    "https://www.aa.com.tr/tr/rss/default?cat=ekonomi",
    "https://www.bloomberght.com/rss",
]

_DIGEST_TTL = 60 * 60 * 12  # refresh twice a day

_DIGEST_SYSTEM = """You are a calm financial news curator for nervous first-time investors.
From the headlines provided, pick AT MOST 3 items relevant to a beginner following the given investment path (stocks / real_estate / hybrid).
For each picked item output exactly this JSON structure, and output ONLY a JSON array:
[{"headline": "<rewritten in plain, calm language - no shouting, no jargon>",
  "why_it_matters": "<1 sentence: does this affect a beginner's portfolio?>",
  "calmness_note": "<1 sentence that prevents panic, e.g. 'No action needed.'>"}]
Never use alarmist words. If nothing is relevant, output []."""


def _parse_rss(xml_text: str, limit: int = 15) -> list[dict]:
    items = []
    try:
        root = ET.fromstring(xml_text)
        for item in root.iter("item"):
            title = item.findtext("title") or ""
            if title.strip():
                items.append({"title": title.strip(), "link": (item.findtext("link") or "").strip()})
            if len(items) >= limit:
                break
    except ET.ParseError as exc:
        logger.warning("RSS parse failed: %s", exc)
    return items


def fetch_headlines() -> list[dict]:
    """Collect recent headlines from all feeds; failures are non-fatal."""
    headlines: list[dict] = []
    for url in RSS_FEEDS:
        try:
            resp = httpx.get(url, timeout=8, follow_redirects=True)
            resp.raise_for_status()
            headlines.extend(_parse_rss(resp.text))
        except Exception as exc:
            logger.warning("Feed %s failed: %s", url, exc)
    return headlines


def get_daily_digest(investment_path: str = "hybrid") -> list[dict]:
    """
    Return up to 3 calm, beginner-framed news items for the given path.
    Cached per day + path.
    """
    import json
    import re

    cache_key = f"news_digest:{date.today().isoformat()}:{investment_path}"
    cached = cache_service.get(cache_key)
    if cached is not None:
        return cached

    headlines = fetch_headlines()
    if not headlines:
        return []

    titles = "\n".join(f"- {h['title']}" for h in headlines[:25])
    raw = generate_text(
        f"Investment path: {investment_path}\n\nHeadlines:\n{titles}",
        system=_DIGEST_SYSTEM,
    )
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip())
    try:
        digest = json.loads(cleaned)
        if not isinstance(digest, list):
            digest = []
    except json.JSONDecodeError:
        logger.warning("News digest JSON parse failed; returning empty digest")
        digest = []

    digest = digest[:3]
    cache_service.set(cache_key, digest, ttl=_DIGEST_TTL)
    return digest
