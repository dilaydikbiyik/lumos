"""
Volatility calculator.

Computes annualised volatility (standard deviation of daily log returns)
over the last 252 trading days (≈ 1 year).

Formula:
    vol = std(log_returns) * sqrt(252)

Cached for 24 hours.
"""

import numpy as np
import pandas as pd

from backend.services import cache as cache_service
from backend.services.market_data import fetch_price_history

TRADING_DAYS = 252


def compute_volatility(tickers: list[str]) -> dict[str, float]:
    """
    Return annualised volatility for each ticker.

    Returns:
        dict: { ticker: annualised_vol }   e.g. {"SPY": 0.18, "GLD": 0.14}
    """
    cache_key = f"volatility:{'_'.join(sorted(tickers))}"
    cached = cache_service.get(cache_key)
    if cached is not None:
        return cached

    price_history = fetch_price_history(tickers, period="1y")

    result: dict[str, float] = {}
    for ticker, prices in price_history.items():
        if len(prices) < 20:
            result[ticker] = 0.2  # fallback
            continue
        log_returns: pd.Series = np.log(prices / prices.shift(1)).dropna()
        vol = float(log_returns.std() * np.sqrt(TRADING_DAYS))
        result[ticker] = round(vol, 6)

    cache_service.set(cache_key, result)
    return result
