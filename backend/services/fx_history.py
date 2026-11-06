"""
Price histories in the READER's currency.

A Turkish reader who held SPY earned the S&P 500's dollar return AND
whatever the lira did against the dollar. The backtest, the projections and
practice mode used the raw dollar series and then deflated the result by
Turkish inflation: a five-year TR portfolio came out at -62% real, with the
S&P 500 at +69% (its dollar return) beside the BIST 100's +614% in lira,
summed as if they were one currency. The asset-class comparison already
converted, so two pages disagreed about the same money.

Every series quoted in another currency is multiplied by that currency's
daily rate into the home currency before anything is measured. A series
whose currency is unknown, or whose rate cannot be read, is DROPPED rather
than passed through: a dollar return shown as a lira one is the defect this
module exists to remove, and the callers' coverage guards then decide
whether enough of the portfolio is left to say anything.
"""
import logging

import pandas as pd

from backend.services.holdings_valuation import ticker_currency
from backend.services.market_data import fetch_price_history

logger = logging.getLogger("lumos.fx_history")


def _naive(s: pd.Series) -> pd.Series:
    s = s.dropna().copy()
    idx = pd.to_datetime(s.index)
    if idx.tz is not None:
        idx = idx.tz_localize(None)
    s.index = idx.normalize()
    return s[~s.index.duplicated(keep="last")].sort_index()


def in_home_currency(history: dict[str, pd.Series], home: str,
                     period: str) -> dict[str, pd.Series]:
    """`history` with every foreign-currency series converted to `home`."""
    currency = {t: ticker_currency(t) for t, s in history.items() if s is not None and not s.empty}
    foreign = sorted({c for c in currency.values() if c and c != home})
    rates = {}
    if foreign:
        pairs = [f"{c}{home}=X" for c in foreign]
        try:
            fetched = fetch_price_history(pairs, period=period)
        except Exception as exc:          # no rates means no foreign series, said below
            logger.warning("fx history unavailable for %s (%s)", pairs, type(exc).__name__)
            fetched = {}
        for c, pair in zip(foreign, pairs):
            series = fetched.get(pair)
            if series is not None and not series.empty:
                rates[c] = _naive(series)

    out = {}
    for ticker, cur in currency.items():
        series = history[ticker]
        if cur == home:
            out[ticker] = series
        elif cur in rates:
            s = _naive(series)
            rate = rates[cur].reindex(s.index, method="ffill")
            converted = (s * rate).dropna()
            if not converted.empty:
                out[ticker] = converted
        else:
            logger.info("dropping %s: no %s->%s rate", ticker, cur, home)
    return out
