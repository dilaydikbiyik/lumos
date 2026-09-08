"""
Currency conversion — the piece that was missing entirely.

Lumos mixes assets priced in different currencies with amounts a user typed
in their own: a Turkish beginner buys SPY (quoted in USD) and enters what
they paid in lira. Without a conversion step those two numbers were compared
directly, and the app told someone who had roughly broken even that they had
lost 97.6% of their money.

Rates come from the same market-data source as everything else, cached and
backed by a last-known-good copy, because a missing rate must degrade to
"we can't value this right now" rather than to a wrong number.
"""

import logging
from datetime import date
from typing import Optional

from backend.services import cache as cache_service

logger = logging.getLogger("lumos.fx")

_TTL_SECONDS = 60 * 60 * 6   # intraday moves don't change a portfolio's story


def _pair_symbol(base: str, quote: str) -> str:
    return f"{base}{quote}=X"


def _series(base: str, quote: str) -> Optional[dict]:
    """
    Daily closes for a pair as {YYYY-MM-DD: rate}, fetched ONCE and cached.

    The first version made a separate network call per date, so valuing a
    portfolio with several purchase dates meant several calls inside the
    valuation loop — against an upstream that rate-limits us. One stall left
    a holding unvalued and quietly showing its purchase price.
    """
    cache_key = f"fx_series:{base}{quote}"
    lkg_key = f"lkg:{cache_key}"
    cached = cache_service.get(cache_key)
    if cached is not None:
        return cached or None

    try:
        import yfinance as yf

        inverted = False
        history = yf.Ticker(_pair_symbol(base, quote)).history(period="5y")
        if history is None or history.empty:
            # Not every pair is quoted directly; invert the mirror pair.
            history = yf.Ticker(_pair_symbol(quote, base)).history(period="5y")
            inverted = True
        if history is None or history.empty:
            raise RuntimeError(f"no data for {base}/{quote}")

        closes = history["Close"]
        series = {}
        for stamp, value in closes.items():
            value = float(value)
            if value <= 0:
                continue
            day = stamp.date() if hasattr(stamp, "date") else stamp
            series[day.isoformat()] = (1.0 / value) if inverted else value

        if not series:
            raise RuntimeError(f"empty series for {base}/{quote}")

        cache_service.set(cache_key, series, ttl=_TTL_SECONDS)
        cache_service.set(lkg_key, series, ttl=None)
        return series
    except Exception as exc:
        logger.warning("FX series fetch failed for %s/%s (%s)", base, quote, type(exc).__name__)
        fallback = cache_service.get(lkg_key)
        if fallback:
            logger.warning("Serving last-known-good FX series for %s/%s", base, quote)
            return fallback
        return None


def rate(base: str, quote: str, on: Optional[date] = None) -> Optional[float]:
    """
    How many `quote` units one `base` unit buys — e.g. rate("USD", "TRY").

    `on` asks for the rate at a past date (the closest trading day at or
    before it), which is what a purchase made months ago needs.

    Returns None when the rate can't be established. Callers MUST treat that
    as "unknown", never as 1.0: silently assuming parity is how a 48x error
    gets presented as a fact.
    """
    base, quote = (base or "").upper(), (quote or "").upper()
    if not base or not quote:
        return None
    if base == quote:
        return 1.0

    series = _series(base, quote)
    if not series:
        return None

    days = sorted(series)
    if on is None:
        return series[days[-1]]

    target = on.isoformat()
    eligible = [d for d in days if d <= target]
    if not eligible:
        # A purchase older than the series: the earliest known rate beats
        # refusing to value the holding at all, and it is the closest truth
        # available.
        return series[days[0]]
    return series[eligible[-1]]


def convert(amount: float, base: str, quote: str, on: Optional[date] = None) -> Optional[float]:
    """`amount` expressed in `base`, converted to `quote`. None if unknown."""
    if amount is None:
        return None
    fx = rate(base, quote, on)
    return None if fx is None else amount * fx
