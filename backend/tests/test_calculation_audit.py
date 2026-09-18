"""
Calculation audit — every number re-derived from first principles.

These tests deliberately do NOT reuse the app's own helpers to decide what
"correct" means; that would only prove the code agrees with itself. Each one
computes the answer independently (an amortisation schedule, a forward
simulation, numpy percentiles) and compares.

Written after an end-to-end audit found six real defects:
  * the defensive sleeve silently shrank when one of its legs was pruned as
    dust, so a profile told "31% stays safe" received 9%;
  * the rounding remainder was dumped on the largest position, publishing a
    45.01% holding next to a stated 45% cap;
  * the formula shown to users omitted the <10% cliff, so it did not
    reproduce the portfolio it was explaining;
  * banker's rounding printed a score one tenth BELOW the sum of its own
    published parts;
  * cash erosion multiplied the balance by the inflation rate, overstating
    the real loss;
  * an aggressive portfolio held VNQ and SCHH together — ~44% in one real
    exposure, the exact thing the app's own copy says it avoids.
"""

from unittest.mock import patch

import numpy as np
import pytest

from backend.schemas.user_profile import RiskProfileAnswers
from backend.services import goal_planner, inflation_service
from backend.services.portfolio_engine import (
    MAX_POSITION_PCT, MIN_WEIGHT_PCT, build_portfolio,
)
from backend.services.projection import _band
from backend.services.rent_vs_buy import _mortgage_payment, compare_rent_vs_buy
from backend.services.risk_engine import _WEIGHTS, compute_risk_score

RISK_SCORES = [round(x * 0.5, 1) for x in range(2, 21)]
BUDGETS = (5_000, 50_000, 200_000, 1_000_000)


# ── Mortgage ──────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("loan,apr,years", [
    (1_000_000, 39.0, 10), (500_000, 6.5, 30), (300_000, 3.8, 20), (250_000, 0.0, 15),
])
def test_annuity_payment_amortises_the_loan_to_zero(loan, apr, years):
    """The only real test of a payment formula: run the schedule."""
    rate, months = apr / 100 / 12, years * 12
    payment = _mortgage_payment(loan, rate, months)

    balance = loan
    for _ in range(months):
        balance = balance + balance * rate - payment

    assert abs(balance) < max(loan * 1e-9, 0.01)


def test_zero_rate_loan_is_just_principal_over_months():
    assert _mortgage_payment(120_000, 0.0, 120) == pytest.approx(1000.0)


# ── Real return ───────────────────────────────────────────────────────────────

def test_fisher_real_return_is_exact():
    cpi = {"2024-01": 100.0, "2025-01": 160.0}   # 60% inflation
    with patch.object(inflation_service, "_get_index", lambda market="TR": cpi):
        # (1.45 / 1.60 - 1) * 100
        assert inflation_service.real_return_pct(45.0, "2024-01", "2025-01") == pytest.approx(-9.375, abs=0.01)
        assert inflation_service.real_return_pct(60.0, "2024-01", "2025-01") == pytest.approx(0.0, abs=0.01)
        assert inflation_service.real_return_pct(0.0, "2024-01", "2025-01") == pytest.approx(-37.5, abs=0.01)


def test_cash_erosion_is_the_purchasing_power_lost_not_the_price_rise():
    """
    After a month of 3% inflation, 10,000 buys what 9,708.74 bought: 291.26
    of value is gone, not 300. The old formula multiplied the balance by the
    rate, overstating the loss — slightly, but always in the same direction,
    in the one number whose entire point is being the honest one.
    """
    cpi = {"2025-01": 100.0, "2025-02": 103.0}
    with patch.object(inflation_service, "_get_index", lambda market="TR": cpi):
        result = inflation_service.monthly_cash_erosion(10_000)

    assert result["erosion_amount"] == pytest.approx(10_000 - 10_000 / 1.03, abs=0.01)
    assert result["erosion_amount"] < 10_000 * 0.03


# ── Portfolio construction ────────────────────────────────────────────────────

@pytest.mark.parametrize("score", RISK_SCORES)
def test_weights_sum_to_one_and_respect_both_bounds(score):
    for budget in BUDGETS:
        portfolio = build_portfolio(risk_score=score, budget=budget, market="TR")
        weights = [a.weight for a in portfolio.allocations]

        assert sum(weights) == pytest.approx(1.0, abs=1e-9), (score, budget)
        # The cap is published in metadata, so it has to hold after the
        # rounding remainder is placed — not just before.
        assert max(weights) <= MAX_POSITION_PCT / 100 + 1e-9, (score, budget)
        assert min(weights) >= MIN_WEIGHT_PCT / 100 - 1e-9, (score, budget)


@pytest.mark.parametrize("score", RISK_SCORES)
def test_defensive_share_matches_the_formula_shown_to_the_user(score):
    """
    The allocation card prints the formula and invites the reader to check
    it. Dust-pruning one leg of the sleeve used to redistribute its weight
    across the growth assets, so the printed number and the real portfolio
    disagreed by up to four points.
    """
    portfolio = build_portfolio(risk_score=score, budget=1_000_000, market="TR")
    actual = sum(a.weight for a in portfolio.allocations
                 if a.category in ("cash", "bond")) * 100

    expected = max(0.0, min(60.0, 60 - 5.5 * score))
    if expected < 10.0:      # the documented cliff
        expected = 0.0

    assert actual == pytest.approx(expected, abs=0.6), (score, actual, expected)


def test_defensive_share_never_rises_as_risk_rises():
    shares = [
        sum(a.weight for a in build_portfolio(risk_score=s, budget=1_000_000,
                                              market="TR").allocations
            if a.category in ("cash", "bond"))
        for s in RISK_SCORES
    ]
    assert shares == sorted(shares, reverse=True), shares


def test_published_formula_describes_the_cliff_it_actually_applies():
    """A formula that does not reproduce the portfolio is worse than none."""
    from backend.i18n import t

    for lang in ("tr", "en", "de"):
        text = t("formula.allocation", lang)
        assert "10" in text and "45" in text and "5" in text, lang


# ── Risk engine ───────────────────────────────────────────────────────────────

def test_weights_are_a_partition():
    assert sum(_WEIGHTS.values()) == pytest.approx(1.0)


def test_score_equals_the_weighted_sum_of_its_published_parts():
    answers = RiskProfileAnswers(budget=100_000, time_horizon="long",
                                 loss_tolerance="high", goal="speculation",
                                 experience="advanced")
    profile = compute_risk_score(answers)
    parts = sum(f.contribution for f in profile.factors)

    # 9*.25 + 9*.30 + 10*.25 + 9*.20 = 9.25, shown to one decimal.
    assert parts == pytest.approx(9.25, abs=0.001)
    assert profile.risk_score == pytest.approx(round(9.3, 1), abs=0.001)


def test_rounding_never_prints_a_score_below_the_sum_of_its_parts():
    """
    Python's round() is banker's rounding: round(9.25, 1) is 9.2. The card
    shows every contribution and invites the reader to add them up, so a
    score one tenth BELOW its own parts is the clearest way to look wrong.
    """
    for horizon in ("short", "medium", "long"):
        for tolerance in ("low", "medium", "high"):
            for goal in ("preservation", "income", "growth", "speculation"):
                for experience in ("none", "beginner", "intermediate", "advanced"):
                    profile = compute_risk_score(RiskProfileAnswers(
                        budget=100_000, time_horizon=horizon,
                        loss_tolerance=tolerance, goal=goal, experience=experience,
                    ))
                    parts = sum(f.contribution for f in profile.factors)
                    if 1.0 < parts < 10.0:     # not clamped
                        assert profile.risk_score >= parts - 1e-9, (parts, profile.risk_score)
                        assert profile.risk_score - parts <= 0.0501, (parts, profile.risk_score)


# ── Goal planner ──────────────────────────────────────────────────────────────

@pytest.mark.parametrize("target,years,apr,start", [
    (300_000, 5, 20.0, 0), (1_000_000, 10, 8.0, 50_000), (50_000, 3, 0.0, 0),
])
def test_required_contribution_actually_reaches_the_target(target, years, apr, start):
    """Forward-simulate the plan the planner returns."""
    monthly = goal_planner.required_monthly_contribution(
        target_amount=target, years=years, annual_growth_pct=apr,
        current_savings=start,
    )["monthly_contribution"]

    rate = (1 + apr / 100) ** (1 / 12) - 1
    balance = start
    for _ in range(years * 12):
        balance = balance * (1 + rate) + monthly

    assert balance == pytest.approx(target, rel=1e-4)


# ── Rent vs buy ───────────────────────────────────────────────────────────────

def test_rent_vs_buy_is_internally_consistent():
    result = compare_rent_vs_buy(
        down_payment=1_000_000, monthly_rent=30_000, years=10,
        home_price=5_000_000, housing_annual_growth_pct=30.0,
        portfolio_annual_growth_pct=35.0, rent_annual_growth_pct=25.0,
        mortgage_annual_rate_pct=39.0, mortgage_term_years=10, market="TR",
    )
    assumptions = result["assumptions"]

    assert result["monthly_mortgage"] == pytest.approx(
        _mortgage_payment(4_000_000, 0.39 / 12, 120), abs=0.05)
    assert result["buy"]["home_value"] == pytest.approx(5_000_000 * 1.30 ** 10, rel=1e-6)
    # Horizon equals term, so the loan must be gone.
    assert result["buy"]["remaining_loan"] == pytest.approx(0.0, abs=1.0)

    loan = result["loan"]
    assert loan["interest_over_full_term"] == pytest.approx(
        loan["total_over_full_term"] - loan["principal"], abs=1.0)

    expected_costs = 5_000_000 * (
        assumptions["title_deed_fee_pct"] + assumptions["agency_commission_with_vat_pct"]
    ) / 100
    assert result["buy"]["purchase_costs"] == pytest.approx(expected_costs, abs=1.0)

    inflation = assumptions["annual_inflation_pct"]
    assert result["buy"]["net_worth_real"] == pytest.approx(
        result["buy"]["net_worth"] / (1 + inflation / 100) ** 10, rel=1e-6)


def test_with_no_growth_and_no_interest_equity_is_exactly_the_home_price():
    result = compare_rent_vs_buy(
        down_payment=1_000_000, monthly_rent=1.0, years=10, home_price=5_000_000,
        housing_annual_growth_pct=0.0, portfolio_annual_growth_pct=0.0,
        rent_annual_growth_pct=0.0, mortgage_annual_rate_pct=0.0,
        mortgage_term_years=10, market="TR",
    )
    assert result["buy"]["equity"] == pytest.approx(5_000_000, abs=1.0)


def test_down_payment_cannot_exceed_the_home_price():
    result = compare_rent_vs_buy(down_payment=9_000_000, monthly_rent=30_000,
                                 years=5, home_price=5_000_000, market="TR")
    assert result["home_price"] == 5_000_000
    assert result["buy"]["remaining_loan"] >= 0.0


# ── Scenario bands ────────────────────────────────────────────────────────────

def test_band_percentiles_match_numpy_and_stay_ordered():
    returns = [i / 100 for i in range(-50, 151)]
    band = _band(returns, 10_000)
    p10, p50, p90 = np.percentile(np.array(returns), [10, 50, 90])

    assert band["pessimistic"]["return_pct"] == pytest.approx(p10 * 100, abs=0.05)
    assert band["typical"]["return_pct"] == pytest.approx(p50 * 100, abs=0.05)
    assert band["optimistic"]["return_pct"] == pytest.approx(p90 * 100, abs=0.05)
    assert band["typical"]["value"] == pytest.approx(10_000 * (1 + p50), abs=0.01)
    assert (band["pessimistic"]["value"] <= band["typical"]["value"]
            <= band["optimistic"]["value"])
