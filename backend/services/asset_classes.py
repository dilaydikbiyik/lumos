"""
Every kind of investment a reader here can make, compared on one footing.

Asked for so the app covers "everything about investing, like Midas — but
educational and comparative": cash, the US Treasury bills people buy for a
"guaranteed" return, bonds short and long, gold, property funds, the home
market, the US or world market, and bitcoin. The comparison is only worth
anything if every row is measured the same way, so each one is:

  * over the SAME five years;
  * in the READER'S currency. A dollar instrument held by a Turkish reader
    earns its own return AND whatever the lira did against the dollar, so it
    is converted at the daily rate before anything is measured. Reporting a
    US Treasury fund's dollar return to a lira saver would describe an
    investment they never had;
  * on ONE calendar. Bitcoin trades at weekends and exchanges do not;
    annualising daily volatility over calendar days with a 252-day factor
    understates it. Every series is aligned to business days first;
  * inflation-adjusted with the reader's own inflation, like every other
    figure in the app;
  * with dividends and coupons included wherever the source has them, and a
    per-row flag where it does not (the BIST 100 is a price index there).

Cash is a row too, because "do nothing" is the comparison most savers are
actually making: nominal change zero, real change whatever inflation took.

Impersonal like the rest of the explorer: it reads the market and nothing
about the reader. The order is the page's teaching order, calm to volatile,
not a ranking, and nothing in it says buy.
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

logger = logging.getLogger("lumos.asset_classes")

WINDOW_YEARS = 5
# Business days per year on the aligned calendar. Every series is resampled
# to business days (holidays carried), which gives ~261 rows a year, not the
# 252 trading days of an exchange — so 252 here would annualise wrong.
_BDAYS = 261
_CACHE_TTL = 12 * 3600


def _real(change_pct: float, market: str) -> Optional[float]:
    try:
        start, end = inflation_service.inflation_window(WINDOW_YEARS, market)
        return round(inflation_service.real_return_pct(change_pct, start, end, market), 1)
    except Exception:
        logger.info("no deflator for %s over %sy", market, WINDOW_YEARS)
        return None


def _on_business_days(s: pd.Series) -> pd.Series:
    """
    One calendar for every asset: the price AS OF each business day.

    Reindexed, not resampled. resample("B").last() filed Saturday's and
    Sunday's bitcoin prices under Friday, so "Friday's close" was really
    Sunday's — caught by a test that compares a weekend-trading series with
    the same series minus its weekends. Taking each business day's own price
    leaves the weekend's move where it belongs, in Monday's return.
    """
    s = s.dropna()
    s.index = pd.to_datetime(s.index)
    if s.index.tz is not None:
        s.index = s.index.tz_localize(None)
    s.index = s.index.normalize()
    s = s[~s.index.duplicated(keep="last")].sort_index()
    days = pd.bdate_range(s.index[0], s.index[-1])
    return s.reindex(days, method="ffill").dropna()


def _measure(s: pd.Series) -> Optional[dict]:
    # The window is cut by DATE, exactly five years back, because the
    # deflator is: inflation is taken over the five years ending this month.
    # The first version cut the last 252×5 rows of a business-day calendar,
    # which is 4.8 years — so prices started in mid-January 2022 while
    # inflation started in November 2021. In lira that put the December 2021
    # crash inside the deflator and outside the price, and every dollar
    # instrument's lira return was wrong by more than half: bitcoin showed
    # +81% in dollars over "five years" when it was +24%.
    start = s.index[-1] - pd.DateOffset(years=WINDOW_YEARS)
    if s.index[0] > start + pd.Timedelta(days=10):
        return None                      # the record does not reach back five years
    s = s[s.index >= start]
    log_ret = np.log(s / s.shift(1)).dropna()
    return {
        "change_pct": round((float(s.iloc[-1]) / float(s.iloc[0]) - 1) * 100, 1),
        "worst_drop_pct": round(float((s / s.cummax() - 1).min()) * 100, 1),
        "volatility_pct": round(float(log_ret.std() * np.sqrt(_BDAYS)) * 100, 1),
    }


def _latest(series: Optional[pd.Series]) -> Optional[float]:
    if series is None or series.dropna().empty:
        return None
    return round(float(series.dropna().iloc[-1]), 2)


def compare(market: str) -> dict:
    pack = get_market_pack(market)
    key = f"asset_classes:{pack.code}:{date.today().isoformat()}"
    cached = cache_service.get(key)
    if cached is not None:
        return cached

    classes = pack.asset_classes
    home = pack.currency
    period = f"{WINDOW_YEARS + 1}y"     # a little extra, so the window is complete after alignment

    adjusted = [c["ticker"] for c in classes if c["ticker"] and c["total_return"]]
    unadjusted = [c["ticker"] for c in classes if c["ticker"] and not c["total_return"]]
    fx_tickers = sorted({f"{c['currency']}{home}=X" for c in classes
                         if c["ticker"] and c["currency"] != home})
    yield_tickers = sorted({c["yield_ticker"] for c in classes if c.get("yield_ticker")})

    try:
        prices = fetch_price_history(adjusted + fx_tickers + yield_tickers, period=period)
        if unadjusted:
            prices.update(fetch_price_history(unadjusted, period=period, adjusted=False))
    except MarketDataError as exc:
        logger.warning("asset classes: no market data (%s)", exc)
        return {"available": False, "market": pack.code, "classes": []}

    rows = []
    for c in classes:
        row = {"key": c["key"], "ticker": c["ticker"], "currency": c["currency"],
               "dividends_included": bool(c["total_return"])}
        if c["ticker"] is None:
            # Cash: it never moves in its own currency, and inflation is the
            # whole story — which is exactly what most savers compare against.
            row.update({"change_pct": 0.0, "worst_drop_pct": 0.0, "volatility_pct": 0.0})
        else:
            series = prices.get(c["ticker"])
            if series is None or series.empty:
                continue
            series = _on_business_days(series)
            if c["currency"] != home:
                fx = prices.get(f"{c['currency']}{home}=X")
                if fx is None or fx.empty:
                    continue        # never show a foreign return as if it were local
                fx = _on_business_days(fx).reindex(series.index).ffill()
                series = (series * fx).dropna()
            facts = _measure(series)
            if facts is None:
                continue
            row.update(facts)
        row["real_change_pct"] = _real(row["change_pct"], pack.code)
        if c.get("yield_ticker"):
            row["live_yield_pct"] = _latest(prices.get(c["yield_ticker"]))
        rows.append(row)

    result = {
        "available": bool(rows),
        "market": pack.code,
        "currency": home,
        "window_years": WINDOW_YEARS,
        "as_of": date.today().isoformat(),
        "classes": rows,
    }
    cache_service.set(key, result, ttl=_CACHE_TTL)
    return result
