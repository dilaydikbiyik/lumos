"""
Time Machine — historical simulation of a portfolio allocation.

Answers "what if you had built this portfolio N years ago?" with honest
worst-case framing (max drawdown, longest stagnation) so beginners see
the character of what they are buying, not just the happy line.
"""
import logging

import pandas as pd

from backend.exceptions import MarketDataError
from backend.services import inflation_service
from backend.services.market_data import fetch_price_history

logger = logging.getLogger("lumos.backtest")

# A period counts as "stagnation" when price stays within this band
STAGNATION_BAND = 0.05  # ±5%
TRADING_DAYS_PER_MONTH = 21


def _max_drawdown(series: pd.Series) -> dict:
    """Deepest peak-to-trough fall and how long recovery took."""
    running_max = series.cummax()
    drawdown = series / running_max - 1.0
    trough_idx = drawdown.idxmin()
    depth = float(drawdown.min())

    # Recovery: first index after trough where the previous peak is regained
    peak_value = running_max.loc[trough_idx]
    after = series.loc[trough_idx:]
    recovered = after[after >= peak_value]
    recovery_days = int(len(after.loc[:recovered.index[0]])) if not recovered.empty else None

    return {
        "max_drawdown_pct": round(depth * 100, 2),
        "recovery_trading_days": recovery_days,  # None = never recovered in window
    }


def _longest_stagnation_months(series: pd.Series) -> float:
    """
    Longest stretch (in months) where price never left a ±5% band around
    the stretch's starting price — "the asset went nowhere".
    """
    values = series.to_numpy()
    longest = 0
    start = 0
    anchor = values[0]

    for i, value in enumerate(values):
        if abs(value / anchor - 1.0) > STAGNATION_BAND:
            longest = max(longest, i - start)
            start = i
            anchor = value
    longest = max(longest, len(values) - start)

    return round(longest / TRADING_DAYS_PER_MONTH, 1)


def run_backtest(weights: dict[str, float], budget: float, period: str = "5y") -> dict:
    """
    Simulate holding a weighted portfolio over the period.

    Args:
        weights: ticker -> weight (should sum to ~1)
        budget:  starting amount (user's own money — makes the numbers real)
        period:  yfinance period string ("1y", "3y", "5y")

    Returns:
        dict with final value, total return, per-asset character metrics,
        and a downsampled value series for charting.
    """
    history = fetch_price_history(list(weights), period=period)

    # Align all series on common dates
    frame = pd.DataFrame(history).dropna()
    if frame.empty:
        raise MarketDataError(f"No overlapping history for {list(weights)}")

    normalised = frame / frame.iloc[0]  # each asset starts at 1.0
    portfolio = sum(normalised[t] * w for t, w in weights.items() if t in normalised)
    value_series = portfolio * budget

    drawdown = _max_drawdown(value_series)

    per_asset = {}
    for ticker in weights:
        if ticker not in frame:
            continue
        s = frame[ticker]
        per_asset[ticker] = {
            **_max_drawdown(s),
            "longest_stagnation_months": _longest_stagnation_months(s),
            "total_return_pct": round((float(s.iloc[-1] / s.iloc[0]) - 1) * 100, 2),
        }

    # Downsample to ~120 points for the frontend chart
    step = max(len(value_series) // 120, 1)
    sampled = value_series.iloc[::step]
    chart = [
        {"date": str(idx.date() if hasattr(idx, "date") else idx), "value": round(float(v), 2)}
        for idx, v in sampled.items()
    ]

    total_return_pct = round((float(value_series.iloc[-1]) / budget - 1) * 100, 2)

    # Real (inflation-adjusted) return — the honest number most apps hide
    years = {"1y": 1, "3y": 3, "5y": 5}.get(period, 1)
    start_month = inflation_service.years_to_months_ago(years)
    end_month = inflation_service.years_to_months_ago(0)
    try:
        real_pct = inflation_service.real_return_pct(total_return_pct, start_month, end_month)
    except Exception:
        real_pct = None

    return {
        "period": period,
        "start_value": budget,
        "final_value": round(float(value_series.iloc[-1]), 2),
        "total_return_pct": total_return_pct,
        "real_return_pct": real_pct,
        **drawdown,
        "worst_value": round(float(value_series.min()), 2),
        "per_asset": per_asset,
        "chart": chart,
    }
