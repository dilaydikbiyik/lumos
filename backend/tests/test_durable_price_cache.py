"""Price history survives the durable tier's JSON round trip."""
import json

import pandas as pd
import pytest

from backend.services import cache_store


def test_price_series_round_trip_through_json():
    days = pd.bdate_range("2024-01-01", periods=5, tz="America/New_York")
    value = {"SPY": pd.Series([1.0, 2.5, float("nan"), 4.0, 5.25], index=days)}
    stored = json.loads(json.dumps({"v": cache_store._encode(value)}))["v"]
    back = cache_store._decode(stored)
    assert list(back) == ["SPY"] and len(back["SPY"]) == 4
    assert back["SPY"].iloc[-1] == pytest.approx(5.25)
    assert str(back["SPY"].index[0].date()) == "2024-01-01"
    assert (back["SPY"] / back["SPY"].shift(1)).dropna().iloc[0] == pytest.approx(2.5)


def test_ordinary_values_are_untouched():
    for value in ({"a": 1}, [1, 2], "x", None, {"SPY": [1, 2]}):
        assert cache_store._decode(cache_store._encode(value)) == value
