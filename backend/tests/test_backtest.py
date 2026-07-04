"""
Time Machine tests — market data mocked with synthetic price series.
"""
import numpy as np
import pandas as pd
import pytest
from unittest.mock import patch

from backend.services.backtest import run_backtest, _longest_stagnation_months

DATES = pd.date_range("2021-01-01", periods=504, freq="B")  # ~2 years


def _series(values):
    return pd.Series(values, index=DATES[: len(values)])


def _fake_history(tickers, period="5y"):
    # SPY: steady doubling; GLD: flat with a crash and recovery
    n = len(DATES)
    spy = _series(np.linspace(100, 200, n))
    gld = _series(np.concatenate([
        np.full(n // 2, 100.0),
        np.linspace(100, 70, n // 4),          # -30% crash
        np.linspace(70, 100, n - n // 2 - n // 4),
    ]))
    return {t: {"SPY": spy, "GLD": gld}[t] for t in tickers}


def test_backtest_returns_growth_and_chart():
    with patch("backend.services.backtest.fetch_price_history", side_effect=_fake_history):
        result = run_backtest({"SPY": 1.0}, budget=100000, period="1y")
    assert result["final_value"] == pytest.approx(200000, rel=0.01)
    assert result["total_return_pct"] == pytest.approx(100, rel=0.05)
    assert 100 <= len(result["chart"]) <= 130
    assert result["chart"][0]["value"] == pytest.approx(100000, rel=0.01)
    # Real (inflation-adjusted) return should be present and lower than nominal
    assert result["real_return_pct"] is not None
    assert result["real_return_pct"] < result["total_return_pct"]


def test_backtest_reports_honest_drawdown():
    with patch("backend.services.backtest.fetch_price_history", side_effect=_fake_history):
        result = run_backtest({"GLD": 1.0}, budget=100000, period="1y")
    assert result["max_drawdown_pct"] == pytest.approx(-30, abs=1.5)
    assert result["per_asset"]["GLD"]["longest_stagnation_months"] >= 10


def test_stagnation_detector_on_flat_series():
    flat = _series(np.full(252, 100.0))  # 1 year dead flat
    assert _longest_stagnation_months(flat) == pytest.approx(12, abs=0.5)


def test_backtest_endpoint_validates_weights(client):
    res = client.post(
        "/backtest",
        json={"weights": {"SPY": 0.5}, "budget": 10000, "period": "1y"},
    )
    assert res.status_code == 422  # weights don't sum to 1


def test_backtest_endpoint_happy_path(client):
    with patch("backend.services.backtest.fetch_price_history", side_effect=_fake_history):
        res = client.post(
            "/backtest",
            json={"weights": {"SPY": 0.6, "GLD": 0.4}, "budget": 50000, "period": "1y"},
        )
    assert res.status_code == 200
    body = res.json()
    assert body["start_value"] == 50000
    assert "SPY" in body["per_asset"] and "GLD" in body["per_asset"]
