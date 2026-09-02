"""
Ticker lookup — turn a symbol into the facts a user would otherwise have to
type by hand: the asset's real name, its current price, and its currency.

Beginners are the users least able to fill an "add asset" form correctly:
they may not know a fund's registered name, and a mistyped symbol silently
costs them live tracking. Looking the symbol up removes the typing AND
validates it in the same step — a symbol that resolves is a symbol that will
keep tracking.
"""

import logging
from typing import Optional

from backend.services import cache as cache_service

logger = logging.getLogger("lumos.ticker_lookup")

# Prices move, names don't. A short TTL keeps the quoted price honest while
# still absorbing the repeated lookups a user makes while filling one form.
_TTL_SECONDS = 900

# Failures are cached far more briefly than successes. Upstream rate-limits us
# intermittently — MSFT resolved locally while production returned nothing —
# and remembering that for a quarter of an hour would tell a user their
# perfectly valid symbol does not exist. Long enough to stop a keystroke storm,
# short enough that a blip heals inside the same form session.
_MISS_TTL_SECONDS = 60


def _name_from_search(symbol: str) -> Optional[str]:
    """
    Yahoo's search endpoint, used only for the display name.

    `Ticker.info` returns nothing from our production datacenter — every
    lookup came back with a price and no name, which is exactly the typing
    the feature was meant to remove. This is a different endpoint and does
    answer from there.
    """
    try:
        import httpx

        res = httpx.get(
            "https://query2.finance.yahoo.com/v1/finance/search",
            params={"q": symbol, "quotesCount": 5, "newsCount": 0},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=6,
        )
        if res.status_code != 200:
            return None
        quotes = res.json().get("quotes", [])
        # Only an exact symbol match — a fuzzy hit would label the holding
        # with some other company's name.
        hit = next((q for q in quotes if (q.get("symbol") or "").upper() == symbol), None)
        if not hit:
            return None
        return hit.get("longname") or hit.get("shortname") or None
    except Exception as exc:
        logger.warning("name search failed for %s: %s", symbol, type(exc).__name__)
        return None


def lookup(ticker: str) -> Optional[dict]:
    """
    Resolve a symbol to {ticker, name, price, currency, exchange}.

    Returns None when the symbol doesn't resolve — the caller reports that as
    "not found" so the user can correct a typo instead of saving a dead symbol.
    """
    symbol = (ticker or "").strip().upper()
    if not symbol:
        return None

    cache_key = f"ticker_lookup:{symbol}"
    cached = cache_service.get(cache_key)
    if cached is not None:
        return cached or None  # empty dict = cached "not found"

    try:
        import yfinance as yf

        tk = yf.Ticker(symbol)
        fast = tk.fast_info
        price = getattr(fast, "last_price", None)
        currency = getattr(fast, "currency", None)
        exchange = getattr(fast, "exchange", None)

        name = None
        try:
            info = tk.info
            name = info.get("longName") or info.get("shortName")
        except Exception:
            # .info is the slow, fragile path; a missing name is survivable,
            # a missing price is not.
            pass
        if not name:
            name = _name_from_search(symbol)

        if price is None:
            # fast_info hits a Yahoo endpoint that is unreliable from our
            # datacenter — SPY resolved locally but 404'd from production while
            # the app was happily pricing SPY elsewhere. Fall back to the
            # download path the rest of the app already depends on, so lookup
            # is never weaker than valuation.
            try:
                from backend.services.market_data import fetch_current_price

                price = fetch_current_price(symbol)
            except Exception:
                # Must not escape: an exception here would skip the miss-cache
                # below and let a bad symbol hit the network on every keystroke.
                price = None

        if price is None:
            # Nothing usable — remember the miss briefly so a user hammering a
            # bad symbol doesn't hammer the upstream with it.
            cache_service.set(cache_key, {}, ttl=_MISS_TTL_SECONDS)
            return None

        result = {
            "ticker": symbol,
            # None, not the symbol: echoing "THYAO.IS" back as the asset's name
            # would look like a successful lookup and quietly become the name
            # the user stores. The client leaves the field for them instead.
            "name": name or None,
            "price": round(float(price), 4),
            "currency": currency or None,
            "exchange": exchange or None,
        }
        cache_service.set(cache_key, result, ttl=_TTL_SECONDS)
        return result
    except Exception as exc:
        logger.warning("ticker lookup failed for %s: %s", symbol, type(exc).__name__)
        return None
