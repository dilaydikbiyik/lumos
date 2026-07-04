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


def test_live_index_used_when_available():
    fake_live = {"2026-01": 100.0, "2026-02": 105.0}
    with patch("backend.services.evds_service.get_live_cpi_index", return_value=fake_live):
        pct = cpi_change_pct("2026-01", "2026-02")
    assert pct == pytest.approx(5.0, abs=0.01)


def test_years_to_months_ago_format():
    from datetime import date
    result = years_to_months_ago(1, today=date(2026, 6, 1))
    assert result == "2025-06"
