"""
Debt before investing — the arithmetic, and when to stay quiet about it.
"""

import pytest

from backend.services import debt_check
from backend.schemas.user_profile import RiskProfileAnswers
from backend.services.risk_engine import compute_risk_score


def test_no_debt_says_nothing():
    assert debt_check.check(None, 100_000) is None
    assert debt_check.check(0, 100_000) is None


def test_trivial_debt_does_not_interrupt():
    """Blocking a first investment over pocket change helps nobody."""
    assert debt_check.check(1_000, 100_000) is None


def test_repayment_beats_investing():
    r = debt_check.check(40_000, 100_000)
    assert r is not None
    # Card interest compounds well above any portfolio expectation
    assert r["debt_annual_pct"] > r["portfolio_annual_pct"]
    assert r["advantage"] > 0
    assert r["interest_avoided"] > r["investment_gain"]


def test_advantage_is_the_difference():
    r = debt_check.check(40_000, 100_000)
    assert r["advantage"] == pytest.approx(
        r["interest_avoided"] - r["investment_gain"], abs=0.01
    )


def test_budget_smaller_than_debt_applies_only_the_budget():
    r = debt_check.check(80_000, 20_000)
    assert r["applied"] == 20_000
    assert r["covers_debt"] is False
    assert r["leftover_after_repayment"] == 0


def test_leftover_reported_when_budget_covers_debt():
    r = debt_check.check(30_000, 50_000)
    assert r["covers_debt"] is True
    assert r["leftover_after_repayment"] == 20_000


def test_monthly_rate_compounds_to_annual():
    # 4.25%/month compounds to well over the naive 51%
    assert debt_check.annual_rate_from_monthly(4.25) > 60


def _answers(**over):
    base = dict(
        budget=100_000, time_horizon="long", loss_tolerance="medium",
        goal="growth", experience="none",
    )
    base.update(over)
    return RiskProfileAnswers(**base)


def test_profile_carries_debt_check_when_debt_reported():
    profile = compute_risk_score(_answers(high_interest_debt=40_000))
    assert profile.debt_check is not None
    assert profile.debt_check["debt"] == 40_000


def test_profile_has_no_debt_check_without_debt():
    assert compute_risk_score(_answers()).debt_check is None
    assert compute_risk_score(_answers(high_interest_debt=0)).debt_check is None
