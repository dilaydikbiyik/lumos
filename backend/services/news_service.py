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
from typing import Optional

import httpx

from backend.services import cache as cache_service
from backend.services.ai_service import generate_text

logger = logging.getLogger("lumos.news")

_DIGEST_TTL = 60 * 60 * 12  # refresh twice a day

# The reader's language and the market's headlines are separate choices: an
# English reader investing in Türkiye wants Turkish market news written in
# English. Both used to be welded to Turkish.
_LANGUAGE_NAMES = {"tr": "TURKISH", "en": "ENGLISH", "de": "GERMAN"}

_DIGEST_SYSTEM = """You are a calm financial news curator for nervous first-time investors.
From the headlines provided, pick AT MOST 3 items relevant to a beginner following the given investment path (stocks / real_estate / hybrid).
ALL output text MUST be in {language} — that is the language the reader chose. The headlines you are given may be in another language; translate them rather than quoting them.
For each picked item output exactly this JSON structure, and output ONLY a JSON array:
[{{"headline": "<rewritten in plain, calm language - no shouting, no jargon>",
  "why_it_matters": "<1 sentence: does this affect a beginner's portfolio?>",
  "calmness_note": "<1 sentence that prevents panic, e.g. 'There is nothing you need to do right now.'>"}}]
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


def fetch_headlines(market: str = "TR") -> list[dict]:
    """Collect recent headlines from the market's feeds; failures are non-fatal."""
    from backend.markets import get_market_pack

    headlines: list[dict] = []
    for url in get_market_pack(market).news_feeds:
        try:
            resp = httpx.get(url, timeout=8, follow_redirects=True)
            resp.raise_for_status()
            headlines.extend(_parse_rss(resp.text))
        except Exception as exc:
            logger.warning("Feed %s failed: %s", url, exc)
    return headlines


def get_daily_digest(investment_path: str = "hybrid", market: str = "TR",
                     lang: str = "tr") -> list[dict]:
    """
    Return up to 3 calm, beginner-framed news items for the given path.
    Cached per day + path + market + language — the same headlines rewritten
    in another language are a different answer, so they need a different key.
    """

    cache_key = f"news_digest:{date.today().isoformat()}:{investment_path}:{market}:{lang}"
    cached = cache_service.get(cache_key)
    if cached is not None:
        return cached

    headlines = fetch_headlines(market)
    if not headlines:
        return []

    titles = "\n".join(f"- {h['title']}" for h in headlines[:25])
    raw = generate_text(
        f"Investment path: {investment_path}\n\nHeadlines:\n{titles}",
        system=_DIGEST_SYSTEM.format(
            language=_LANGUAGE_NAMES.get(lang, _LANGUAGE_NAMES["tr"])
        ),
        # Summarising headlines into calm one-liners is mechanical work. Run
        # it on a small fast model rather than the one the advisor uses.
        job="light",
    )
    from backend.services.json_extract import extract_json_array

    digest = extract_json_array(raw)
    if digest is None:
        logger.warning("News digest JSON parse failed; returning empty digest")
        digest = []

    digest = digest[:3]
    cache_service.set(cache_key, digest, ttl=_DIGEST_TTL)
    return digest


def context_sentence(investment_path: str = "hybrid", market: str = "TR",
                     lang: str = "tr") -> Optional[str]:
    """
    One calm sentence about what is going on right now, for the scenario card.

    Strictly SEPARATE from the numbers. The scenario band is the distribution
    of an asset's own history and must stay that way — a model that could
    nudge the figures would turn a measurement into a forecast, which is the
    one thing every projection in this app refuses to be.

    So this reads the digest that already exists and returns prose beside the
    band, never into it. It returns None rather than filler: a card with no
    sentence is fine, a card with an invented one is not.
    """
    try:
        digest = get_daily_digest(investment_path, market, lang)
    except Exception as exc:
        logger.warning("context sentence unavailable (%s)", type(exc).__name__)
        return None

    if not digest:
        return None

    # The digest is already calm, already in the reader's language, and
    # already cached for the day — one more model call here would buy nothing
    # except another thing to go wrong.
    first = digest[0]
    if isinstance(first, dict):
        return first.get("takeaway") or first.get("summary") or first.get("headline")
    return str(first) if first else None
