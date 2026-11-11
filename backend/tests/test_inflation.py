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
    # TÜİK TÜFE, January to December 2020, per the bundled static dataset
    with _NO_LIVE:
        pct = cpi_change_pct("2020-01", "2020-12")
    assert pct == pytest.approx(13.07, abs=0.1)


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


def test_the_inflation_window_spans_exactly_the_years_asked():
    """Five years of prices were deflated by 59 months of CPI: the window
    ended at 'this month', which snapped back to the last published one."""
    from unittest.mock import patch

    from backend.services import inflation_service

    with patch.object(inflation_service, "index_as_of", return_value="2026-10"):
        assert inflation_service.inflation_window(5, "TR") == ("2021-10", "2026-10")
        assert inflation_service.inflation_window(1, "TR") == ("2025-10", "2026-10")
    with patch.object(inflation_service, "index_as_of", return_value="2026-01"):
        assert inflation_service.inflation_window(3, "TR") == ("2023-01", "2026-01")


def test_a_missing_month_lengthens_the_span_not_the_rate():
    """The US index has no October 2025; 'a year ago' snapped to September
    and thirteen months of inflation were reported as the annual rate."""
    from unittest.mock import patch

    from backend.services import inflation_service

    index = {f"2025-{m:02d}": 100.0 * 1.003 ** (m - 1) for m in range(1, 13) if m != 10}
    index.update({f"2026-{m:02d}": 100.0 * 1.003 ** (11 + m) for m in range(1, 11)})
    true_annual = (1.003 ** 12 - 1) * 100
    with patch.object(inflation_service, "_get_index", lambda market="TR": index):
        assert inflation_service.trailing_annual_inflation_pct("US") == pytest.approx(true_annual, abs=0.02)
        monthly = inflation_service.monthly_cash_erosion(10_000, market="US")["monthly_inflation_pct"]
    assert monthly == pytest.approx(0.3, abs=0.01)


def test_long_run_housing_growth_is_not_last_years():
    from backend.services.assumptions import _annualized_from_index

    quarters = [f"{y}-Q{q}" for y in range(2015, 2027) for q in (1, 2, 3, 4)][:46]
    index = {q: 100 * 1.01 ** i for i, q in enumerate(quarters)}      # +1% a quarter
    index[quarters[-1]] = index[quarters[-5]] * 1.006                 # a flat last year
    assert _annualized_from_index(index) == pytest.approx(3.7, abs=0.2)
    assert _annualized_from_index({q: index[q] for q in quarters[-12:]}) is None   # under five years
