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
# A batch that came back short is served for a few minutes only, so the next
# request retries the missing symbol instead of inheriting the gap all day.
INCOMPLETE_TTL_SECONDS = 60 * 5

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
        result = {t: s for t, s in result.items() if s is not None and not s.empty}

        # A batch can come back missing a symbol while every other one lands.
        # That partial answer used to be cached — including into the
        # never-expiring last-known-good copy — so one bad fetch froze a real
        # holding at its purchase price indefinitely: VNQ showed no change for
        # weeks while SPY, requested in the same call, tracked live.
        missing = [t for t in tickers if t not in result]
        for ticker in missing:
            try:
                single = yf.download(
                    tickers=ticker, period=period,
                    auto_adjust=True, progress=False, threads=False,
                )
                if single is None or single.empty:
                    continue
                if isinstance(single.columns, pd.MultiIndex):
                    series = single["Close"][ticker].dropna()
                else:
                    series = single["Close"].dropna()
                if not series.empty:
                    result[ticker] = series
                    logger.info("recovered %s with a single-ticker retry", ticker)
            except Exception:
                logger.warning("retry for %s failed — it stays absent", ticker)

        if not result:
            raise MarketDataError(f"yfinance returned no usable data for {tickers}")
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

    complete = all(t in result for t in tickers)
    # An incomplete answer is worth serving now but must not be remembered as
    # the good copy — the never-expiring fallback is exactly what turned one
    # missing symbol into a permanently frozen holding.
    if complete:
        cache_service.set(cache_key, result)
        cache_service.set(stale_key, result, ttl=STALE_TTL_SECONDS)
        cache_service.set(lkg_key, result, ttl=None)
    else:
        cache_service.set(cache_key, result, ttl=INCOMPLETE_TTL_SECONDS)
        logger.warning(
            "partial market data for %s (missing %s) — cached briefly, not as last-known-good",
            tickers, [t for t in tickers if t not in result],
        )
    return result


def fetch_current_price(ticker: str) -> Optional[float]:
    """Return the latest closing price for a single ticker."""
    history = fetch_price_history([ticker], period="5d")
    series = history.get(ticker)
    if series is None or series.empty:
        return None
    return float(series.iloc[-1])
