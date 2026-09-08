"""
Inflation reality layer tests.

cpi tests pin the data source per test: static-fallback tests patch the
live EVDS lookup to None; live-source behavior is covered separately in
test_region_intelligence's fetch_series test.
"""
import pytest
from unittest.mock import patch

from backend.services.inflation_service import (
    cpi_change_pct,
    monthly_cash_erosion,
    real_return_pct,
    years_to_months_ago,
)

_NO_LIVE = patch("backend.services.evds_service.get_live_cpi_index", return_value=None)


def test_cpi_change_reflects_static_checkpoints_on_fallback():
    # 2020-01 = 100.0, 2020-12 = 114.3 per the bundled static dataset
    with _NO_LIVE:
        pct = cpi_change_pct("2020-01", "2020-12")
    assert pct == pytest.approx(14.3, abs=0.1)


def test_real_return_below_nominal_during_high_inflation():
    # 45% nominal gain while inflation ran far higher -> NEGATIVE real return
    # (true in both the static dataset and live EVDS data for 2022)
    real = real_return_pct(45, "2021-12", "2022-12")
    assert real < 0


def test_real_return_equals_nominal_with_zero_inflation():
    real = real_return_pct(20, "2020-01", "2020-01")
    assert real == pytest.approx(20, abs=0.01)


def test_monthly_cash_erosion_scales_with_amount():
    result = monthly_cash_erosion(100000)
    assert result["monthly_inflation_pct"] >= 0
    assert result["erosion_amount"] >= 0


def test_fresher_live_index_wins_over_the_bundled_file():
    # Live data that reaches further forward than the bundled snapshot
    fake_live = {"2099-01": 100.0, "2099-02": 105.0}
    with patch("backend.services.evds_service.get_live_cpi_index", return_value=fake_live):
        pct = cpi_change_pct("2099-01", "2099-02")
    assert pct == pytest.approx(5.0, abs=0.01)


def test_a_stalled_live_series_loses_to_a_fresher_bundled_file():
    """
    "Live always wins" is wrong when the upstream series stalls. TCMB stopped
    publishing the CPI series this app used at 2026-01 while the repo already
    carried data through 2026-06, so preferring live served numbers eight
    months older than what was on disk.
    """
    from backend.services.inflation_service import _STATIC_INDEX, _get_index

    stalled = {"2020-01": 100.0, "2020-02": 101.0}
    with patch("backend.services.evds_service.get_live_cpi_index", return_value=stalled):
        chosen = _get_index("TR")

    assert max(chosen) == max(_STATIC_INDEX)
    assert max(chosen) > max(stalled)


def test_index_as_of_reports_the_month_actually_covered():
    """A rate with no 'as of' date is a claim about today that may be stale."""
    from backend.services.inflation_service import index_as_of

    fake_live = {"2099-01": 100.0, "2099-05": 110.0}
    with patch("backend.services.evds_service.get_live_cpi_index", return_value=fake_live):
        assert index_as_of("TR") == "2099-05"


def test_years_to_months_ago_format():
    from datetime import date
    result = years_to_months_ago(1, today=date(2026, 6, 1))
    assert result == "2025-06"
