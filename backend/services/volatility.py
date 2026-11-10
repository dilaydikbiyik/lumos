"""
Volatility calculator.

Computes annualised volatility (standard deviation of daily log returns)
over the last 252 trading days (≈ 1 year).

Formula:
    vol = std(log_returns) * sqrt(252)

Cached for 24 hours.
"""

import logging

import numpy as np
import pandas as pd

from backend.exceptions import MarketDataError
from backend.services import cache as cache_service
from backend.services.market_data import fetch_price_history

logger = logging.getLogger("lumos.volatility")

TRADING_DAYS = 252

# Last resort: a fresh install with the data source down must not turn the
# portfolio recommendation into an error page. These are not fabricated —
# each is the asset's multi-year historical annualised volatility level;
# they yield to the real computation as soon as live data returns.
BASELINE_VOLATILITY = {
    "XU100.IS": 0.35,
    "SPY": 0.17,
    "QQQ": 0.24,
    "GLD": 0.15,
    "VNQ": 0.21,
    "SCHH": 0.22,
}
_DEFAULT_VOL = 0.2


# Five years, not one.
#
# Measured 2026-11-05: over ONE year gold's volatility was 29.0% — above the
# BIST 100 (24.6%) and the Nasdaq 100 (21.0%) — because gold had an unusually
# violent year. Over five years it is 19.2% and the BIST 100 29.2%; over ten,
# 16.6% and 25.6%. A single unusual year was flipping the order of the
# assets, and since an aggressive profile weights growth assets BY volatility,
# the most aggressive portfolios put 43-50% of the money into gold — while
# the app's own projection guard refuses to draw anything from fewer than
# three independent periods. One year is not a description of an asset; it
# is a description of last year. Five years covers a full cycle and still
# moves when the world does.
VOLATILITY_WINDOW = "5y"


def compute_volatility(tickers: list[str], currency: str | None = None) -> dict[str, float]:
    """
    Return annualised volatility for each ticker — in `currency` when given.

    In the READER's currency, because that is the swing they live with: for
    a Turkish reader the S&P 500 fund moved 23% a year in lira, not the 17%
    it moved in dollars, and the cash fund 17%, not 0.3%. Measured in
    dollars, the engine read dollar funds as the calm ones and tilted
    cautious Turkish profiles toward them, and the cards quoted dollar
    swings beside lira amounts.

    Returns:
        dict: { ticker: annualised_vol }   e.g. {"SPY": 0.18, "GLD": 0.14}
    """
    # The window is part of the key. It used to be absent, so changing the
    # window would have left the durable cache serving last week's one-year
    # numbers in production as if nothing had changed.
    cache_key = f"volatility:{VOLATILITY_WINDOW}:{currency or 'own'}:{'_'.join(sorted(tickers))}"
    cached = cache_service.get(cache_key)
    if cached is not None:
        return cached

    try:
        price_history = fetch_price_history(tickers, period=VOLATILITY_WINDOW)
        if currency:
            from backend.services.fx_history import in_home_currency
            price_history = in_home_currency(price_history, currency, VOLATILITY_WINDOW)
    except MarketDataError as exc:
        # Data source and every cache tier are down: continue with
        # historical baseline volatilities — never show the user an error page.
        logger.warning("volatility falling back to historical baselines: %s", exc)
        return {t: BASELINE_VOLATILITY.get(t, _DEFAULT_VOL) for t in tickers}

    result: dict[str, float] = {}
    for ticker, prices in price_history.items():
        if len(prices) < 20:
            result[ticker] = BASELINE_VOLATILITY.get(ticker, _DEFAULT_VOL)
            continue
        log_returns: pd.Series = np.log(prices / prices.shift(1)).dropna()
        vol = float(log_returns.std() * np.sqrt(TRADING_DAYS))
        result[ticker] = round(vol, 6)

    cache_service.set(cache_key, result)
    return result
