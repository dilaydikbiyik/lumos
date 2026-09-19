"""
German regional house prices — Deutsche Bundesbank, free and keyless.

Germany has no Bundesland-level house price index in any free source. That is
not an oversight, it is the state of the data, and it was checked rather than
assumed (2026-09-18):

  * Eurostat's entire prc_hpi_* family is country-level. Passing NUTS codes
    (DE1, DE3, DEA) to prc_hpi_q returns zero observations, and a scan of the
    full Eurostat catalogue finds no dataset that is both a property price
    index and regional.
  * Destatis GENESIS and regionalstatistik.de do publish regional figures, but
    every data endpoint returns 401 for the guest account — they need a
    (free) registration, which is a different kind of dependency.

What the Bundesbank does publish, without a key, is a residential price index
for three CITY-SIZE aggregates, 2004 onwards:

  DE0007   the seven largest cities
  DE0127   127 cities
  DEK      all districts and independent cities — i.e. the country

These are NESTED, not alternatives: Berlin is inside all three. So this is a
comparison of market segments — "what have prices done in the big cities
versus the country" — and the caller must present it as one. Ranking them
against each other as places to buy would be nonsense.

Annual, not quarterly, unlike the Turkish and US series.

The same API also carries Germany's monthly harmonised consumer price index
and its actual-rentals component — and it is nine months fresher than
Eurostat's, which is why the German market reads inflation from here.
"""

import csv
import io
import logging
from typing import Optional

from backend.services import cache as cache_service

logger = logging.getLogger("lumos.bundesbank")

_PROPERTY = "https://api.statistiken.bundesbank.de/rest/data/BBDR1"
_PRICES = "https://api.statistiken.bundesbank.de/rest/data/BBDP1"
_TTL_SECONDS = 60 * 60 * 24
_TIMEOUT = 30

# All residential property, transaction-weighted, index 2022 = 100. One
# measure across all three aggregates, so the comparison is like-for-like.
_MEASURE = "N.BBK.BRWHTTGK.P.I22.A"

SEGMENTS: dict[str, str] = {
    "DE0007": "Seven largest cities",
    "DE0127": "127 cities",
    "DEK": "All districts (Germany)",
}

# Observations are annual; the rest of the app works in months, so each year
# is anchored to a month the other series would also carry.
_YEAR_ANCHOR = "12"


def _series(geo: str) -> Optional[dict[str, float]]:
    """{YYYY-12: index} for one aggregate, or None when unreadable."""
    cache_key = f"bundesbank:hpi:{geo}"
    lkg_key = f"lkg:{cache_key}"
    cached = cache_service.get(cache_key)
    if cached is not None:
        return cached or None

    try:
        import httpx

        res = httpx.get(f"{_PROPERTY}/A.{geo}.{_MEASURE}",
                        params={"format": "csv"}, timeout=_TIMEOUT,
                        follow_redirects=True)
        res.raise_for_status()

        # The Bundesbank's CSV is semicolon-separated with a decimal comma,
        # and carries metadata rows above the observations.
        out: dict[str, float] = {}
        for row in csv.reader(io.StringIO(res.text), delimiter=";"):
            if len(row) < 2:
                continue
            period, value = row[0].strip(), row[1].strip()
            if len(period) != 4 or not period.isdigit() or not value:
                continue
            try:
                out[f"{period}-{_YEAR_ANCHOR}"] = float(value.replace(",", "."))
            except ValueError:
                continue

        if not out:
            raise RuntimeError(f"Bundesbank returned no observations for {geo}")

        cache_service.set(cache_key, out, ttl=_TTL_SECONDS)
        cache_service.set(lkg_key, out, ttl=None)
        return out
    except Exception as exc:
        logger.warning("Bundesbank fetch failed for %s (%s)", geo, type(exc).__name__)
        fallback = cache_service.get(lkg_key)
        if fallback:
            logger.warning("Serving last-known-good Bundesbank data for %s", geo)
            return fallback
        return None


def get_segments(lang: str = "tr") -> dict[str, dict]:
    """
    Every aggregate, shaped like the other sub-national readers:
    {code: {"name": ..., "index": {YYYY-MM: value}}}.

    A segment that fails is omitted. Unlike the state map there are only
    three, so a partial result is still a usable comparison rather than a
    misleading sample.
    """
    from backend.i18n import t

    out: dict[str, dict] = {}
    for geo, fallback in SEGMENTS.items():
        index = _series(geo)
        if index:
            name = t(f"segment.{geo}", lang)
            out[geo] = {"name": fallback if name == f"segment.{geo}" else name,
                        "index": index}
    return out


# ── Consumer prices ──────────────────────────────────────────────────────────
# Monthly harmonised index, the same concept Eurostat publishes. Kept here
# because the Bundesbank's copy is current while Eurostat's stopped nine
# months short — for every euro-area country, not only Germany.

_HICP_TOTAL = "M.DE.N.HVPI.C.A00000.I.A"
_HICP_RENTS = "M.DE.N.HVPI.C.E2C041.I.A"


def _monthly(series_key: str, cache_name: str) -> Optional[dict[str, float]]:
    """{YYYY-MM: index} for a monthly Bundesbank series."""
    cache_key = f"bundesbank:{cache_name}"
    lkg_key = f"lkg:{cache_key}"
    cached = cache_service.get(cache_key)
    if cached is not None:
        return cached or None

    try:
        import httpx

        res = httpx.get(f"{_PRICES}/{series_key}", params={"format": "csv"},
                        timeout=_TIMEOUT, follow_redirects=True)
        res.raise_for_status()

        out: dict[str, float] = {}
        for row in csv.reader(io.StringIO(res.text), delimiter=";"):
            if len(row) < 2:
                continue
            period, value = row[0].strip(), row[1].strip()
            # YYYY-MM rows only; the file also carries metadata and headers.
            if len(period) != 7 or not period[:4].isdigit() or not value:
                continue
            try:
                out[period] = float(value.replace(",", "."))
            except ValueError:
                continue

        if not out:
            raise RuntimeError(f"Bundesbank returned no observations for {series_key}")

        cache_service.set(cache_key, out, ttl=_TTL_SECONDS)
        cache_service.set(lkg_key, out, ttl=None)
        return out
    except Exception as exc:
        logger.warning("Bundesbank fetch failed for %s (%s)", series_key, type(exc).__name__)
        fallback = cache_service.get(lkg_key)
        if fallback:
            logger.warning("Serving last-known-good Bundesbank data for %s", series_key)
            return fallback
        return None


def get_hicp_index() -> Optional[dict[str, float]]:
    """Germany's harmonised consumer price index, keyed by YYYY-MM."""
    return _monthly(_HICP_TOTAL, "hicp")


def get_rent_index() -> Optional[dict[str, float]]:
    """Actual rentals for housing — the HICP component, not a house price."""
    return _monthly(_HICP_RENTS, "rents")
