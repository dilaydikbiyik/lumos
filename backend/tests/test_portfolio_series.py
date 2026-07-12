"""
Realism guard tests for the shared portfolio series helper.

The bug it prevents: when yfinance returns data for only SOME tickers,
the old code left the series starting below 1.0 while measuring returns
against the full budget — a doubled surviving asset could render as a
massive LOSS ("100.000 TL -> 40 TL" class of nonsense).
"""
import numpy as np
import pandas as pd
import pytest

from backend.exceptions import MarketDataError
from backend.services.portfolio_series import build_normalized_series


def _series(multipliers):
    """A price series that starts at 100 and ends at 100 * final multiplier."""
    idx = pd.date_range("2020-01-01", periods=len(multipliers), freq="D")
    return pd.Series(np.array(multipliers) * 100.0, index=idx)


def test_full_coverage_series_starts_at_one_and_tracks_weights():
    # Two assets, 50/50; one doubles, one flat -> portfolio ends at 1.5x
    history = {"A": _series([1.0, 1.5, 2.0]), "B": _series([1.0, 1.0, 1.0])}
    s = build_normalized_series(history, {"A": 0.5, "B": 0.5})
    assert s.iloc[0] == pytest.approx(1.0)
    assert s.iloc[-1] == pytest.approx(1.5)  # (2.0*0.5 + 1.0*0.5)


def test_partial_coverage_renormalizes_surviving_weights():
    # Intended 20% A / 80% B, but B has NO data. A doubled.
    # Renormalized to 100% A, so the series must double — NOT show a loss.
    history = {"A": _series([1.0, 1.5, 2.0]), "B": None}
    # coverage = 0.2 which is below the 0.8 floor -> must refuse, not lie
    with pytest.raises(MarketDataError):
        build_normalized_series(history, {"A": 0.2, "B": 0.8})


def test_high_coverage_renormalizes_instead_of_shrinking():
    # 85% A (survives, doubles) + 15% C (missing) -> above 0.8 floor.
    # Surviving weight renormalized to 1.0, so series doubles.
    history = {"A": _series([1.0, 1.5, 2.0]), "C": None}
    s = build_normalized_series(history, {"A": 0.85, "C": 0.15})
    assert s.iloc[0] == pytest.approx(1.0)   # starts at budget, not 0.85
    assert s.iloc[-1] == pytest.approx(2.0)  # a doubling reads as a doubling


def test_no_data_raises():
    with pytest.raises(MarketDataError):
        build_normalized_series({"A": None, "B": None}, {"A": 0.5, "B": 0.5})
