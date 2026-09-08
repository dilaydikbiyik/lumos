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

    cache_key = f"fx:{base}{quote}:{on.isoformat() if on else 'latest'}"
    lkg_key = f"lkg:{cache_key}"
    cached = cache_service.get(cache_key)
    if cached is not None:
        return cached or None

    try:
        import yfinance as yf

        # Two years covers any realistic purchase date; a spot-only request
        # would leave historical conversions unanswerable.
        period = "5d" if on is None else "5y"
        history = yf.Ticker(_pair_symbol(base, quote)).history(period=period)

        if history is None or history.empty:
            # Not every pair is quoted directly; invert the mirror pair.
            mirror = yf.Ticker(_pair_symbol(quote, base)).history(period=period)
            if mirror is None or mirror.empty:
                raise RuntimeError(f"no data for {base}/{quote}")
            history = mirror
            inverted = True
        else:
            inverted = False

        closes = history["Close"]
        if on is not None:
            eligible = closes[closes.index.date <= on]
            if len(eligible) == 0:
                raise RuntimeError(f"no {base}/{quote} quote on or before {on}")
            value = float(eligible.iloc[-1])
        else:
            value = float(closes.iloc[-1])

        if value <= 0:
            raise RuntimeError("non-positive rate")
        result = 1.0 / value if inverted else value

        cache_service.set(cache_key, result, ttl=_TTL_SECONDS)
        cache_service.set(lkg_key, result, ttl=None)
        return result
    except Exception as exc:
        logger.warning("FX lookup failed for %s/%s (%s)", base, quote, type(exc).__name__)
        fallback = cache_service.get(lkg_key)
        if fallback:
            logger.warning("Serving last-known-good FX for %s/%s", base, quote)
            return fallback
        return None


def convert(amount: float, base: str, quote: str, on: Optional[date] = None) -> Optional[float]:
    """`amount` expressed in `base`, converted to `quote`. None if unknown."""
    if amount is None:
        return None
    fx = rate(base, quote, on)
    return None if fx is None else amount * fx
