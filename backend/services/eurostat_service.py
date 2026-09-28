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
        if cache_service.in_cooldown("eurostat"):
            raise cache_service.UpstreamInCooldown("eurostat")

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
        # Leave this source alone for a short while. Without it every
        # subsequent request re-attempts a dead upstream and waits out
        # the full timeout; stale data is fine, a hung app is not.
        if not isinstance(exc, cache_service.UpstreamInCooldown):
            cache_service.start_cooldown("eurostat")
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


def get_regional_populations(geos: list[str], age: str = "TOTAL",
                             since: str = "2019") -> Optional[dict[str, dict[str, float]]]:
    """
    Population for MANY NUTS-2 regions, keyed {geo: {year: value}}, in ONE
    request.

    Plural on purpose. Fetching a region at a time meant 26 serial HTTP calls
    for a Turkish reader and 38 for a German one — doubled again by the
    working-age band — which took two minutes on a cold cache. Eurostat
    accepts repeated `geo` parameters, so the whole table is one call.

    This is also why the TÜİK blocker lifted. Sub-national population for
    Türkiye lives in TÜİK's MEDAS, a ZK-framework UI with no data API: every
    response is a session-bound component update, so reading it would mean
    scraping a government site, which this app does nowhere. Eurostat
    publishes the same figures for Türkiye as a candidate country, through the
    interface this module already speaks for Germany.

    `age` takes Eurostat's own bands, so Y15-64 against TOTAL gives the
    working-age share without a second data source.
    """
    if not geos:
        return None

    cache_key = f"eurostat:pop:{','.join(sorted(geos))}:{age}:{since}"
    lkg_key = f"lkg:{cache_key}"
    cached = cache_service.get(cache_key)
    if cached is not None:
        return cached or None

    try:
        if cache_service.in_cooldown("eurostat"):
            raise cache_service.UpstreamInCooldown("eurostat")

        import httpx

        params = [("format", "JSON"), ("lang", "EN"), ("sex", "T"),
                  ("age", age), ("sinceTimePeriod", since)]
        params += [("geo", g) for g in geos]
        res = httpx.get(f"{_BASE}/demo_r_pjanaggr3", params=params, timeout=30)
        res.raise_for_status()
        payload = res.json()

        # A multi-dimension response keys values by a FLAT row-major index, so
        # the position of each dimension has to be rebuilt from `id`/`size`
        # rather than assumed — the dimension order is the server's to choose.
        dim_ids = payload["id"]
        sizes = payload["size"]
        strides = {}
        stride = 1
        for name, size in zip(reversed(dim_ids), reversed(sizes)):
            strides[name] = stride
            stride *= size

        geo_index = payload["dimension"]["geo"]["category"]["index"]
        time_index = payload["dimension"]["time"]["category"]["index"]
        # Every other dimension is pinned to a single value by the query, so
        # its position is 0 and contributes nothing to the offset.
        values = payload["value"]

        out: dict[str, dict[str, float]] = {}
        for geo, gpos in geo_index.items():
            series = {}
            for period, tpos in time_index.items():
                flat = gpos * strides["geo"] + tpos * strides["time"]
                value = values.get(str(flat))
                if value is not None:
                    series[period] = float(value)
            if series:
                out[geo] = series

        if not out:
            raise RuntimeError("Eurostat returned no observations")

        cache_service.set(cache_key, out, ttl=_TTL_SECONDS)
        cache_service.set(lkg_key, out, ttl=None)
        return out
    except Exception as exc:
        logger.warning("Eurostat population fetch failed (%s)", type(exc).__name__)
        if not isinstance(exc, cache_service.UpstreamInCooldown):
            cache_service.start_cooldown("eurostat")
        fallback = cache_service.get(lkg_key)
        if fallback:
            logger.warning("Serving last-known-good Eurostat population data")
            return fallback
        return None
