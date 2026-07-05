"""
Future scenarios — the honest answer to "what could my money become?".

We never predict. Instead we compute EVERY rolling N-year window in the
asset's own history and report the distribution: pessimistic (p10),
typical (median), optimistic (p90). The user sees a RANGE the asset has
actually produced, applied to their own amount — with the worst window
shown first (vision: honest downside before upside).
"""
import logging

import numpy as np

from backend.exceptions import MarketDataError
from backend.services import evds_service, inflation_service
from backend.services.market_data import fetch_price_history

logger = logging.getLogger("lumos.projection")

TRADING_DAYS_PER_YEAR = 252
MIN_WINDOWS = 6  # fewer rolling windows than this -> refuse to pretend it's a distribution


def _rolling_window_returns(values: np.ndarray, window: int, step: int) -> list[float]:
    """Total returns of every `window`-length slice, sampled every `step` points."""
    returns = []
    for start in range(0, len(values) - window, step):
        begin, end = values[start], values[start + window]
        if begin > 0:
            returns.append(end / begin - 1)
    return returns


def _band(returns: list[float], amount: float) -> dict:
    arr = np.array(returns)
    p10, p50, p90 = np.percentile(arr, [10, 50, 90])
    return {
        "windows_analysed": len(returns),
        "pessimistic": {"return_pct": round(p10 * 100, 1), "value": round(amount * (1 + p10), 2)},
        "typical":     {"return_pct": round(p50 * 100, 1), "value": round(amount * (1 + p50), 2)},
        "optimistic":  {"return_pct": round(p90 * 100, 1), "value": round(amount * (1 + p90), 2)},
    }


def project_asset(ticker: str, amount: float, years: int) -> dict:
    """
    Scenario band for an exchange-traded asset from its own daily history.
    Uses the longest history yfinance provides (up to 10y).
    """
    history = fetch_price_history([ticker], period="10y")
    series = history.get(ticker)
    if series is None or series.empty:
        raise MarketDataError(f"No history for {ticker}")

    values = series.to_numpy()
    window = years * TRADING_DAYS_PER_YEAR
    # sample monthly so windows overlap without being near-duplicates
    returns = _rolling_window_returns(values, window, step=21)

    if len(returns) < MIN_WINDOWS:
        return {
            "available": False,
            "reason": (
                f"{ticker} için {years} yıllık pencere dağılımı çıkaracak kadar "
                "geçmiş veri yok — daha kısa bir vade dene."
            ),
        }

    years_covered = round(len(values) / TRADING_DAYS_PER_YEAR, 1)
    return {
        "available": True,
        "ticker": ticker,
        "amount": amount,
        "years": years,
        "history_years": years_covered,
        **_band(returns, amount),
        "honesty_note": (
            f"Bu bir tahmin DEĞİL: {ticker}'nin kendi geçmişindeki tüm {years} yıllık "
            "dönemlerin dağılımı. Gelecek bu aralığın dışına da çıkabilir."
        ),
    }


def project_region(region_code: str, amount: float, years: int) -> dict:
    """
    Scenario band for a housing region from the TCMB index (monthly).
    Also converts the typical scenario to REAL terms so a nominal boom
    during high inflation doesn't masquerade as wealth.
    """
    data = evds_service.get_regional_housing_indices()
    entry = data.get(region_code)
    if not entry:
        return {"available": False, "reason": "Bölge verisi şu an alınamıyor."}

    index = entry["index"]
    months_sorted = sorted(index)
    values = np.array([index[m] for m in months_sorted])
    window = years * 12
    returns = _rolling_window_returns(values, window, step=1)

    if len(returns) < MIN_WINDOWS:
        available_years = max(len(values) // 12, 0)
        return {
            "available": False,
            "reason": (
                f"TCMB bölge endeksi {available_years} yıllık geçmişe sahip — {years} yıllık "
                "senaryo bandı için yeterli pencere yok. Daha kısa vade dene "
                "(endeks 2023'te yeniden bazlandı)."
            ),
        }

    band = _band(returns, amount)

    # typical senaryonun reel karşılığı — nominal patlama servet sanılmasın
    start_month = months_sorted[max(len(months_sorted) - 1 - window, 0)]
    end_month = months_sorted[-1]
    try:
        real_typical = inflation_service.real_return_pct(
            band["typical"]["return_pct"], start_month, end_month
        )
    except Exception:
        real_typical = None

    return {
        "available": True,
        "region_code": region_code,
        "region": entry["region"],
        "amount": amount,
        "years": years,
        **band,
        "typical_real_return_pct": real_typical,
        "honesty_note": (
            "Bölge (NUTS2) endeksi dağılımıdır — tek bir mahalle/parsel değil. "
            "\"60 kat arttı\" anekdotları genelde nominal ve seçilmiş örneklerdir; "
            "reel karşılığı yanında gösteriyoruz."
        ),
    }
