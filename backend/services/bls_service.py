"""
US price data — Bureau of Labor Statistics public API.

No API key: the v1 endpoint answers unauthenticated, which keeps the US pack
live without asking anyone to register for anything.

Series used:
  CUUR0000SA0   headline CPI-U, all items          → real-return maths
  CUUR0000SEHA  rent of primary residence          → rent growth in rent-vs-buy

NOT a house price index. A rent index measures what it costs to OCCUPY
housing, not what homes SELL for; treating one as the other would quietly
corrupt every buy-vs-rent verdict. US house prices need Case-Shiller, which
lives behind a (free) FRED key — see fred_service.
"""

import json
import logging
from datetime import date
from pathlib import Path
from typing import Optional

from backend.services import cache as cache_service

logger = logging.getLogger("lumos.bls")

_API = "https://api.bls.gov/publicAPI/v1/timeseries/data/"
_CPI_SERIES = "CUUR0000SA0"
_RENT_SERIES = "CUUR0000SEHA"
_TTL_SECONDS = 60 * 60 * 24  # published monthly; a day is plenty

_DATA_DIR = Path(__file__).parent.parent / "data"
# Bundled snapshots. The v1 endpoint allows 25 requests/day per IP and our
# datacenter shares that budget with everyone else on it, so the live call
# does fail in production — and when it did, US inflation silently sat on a
# hardcoded 3.0% constant while claiming to be measured. A real index, even a
# slightly stale one, beats a made-up number.
_STATIC_FILES = {
    _CPI_SERIES: "us_cpi_index.json",
    _RENT_SERIES: "us_rent_index.json",
}


def _static_index(series_id: str) -> Optional[dict[str, float]]:
    filename = _STATIC_FILES.get(series_id)
    if not filename:
        return None
    try:
        return json.loads((_DATA_DIR / filename).read_text())["index"]
    except Exception:
        return None


def _fetch_series(series_id: str, years: int = 6) -> Optional[dict[str, float]]:
    """{YYYY-MM: index} for a BLS series, or None if it can't be read."""
    cache_key = f"bls:{series_id}:{years}"
    lkg_key = f"lkg:{cache_key}"
    cached = cache_service.get(cache_key)
    if cached is not None:
        return cached or None

    end_year = date.today().year
    # The v1 endpoint caps a request at 10 years; stay inside it.
    start_year = end_year - min(years, 9)

    try:
        import httpx

        res = httpx.post(
            _API,
            json={
                "seriesid": [series_id],
                "startyear": str(start_year),
                "endyear": str(end_year),
            },
            headers={"Content-Type": "application/json"},
            timeout=20,
        )
        payload = res.json()
        if payload.get("status") != "REQUEST_SUCCEEDED":
            raise RuntimeError(payload.get("status") or "BLS request failed")

        series = payload["Results"]["series"][0]["data"]
        index: dict[str, float] = {}
        for row in series:
            period = row.get("period", "")
            # M13 is BLS's annual average — a synthetic 13th month that would
            # sort after December and skew "latest value" reads.
            if not period.startswith("M") or period == "M13":
                continue
            try:
                index[f"{row['year']}-{period[1:]}"] = float(row["value"])
            except (TypeError, ValueError):
                # BLS marks suppressed or not-yet-published observations "-".
                # One such month must not cost us the entire series, which is
                # exactly what it did before this guard.
                continue

        if not index:
            raise RuntimeError("BLS returned no monthly observations")

        cache_service.set(cache_key, index, ttl=_TTL_SECONDS)
        cache_service.set(lkg_key, index, ttl=None)  # last-known-good, never expires
        return index
    except Exception as exc:
        logger.warning("BLS fetch failed for %s (%s)", series_id, type(exc).__name__)
        fallback = cache_service.get(lkg_key)
        if fallback:
            logger.warning("Serving last-known-good BLS data for %s", series_id)
            return fallback
        static = _static_index(series_id)
        if static:
            logger.warning("Serving bundled static index for %s", series_id)
            return static
        return None


def get_cpi_index() -> Optional[dict[str, float]]:
    """US CPI-U index keyed by YYYY-MM."""
    return _fetch_series(_CPI_SERIES)


def get_rent_index() -> Optional[dict[str, float]]:
    """US rent-of-primary-residence index keyed by YYYY-MM."""
    return _fetch_series(_RENT_SERIES)
