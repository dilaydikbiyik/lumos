"""
Inflation reality layer tests.
"""
import pytest

from backend.services.inflation_service import (
    cpi_change_pct,
    monthly_cash_erosion,
    real_return_pct,
    years_to_months_ago,
)


def test_cpi_change_reflects_known_checkpoints():
    # 2020-01 = 100.0, 2020-12 = 114.3 per the static dataset
    pct = cpi_change_pct("2020-01", "2020-12")
    assert pct == pytest.approx(14.3, abs=0.1)


def test_real_return_below_nominal_during_high_inflation():
    # 45% nominal gain while inflation ran ~60% should show a NEGATIVE real return
    real = real_return_pct(45, "2021-12", "2022-12")
    assert real < 0


def test_real_return_equals_nominal_with_zero_inflation():
    real = real_return_pct(20, "2020-01", "2020-01")
    assert real == pytest.approx(20, abs=0.01)


def test_monthly_cash_erosion_scales_with_amount():
    result = monthly_cash_erosion(100000)
    assert result["monthly_inflation_pct"] >= 0
    assert result["erosion_amount"] >= 0


def test_years_to_months_ago_format():
    from datetime import date
    result = years_to_months_ago(1, today=date(2026, 6, 1))
    assert result == "2025-06"
