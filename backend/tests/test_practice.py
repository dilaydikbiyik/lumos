"""
Practice mode (sanal portföy) tests — market data mocked.
"""
import numpy as np
import pandas as pd
import pytest
from unittest.mock import patch

from backend.exceptions import MarketDataError
from backend.services.practice_mode import practice_snapshot

DATES = pd.date_range("2026-05-01", periods=22, freq="B")


def _rising_history(tickers, period="1mo"):
    return {t: pd.Series(np.linspace(100, 110, len(DATES)), index=DATES) for t in tickers}


def _empty_history(tickers, period="1mo"):
    return {}


def test_practice_snapshot_computes_value_and_change():
    with patch("backend.services.practice_mode.fetch_price_history", side_effect=_rising_history):
        result = practice_snapshot({"SPY": 1.0}, virtual_budget=100000)
    assert result["current_value"] > 0
    assert result["weekly_change_pct"] > 0
    assert result["biggest_mover"]["ticker"] == "SPY"


def test_practice_snapshot_raises_without_data():
    with patch("backend.services.practice_mode.fetch_price_history", side_effect=_empty_history):
        with pytest.raises(MarketDataError):
            practice_snapshot({"SPY": 1.0})


def test_practice_endpoint(client):
    with patch("backend.services.practice_mode.fetch_price_history", side_effect=_rising_history):
        res = client.post("/practice/snapshot", json={"weights": {"SPY": 1.0}})
    assert res.status_code == 200
    assert res.json()["virtual_budget"] == 100000.0
