"""
What a typical home costs in the reader's market — the starting point for
every example amount on the property pages.

Asked for after the region explorer offered "what if you had bought for
1,000,000" in every market: about 18 m² at Türkiye's national price, and a
large house in Germany. An example the reader cannot picture teaches
nothing, so the default is the price of an ordinary home where they live,
read live where an official source publishes one:

  * Türkiye — TCMB's national housing unit price (TL per m²) times 100 m²;
  * United States — the median sales price of houses sold (FRED: MSPUS);
  * Germany — no free live series; a dated published per-m² figure.

Every answer says where it came from and when, and whether it is live. A
live source that cannot be read falls back to the pack's dated figure, never
to a number with no date on it.
"""
import logging
from datetime import date

from backend.markets import get_market_pack
from backend.services import cache as cache_service

logger = logging.getLogger("lumos.typical_home")
_TTL = 24 * 3600


def _live(spec: dict):
    """(price, as_of) from the live source, or None."""
    if spec["source"] == "evds":
        from backend.services import evds_service
        start = f"01-01-{date.today().year - 2}"
        end = f"31-12-{date.today().year}"
        batch = evds_service.fetch_quarterly_series_batch([spec["series"]], start, end) or {}
        series = batch.get(spec["series"]) or {}
        if series:
            month = max(series)
            return series[month] * spec["m2"], month
    elif spec["source"] == "fred":
        from backend.services import fred_service
        series = fred_service._observations(spec["series"], f"{date.today().year - 2}-01-01") or {}
        if series:
            month = max(series)
            return series[month], month
    return None


def _round(price: float) -> float:
    """Two significant figures: an example amount, not a valuation."""
    if price <= 0:
        return 0.0
    magnitude = 10 ** (len(str(int(price))) - 2)
    return float(round(price / magnitude) * magnitude)


def typical_home(market: str) -> dict:
    pack = get_market_pack(market)
    spec = pack.typical_home
    key = f"typical_home:{pack.code}:{date.today().isoformat()}"
    cached = cache_service.get(key)
    if cached is not None:
        return cached

    live = None
    if spec["source"] in ("evds", "fred"):
        try:
            live = _live(spec)
        except Exception as exc:          # a dead upstream must not break the page
            logger.warning("typical home: live read failed for %s (%s)", pack.code, type(exc).__name__)

    if live:
        price, as_of = live
    elif spec["source"] == "static":
        price, as_of = spec["price_per_m2"] * spec["m2"], spec["as_of"]
    else:
        price, as_of = spec["fallback"], spec["as_of"]

    result = {
        "market": pack.code,
        "currency": pack.currency,
        "price": round(price),
        "example_amount": _round(price),
        "source": spec["source"],
        "source_name": spec.get("source_name", ""),
        "m2": spec.get("m2"),
        "live": bool(live),
        "as_of": as_of,
    }
    cache_service.set(key, result, ttl=_TTL)
    return result
