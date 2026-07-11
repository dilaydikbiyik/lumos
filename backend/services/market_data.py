"""
Market data service — fetches prices via yfinance with daily caching.

Supported asset classes:
  - BIST (XU100 proxy: ISCTR.IS, AKBNK.IS etc.)
  - US ETFs: SPY, QQQ
  - Gold: GLD
  - REIT ETFs: VNQ, SCHH  (added in Phase 3.5)
"""

import logging

import pandas as pd
import yfinance as yf
from typing import Optional

from backend.exceptions import MarketDataError
from backend.services import cache as cache_service

logger = logging.getLogger("lumos.market_data")

# Stale copies outlive the fresh cache — used only when yfinance fails
STALE_TTL_SECONDS = 60 * 60 * 24 * 7  # 7 days

# REALISM NOTE (2026-07-10): Yahoo started blocking requests from old
# yfinance versions in production, and with both cache tiers empty the user
# saw a hard error ("Market data temporarily unavailable"). A third tier was
# added: a never-expiring "last known good" (LKG) copy. Any install that has
# fetched successfully once keeps working on the latest real data even if
# Yahoo goes fully dark — dated real data instead of an error page, and
# never a fabricated value.

# ── Default asset universe ────────────────────────────────────────────────────
DEFAULT_TICKERS = [
    "XU100.IS",   # BIST 100 index (proxy)
    "SPY",        # S&P 500 ETF
    "QQQ",        # Nasdaq ETF
    "GLD",        # Gold ETF
    "VNQ",        # Vanguard Real Estate ETF
    "SCHH",       # Schwab US REIT ETF
]


def fetch_price_history(
    tickers: Optional[list] = None,
    period: str = "1y",
) -> dict[str, pd.Series]:
    """
    Download adjusted close prices for the given tickers.
    Results are cached for 24 hours.

    Returns:
        dict mapping ticker → pd.Series of daily adjusted close prices.
    """
    tickers = tickers or DEFAULT_TICKERS
    cache_key = f"price_history:{'_'.join(sorted(tickers))}:{period}"
    stale_key = f"stale:{cache_key}"
    lkg_key = f"lkg:{cache_key}"  # last-known-good: never-expiring last resort

    cached = cache_service.get(cache_key)
    if cached is not None:
        return cached

    try:
        raw = yf.download(
            tickers=tickers,
            period=period,
            auto_adjust=True,
            progress=False,
            threads=True,
        )
        if raw is None or raw.empty:
            raise MarketDataError(f"yfinance returned no data for {tickers}")

        # yfinance returns MultiIndex if multiple tickers
        if isinstance(raw.columns, pd.MultiIndex):
            closes = raw["Close"]
        else:
            closes = raw[["Close"]]
            closes.columns = tickers

        result = {ticker: closes[ticker].dropna() for ticker in closes.columns}
    except Exception as exc:
        # Fallback 1: stale copy (≤7 days) — Fallback 2: last-known-good (no expiry)
        for label, key in (("stale", stale_key), ("last-known-good", lkg_key)):
            fallback = cache_service.get(key)
            if fallback is not None:
                logger.warning(
                    "yfinance failed (%s) — serving %s market data for %s",
                    exc, label, tickers,
                )
                return fallback
        raise MarketDataError(f"Market data fetch failed with no fallback: {exc}") from exc

    cache_service.set(cache_key, result)
    cache_service.set(stale_key, result, ttl=STALE_TTL_SECONDS)
    cache_service.set(lkg_key, result, ttl=None)  # never expires
    return result


def fetch_current_price(ticker: str) -> Optional[float]:
    """Return the latest closing price for a single ticker."""
    history = fetch_price_history([ticker], period="5d")
    series = history.get(ticker)
    if series is None or series.empty:
        return None
    return float(series.iloc[-1])
