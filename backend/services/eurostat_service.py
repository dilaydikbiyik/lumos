"""
Euro-area price data — Eurostat's public dissemination API.

No API key, and it carries both series the German pack needs:

  prc_hicp_midx / CP00   harmonised consumer price index (monthly)
  prc_hpi_q    / TOTAL   house price index (quarterly)  ← a real PRICE index

Unlike the US, Germany gets a genuine house price index for free, so the
buy-vs-rent comparison rests on what homes actually sell for.

Eurostat publishes on a lag (HICP roughly a month, HPI a quarter), which is
fine: every consumer here reads "the nearest known month at or before X".
"""

import logging
from typing import Optional

from backend.services import cache as cache_service

logger = logging.getLogger("lumos.eurostat")

_BASE = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"
_TTL_SECONDS = 60 * 60 * 24


def _fetch(dataset: str, params: dict, cache_key: str) -> Optional[dict[str, float]]:
    """{period: value} from a Eurostat dataset, or None when unreadable."""
    lkg_key = f"lkg:{cache_key}"
    cached = cache_service.get(cache_key)
    if cached is not None:
        return cached or None

    try:
        import httpx

        res = httpx.get(f"{_BASE}/{dataset}", params={"format": "JSON", "lang": "EN", **params}, timeout=25)
        res.raise_for_status()
        payload = res.json()

        # Eurostat returns values in a flat map keyed by the time dimension's
        # ordinal position, not by the period label — they have to be rejoined.
        positions = payload["dimension"]["time"]["category"]["index"]
        values = payload["value"]
        series = {
            period: float(values[str(pos)])
            for period, pos in positions.items()
            if str(pos) in values and values[str(pos)] is not None
        }
        if not series:
            raise RuntimeError("Eurostat returned no observations")

        cache_service.set(cache_key, series, ttl=_TTL_SECONDS)
        cache_service.set(lkg_key, series, ttl=None)
        return series
    except Exception as exc:
        logger.warning("Eurostat fetch failed for %s (%s)", dataset, type(exc).__name__)
        fallback = cache_service.get(lkg_key)
        if fallback:
            logger.warning("Serving last-known-good Eurostat data for %s", dataset)
            return fallback
        return None


def get_hicp_index(geo: str = "DE", since: str = "2018-01") -> Optional[dict[str, float]]:
    """Harmonised CPI keyed by YYYY-MM."""
    return _fetch(
        "prc_hicp_midx",
        {"geo": geo, "coicop": "CP00", "unit": "I15", "sinceTimePeriod": since},
        f"eurostat:hicp:{geo}:{since}",
    )


def get_rent_index(geo: str = "DE", since: str = "2018-01") -> Optional[dict[str, float]]:
    """HICP sub-index for actual rentals for housing (CP041), keyed by YYYY-MM."""
    return _fetch(
        "prc_hicp_midx",
        {"geo": geo, "coicop": "CP041", "unit": "I15", "sinceTimePeriod": since},
        f"eurostat:rent:{geo}:{since}",
    )


def get_house_price_index(geo: str = "DE", since: str = "2015-Q1") -> Optional[dict[str, float]]:
    """
    House price index keyed by QUARTER (e.g. "2026-Q1") — deliberately not
    converted to months: pretending to know a monthly value Eurostat never
    published would be inventing data.
    """
    return _fetch(
        "prc_hpi_q",
        {"geo": geo, "purchase": "TOTAL", "unit": "I15_Q", "sinceTimePeriod": since},
        f"eurostat:hpi:{geo}:{since}",
    )
