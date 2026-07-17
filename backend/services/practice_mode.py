"""
Practice portfolio (practice mode) — a beginner "builds" the recommended
portfolio with fake money and watches it move with REAL market data.
Zero risk, real learning; the natural on-ramp before touching real cash.

We reuse market_data directly (not backtest.py, which needs historical
alignment) — practice mode only needs recent daily performance.
"""
import logging

from backend.exceptions import MarketDataError
from backend.services.market_data import fetch_price_history

logger = logging.getLogger("lumos.practice")

DEFAULT_PRACTICE_BUDGET = 100000.0


def practice_snapshot(weights: dict[str, float], virtual_budget: float = DEFAULT_PRACTICE_BUDGET) -> dict:
    """
    Current-state snapshot of a practice portfolio: what it would be worth
    today, and this week's change with a plain-language 'why'.
    """
    history = fetch_price_history(list(weights), period="1mo")

    per_asset = {}
    total_value = 0.0
    total_week_ago_value = 0.0

    for ticker, weight in weights.items():
        series = history.get(ticker)
        if series is None or series.empty:
            # Unpriced slice (e.g. cash): it exists and sits FLAT. Excluding
            # it would shrink the base and overstate the weekly move.
            allocation_value = virtual_budget * weight
            total_value += allocation_value
            total_week_ago_value += allocation_value
            per_asset[ticker] = {
                "weekly_change_pct": 0.0,
                "current_value": round(allocation_value, 2),
                "flat": True,
            }
            continue

        latest = float(series.iloc[-1])
        week_ago_idx = max(len(series) - 6, 0)  # ~5 trading days back
        week_ago = float(series.iloc[week_ago_idx])

        allocation_value = virtual_budget * weight
        units = allocation_value / week_ago if week_ago else 0
        current_value = units * latest

        total_value += current_value
        total_week_ago_value += allocation_value

        per_asset[ticker] = {
            "weekly_change_pct": round((latest / week_ago - 1) * 100, 2) if week_ago else 0.0,
            "current_value": round(current_value, 2),
        }

    if not per_asset or all(a.get("flat") for a in per_asset.values()):
        raise MarketDataError("No price data available for practice portfolio")

    weekly_change = total_value - total_week_ago_value
    weekly_change_pct = round((total_value / total_week_ago_value - 1) * 100, 2) if total_week_ago_value else 0.0

    # Plain-language driver: the asset that moved the most this week
    biggest_mover = max(per_asset.items(), key=lambda kv: abs(kv[1]["weekly_change_pct"]))

    return {
        "virtual_budget": virtual_budget,
        "current_value": round(total_value, 2),
        "weekly_change_amount": round(weekly_change, 2),
        "weekly_change_pct": weekly_change_pct,
        "per_asset": per_asset,
        "biggest_mover": {
            "ticker": biggest_mover[0],
            "weekly_change_pct": biggest_mover[1]["weekly_change_pct"],
        },
    }
