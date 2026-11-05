"""
The stock explorer: many companies, described and never recommended.

Asked for so the app would feel as broad as a brokerage — "Midas has a lot
of stocks" — while staying an education tool. The line it must not cross is
the one in docs/legal-review-brief.md: naming specific instruments
PERSONALISED to someone is the investment-advice question. So this module is
built so that it cannot personalise, and the tests hold it to that:

  * it reads the MARKET and nothing else about the user — not the risk
    score, not the holdings, not the profile. Two readers on one market get
    byte-identical numbers;
  * the list is sorted by NAME. Sorting by return would turn it into a
    leaderboard of last year's winners, which is a recommendation by
    ordering;
  * there is no score, rank, rating or "suits you" field anywhere in it.

What it says about each company is the one thing a beginner most needs to
learn about single stocks, measured rather than asserted: over the same five
years, how far did THIS company fall at its worst, and how far did the whole
index fall? The index is what the recommended funds hold; a single company
almost always swings harder. Returns are shown inflation-adjusted, like
every other figure in the app — a Turkish stock's nominal lira return over
five years is mostly inflation, and printing it raw would teach the
opposite of what the app exists to teach.
"""
import logging
from datetime import date
from typing import Optional

import numpy as np
import pandas as pd

from backend.exceptions import MarketDataError
from backend.markets import get_market_pack
from backend.services import cache as cache_service
from backend.services import inflation_service
from backend.services.market_data import fetch_price_history

logger = logging.getLogger("lumos.stock_explorer")

WINDOW_YEARS = 5
_TRADING_DAYS = 252
_CACHE_TTL = 12 * 3600          # prices move daily; the lesson does not need minutes


def _measure(series: Optional[pd.Series]) -> Optional[dict]:
    """Five-year facts about one price series, or None when there is too little."""
    if series is None:
        return None
    s = series.dropna()
    # Most of the window, or the comparison with the index is not like for like.
    if len(s) < _TRADING_DAYS * (WINDOW_YEARS - 0.5):
        return None
    drawdown = float((s / s.cummax() - 1.0).min())
    log_ret = np.log(s / s.shift(1)).dropna()
    return {
        "change_pct": round((float(s.iloc[-1]) / float(s.iloc[0]) - 1) * 100, 1),
        "worst_drop_pct": round(drawdown * 100, 1),
        "volatility_pct": round(float(log_ret.std() * np.sqrt(_TRADING_DAYS)) * 100, 1),
    }


def _real(change_pct: float, market: str) -> Optional[float]:
    """Inflation-adjusted, or None when the deflator cannot be read."""
    try:
        start = inflation_service.years_to_months_ago(WINDOW_YEARS)
        end = inflation_service.years_to_months_ago(0)
        return round(inflation_service.real_return_pct(change_pct, start, end, market), 1)
    except Exception:            # missing CPI months — show nominal only, say so
        logger.info("no deflator for %s over %sy", market, WINDOW_YEARS)
        return None


def explore(market: str) -> dict:
    """
    Every explorer stock for `market` with its five-year facts and the
    index's, sorted by name. Deliberately takes no user: see module docstring.
    """
    pack = get_market_pack(market)
    cache_key = f"stock_explorer:{pack.code}:{date.today().isoformat()}"
    cached = cache_service.get(cache_key)
    if cached is not None:
        return cached

    stocks = pack.explorer_stocks
    benchmark = pack.explorer_benchmark or {"ticker": pack.default_index_ticker,
                                            "total_return": True}
    index_ticker = benchmark["ticker"]
    total_return = bool(benchmark["total_return"])
    try:
        # One basis for the companies AND the benchmark, chosen by what the
        # benchmark can be measured on. Mixing them flattered every company.
        history = fetch_price_history([s["ticker"] for s in stocks] + [index_ticker],
                                      period=f"{WINDOW_YEARS}y", adjusted=total_return)
    except MarketDataError as exc:
        logger.warning("stock explorer: no market data (%s)", exc)
        return {"available": False, "market": pack.code, "stocks": []}

    index = _measure(history.get(index_ticker))
    if index:
        index["real_change_pct"] = _real(index["change_pct"], pack.code)

    rows = []
    for stock in stocks:
        facts = _measure(history.get(stock["ticker"]))
        if facts is None:
            continue             # a company with too short a record is left out, not estimated
        facts["real_change_pct"] = _real(facts["change_pct"], pack.code)
        if index and index["volatility_pct"]:
            facts["swing_vs_index"] = round(facts["volatility_pct"] / index["volatility_pct"], 1)
        rows.append({**stock, **facts})

    # By NAME. Never by return — that would be a leaderboard, and a
    # leaderboard is a recommendation by ordering.
    rows.sort(key=lambda r: r["name"].casefold())

    result = {
        "available": bool(rows),
        "market": pack.code,
        "as_of": pack.explorer_as_of,
        "window_years": WINDOW_YEARS,
        "dividends_included": total_return,
        "index": {"ticker": index_ticker, "name": pack.default_index_name or index_ticker,
                  **index} if index else None,
        "stocks": rows,
    }
    cache_service.set(cache_key, result, ttl=_CACHE_TTL)
    return result
