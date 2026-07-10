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

# Son çare: taze kurulum + veri kaynağı kapalı senaryosunda portföy önerisi
# hata sayfasına düşmesin. Değerler uydurma değil — her varlığın çok yıllık
# tarihsel yıllıklandırılmış oynaklık mertebesidir; canlı veri gelir gelmez
# yerini gerçek hesaplamaya bırakır.
BASELINE_VOLATILITY = {
    "XU100.IS": 0.35,
    "SPY": 0.17,
    "QQQ": 0.24,
    "GLD": 0.15,
    "VNQ": 0.21,
    "SCHH": 0.22,
}
_DEFAULT_VOL = 0.2


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

    try:
        price_history = fetch_price_history(tickers, period="1y")
    except MarketDataError as exc:
        # Veri kaynağı ve tüm cache katmanları kapalı: tarihsel taban
        # oynaklıklarla devam et — kullanıcıya hata sayfası gösterme.
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
