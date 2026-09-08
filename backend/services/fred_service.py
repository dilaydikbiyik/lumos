"""
US house price data — FRED (Federal Reserve Bank of St. Louis).

This is the one source that closes the gap the US pack had been declaring
honestly: the BLS rent index measures what it costs to OCCUPY housing, not
what homes SELL for, and substituting one for the other would corrupt every
buy-vs-rent verdict. FRED carries the FHFA All-Transactions House Price
Index, which is a genuine price index — nationally and for all 50 states
plus DC, so the US finally gets the equivalent of the 81-province table.

Series (verified live 2026-09-08 against fred.stlouisfed.org):
  USSTHPI     All-Transactions HPI, United States
  {XX}STHPI   the same index per state — CASTHPI, NYSTHPI, TXSTHPI, …
Both are quarterly, both index 1980:Q1 = 100, both not seasonally adjusted.
Using FHFA for the nation AND the states keeps the units identical; mixing
in Case-Shiller (monthly, Jan-2000 = 100, 20 metros only) would not.

WHAT THIS INDEX IS, precisely: FHFA estimates it from sales prices AND
appraisal data on refinancings. Case-Shiller uses repeat sales only. So this
tracks appreciation well but is not the same measurement as TCMB's TL/m²
unit prices — the caller must say so rather than implying one number.

The key is free but required. Without it this module reports unavailable and
the US pack keeps declaring no housing index, which is the honest state.
"""

import logging
from typing import Optional

from backend.config import settings
from backend.services import cache as cache_service

logger = logging.getLogger("lumos.fred")

_BASE = "https://api.stlouisfed.org/fred/series/observations"
_TTL_SECONDS = 60 * 60 * 24
_TIMEOUT = 25

NATIONAL_SERIES = "USSTHPI"

# 50 states + DC. The series id is the postal code + "STHPI".
STATES: dict[str, str] = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
    "CA": "California", "CO": "Colorado", "CT": "Connecticut",
    "DE": "Delaware", "DC": "District of Columbia", "FL": "Florida",
    "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois",
    "IN": "Indiana", "IA": "Iowa", "KS": "Kansas", "KY": "Kentucky",
    "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota",
    "MS": "Mississippi", "MO": "Missouri", "MT": "Montana",
    "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire",
    "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
    "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio",
    "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania",
    "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota",
    "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont",
    "VA": "Virginia", "WA": "Washington", "WV": "West Virginia",
    "WI": "Wisconsin", "WY": "Wyoming",
}


def is_configured() -> bool:
    return bool(settings.FRED_API_KEY)


def series_id(state_code: str) -> str:
    return f"{state_code.upper()}STHPI"


def _observations(series: str, since: str = "2000-01-01") -> Optional[dict[str, float]]:
    """{YYYY-MM: value} for one FRED series, or None when unreadable."""
    if not is_configured():
        return None

    cache_key = f"fred:obs:{series}:{since}"
    lkg_key = f"lkg:{cache_key}"
    cached = cache_service.get(cache_key)
    if cached is not None:
        return cached or None

    try:
        import httpx

        res = httpx.get(
            _BASE,
            params={
                "series_id": series,
                "api_key": settings.FRED_API_KEY,
                "file_type": "json",
                "observation_start": since,
            },
            timeout=_TIMEOUT,
        )
        # A bad key is a 400 with a readable message — surface it plainly
        # instead of letting it look like "the data isn't there".
        if res.status_code == 400:
            logger.error("FRED rejected the request for %s: %s", series, res.text[:200])
            res.raise_for_status()
        res.raise_for_status()

        # FRED writes missing observations as "." — dropping them keeps the
        # series monotonic in time rather than inventing a zero.
        observations = {
            row["date"][:7]: float(row["value"])
            for row in res.json().get("observations", [])
            if row.get("value") not in (None, ".", "")
        }
        if not observations:
            raise RuntimeError(f"FRED returned no observations for {series}")

        cache_service.set(cache_key, observations, ttl=_TTL_SECONDS)
        cache_service.set(lkg_key, observations, ttl=None)
        return observations
    except Exception as exc:
        logger.warning("FRED fetch failed for %s (%s)", series, type(exc).__name__)
        fallback = cache_service.get(lkg_key)
        if fallback:
            logger.warning("Serving last-known-good FRED data for %s", series)
            return fallback
        return None


def get_national_hpi(since: str = "2000-01-01") -> Optional[dict[str, float]]:
    """National house price index keyed by YYYY-MM (quarterly observations)."""
    return _observations(NATIONAL_SERIES, since)


def get_state_hpi(state_code: str, since: str = "2000-01-01") -> Optional[dict[str, float]]:
    """One state's house price index keyed by YYYY-MM."""
    if state_code.upper() not in STATES:
        return None
    return _observations(series_id(state_code), since)


def get_all_state_hpi(since: str = "2000-01-01") -> dict[str, dict]:
    """
    Every state's index, shaped like the TR province payload:
    {code: {"name": ..., "index": {YYYY-MM: value}}}.

    51 requests is a lot to make on a page load, so the whole map is cached
    as one entry and the per-series cache absorbs partial failures. A state
    that fails is omitted rather than shown with a stale neighbour's numbers.
    """
    if not is_configured():
        return {}

    cache_key = f"fred:states:{since}"
    cached = cache_service.get(cache_key)
    if cached is not None:
        return cached or {}

    out: dict[str, dict] = {}
    for code, name in STATES.items():
        index = _observations(series_id(code), since)
        if index:
            out[code] = {"name": name, "index": index}

    if not out:
        return {}

    # Only a complete-enough map is worth caching: a handful of states that
    # happened to fail must not become the permanent answer for a day.
    if len(out) >= len(STATES) * 0.9:
        cache_service.set(cache_key, out, ttl=_TTL_SECONDS)
    else:
        logger.warning("FRED state map incomplete (%d/%d) — not cached",
                       len(out), len(STATES))
    return out
