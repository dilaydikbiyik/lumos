"""
Returns in the reader's currency — the defect and the guard.

A Turkish five-year backtest summed SPY's dollar return with the BIST 100's
lira return and deflated the total by Turkish inflation: -62% real. Every
foreign series is now converted at the daily rate before it is combined.
"""
from unittest.mock import patch

import pandas as pd
import pytest


def _days(n, start, end):
    idx = pd.bdate_range("2021-01-04", periods=n)
    return pd.Series([start + (end - start) * i / (n - 1) for i in range(n)], index=idx)


def test_a_dollar_series_is_converted_for_a_lira_reader():
    from backend.services import fx_history

    spy = _days(100, 100.0, 110.0)          # +10% in dollars
    usdtry = _days(100, 10.0, 20.0)          # the lira halves
    with patch.object(fx_history, "fetch_price_history", return_value={"USDTRY=X": usdtry}):
        out = fx_history.in_home_currency({"SPY": spy}, "TRY", "5y")
    s = out["SPY"]
    assert (s.iloc[-1] / s.iloc[0] - 1) == pytest.approx(1.2, abs=1e-6)   # 1.10 x 2.0


def test_a_home_currency_series_is_untouched_and_a_missing_rate_drops_the_foreign_one():
    from backend.services import fx_history

    bist = _days(50, 100.0, 150.0)
    spy = _days(50, 100.0, 110.0)
    with patch.object(fx_history, "fetch_price_history", return_value={}):
        out = fx_history.in_home_currency({"XU100.IS": bist, "SPY": spy}, "TRY", "5y")
    assert out["XU100.IS"] is bist
    assert "SPY" not in out, "a dollar return must never pass as a lira one"


def test_a_us_reader_gets_dollar_series_as_they_are():
    from backend.services import fx_history

    spy = _days(50, 100.0, 110.0)
    with patch.object(fx_history, "fetch_price_history",
                      side_effect=AssertionError("no rate is needed")):
        out = fx_history.in_home_currency({"SPY": spy}, "USD", "5y")
    assert out["SPY"] is spy


def test_the_turkish_backtest_measures_dollar_assets_in_lira():
    from backend.services import backtest, fx_history

    spy = _days(300, 100.0, 110.0)
    usdtry = _days(300, 10.0, 20.0)
    with patch.object(backtest, "fetch_price_history", return_value={"SPY": spy}), \
         patch.object(fx_history, "fetch_price_history", return_value={"USDTRY=X": usdtry}), \
         patch.object(backtest.inflation_service, "real_return_pct", return_value=None):
        result = backtest.run_backtest({"SPY": 1.0}, 1000.0, "1y", market="TR")
    assert result["total_return_pct"] == pytest.approx(120.0, abs=0.01)
