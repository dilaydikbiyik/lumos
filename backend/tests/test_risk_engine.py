"""
Tests for the risk engine.
10 scenarios covering the persona types from tests/e2e/scenarios.json.
"""

from backend.schemas.user_profile import RiskProfileAnswers
from backend.services.risk_engine import compute_risk_score


def _answers(**kwargs) -> RiskProfileAnswers:
    defaults = {
        "budget": 100_000,
        "time_horizon": "medium",
        "loss_tolerance": "medium",
        "goal": "growth",
        "experience": "beginner",
    }
    defaults.update(kwargs)
    return RiskProfileAnswers(**defaults)  # type: ignore


# ── Score bounds ───────────────────────────────────────────────────────────────

def test_score_is_between_1_and_10():
    for scenario in [
        _answers(time_horizon="short", loss_tolerance="low", goal="preservation", experience="none"),
        _answers(time_horizon="long",  loss_tolerance="high", goal="speculation", experience="advanced"),
    ]:
        result = compute_risk_score(scenario)
        assert 1 <= result.risk_score <= 10


# ── Conservative user ─────────────────────────────────────────────────────────

def test_conservative_profile_low_score():
    answers = _answers(
        time_horizon="short",
        loss_tolerance="low",
        goal="preservation",
        experience="none",
    )
    result = compute_risk_score(answers)
    assert result.risk_score <= 3
    assert result.label == "Muhafazakâr"


# ── Moderate user ─────────────────────────────────────────────────────────────

def test_moderate_profile_mid_score():
    answers = _answers(
        time_horizon="medium",
        loss_tolerance="medium",
        goal="income",
        experience="beginner",
    )
    result = compute_risk_score(answers)
    assert 3 < result.risk_score <= 6
    assert result.label == "Dengeli"


# ── Aggressive user ───────────────────────────────────────────────────────────

def test_aggressive_profile_high_score():
    answers = _answers(
        time_horizon="long",
        loss_tolerance="high",
        goal="speculation",
        experience="advanced",
    )
    result = compute_risk_score(answers)
    assert result.risk_score >= 8
    assert result.label == "Atılgan"


# ── Short-term user ───────────────────────────────────────────────────────────

def test_short_term_lowers_score():
    long_score = compute_risk_score(
        _answers(time_horizon="long", loss_tolerance="high", goal="growth", experience="intermediate")
    ).risk_score
    short_score = compute_risk_score(
        _answers(time_horizon="short", loss_tolerance="high", goal="growth", experience="intermediate")
    ).risk_score
    assert short_score < long_score


# ── Retirement user ───────────────────────────────────────────────────────────

def test_retirement_profile():
    answers = _answers(
        time_horizon="long",
        loss_tolerance="low",
        goal="income",
        experience="beginner",
    )
    result = compute_risk_score(answers)
    assert result.risk_score < 6  # income + low tolerance = moderate at best


# ── Response structure ────────────────────────────────────────────────────────

def test_response_has_all_fields():
    result = compute_risk_score(_answers())
    assert result.risk_score is not None
    assert result.label in {"Muhafazakâr", "Dengeli", "Büyüme Odaklı", "Atılgan"}
    assert len(result.summary) > 10
    assert result.answers is not None


# ── Determinism ───────────────────────────────────────────────────────────────

def test_same_input_gives_same_output():
    a = _answers(time_horizon="medium", loss_tolerance="medium", goal="growth", experience="intermediate")
    assert compute_risk_score(a).risk_score == compute_risk_score(a).risk_score


# ── Experience levels ─────────────────────────────────────────────────────────

def test_advanced_experience_raises_score():
    low = compute_risk_score(_answers(experience="none")).risk_score
    high = compute_risk_score(_answers(experience="advanced")).risk_score
    assert high > low


# ── Budget does not affect score ──────────────────────────────────────────────

def test_budget_does_not_affect_score():
    a = compute_risk_score(_answers(budget=10_000)).risk_score
    b = compute_risk_score(_answers(budget=10_000_000)).risk_score
    assert a == b


# ── Age modifier ──────────────────────────────────────────────────────────────

def test_young_user_gets_higher_score():
    young = compute_risk_score(_answers(age=25)).risk_score
    mid = compute_risk_score(_answers()).risk_score   # no age
    assert young >= mid


def test_older_user_gets_lower_score():
    old = compute_risk_score(_answers(age=60)).risk_score
    mid = compute_risk_score(_answers()).risk_score
    assert old <= mid


def test_age_modifier_capped_score_stays_in_bounds():
    # Very old + already aggressive profile must not go below 1
    result = compute_risk_score(
        _answers(age=80, time_horizon="short", loss_tolerance="low",
                 goal="preservation", experience="none")
    )
    assert 1 <= result.risk_score <= 10


# ── Income stability modifier ─────────────────────────────────────────────────

def test_irregular_income_lowers_score():
    stable = compute_risk_score(_answers(income_stability="stable")).risk_score
    irregular = compute_risk_score(_answers(income_stability="irregular")).risk_score
    assert irregular < stable


def test_variable_income_between_stable_and_irregular():
    stable = compute_risk_score(_answers(income_stability="stable")).risk_score
    variable = compute_risk_score(_answers(income_stability="variable")).risk_score
    irregular = compute_risk_score(_answers(income_stability="irregular")).risk_score
    assert irregular <= variable <= stable


def test_modifier_combo_capped_at_bounds():
    # young + stable = max +1.5 modifier cap — still ≤ 10
    r = compute_risk_score(
        _answers(age=22, income_stability="stable",
                 time_horizon="long", loss_tolerance="high",
                 goal="speculation", experience="advanced")
    )
    assert r.risk_score <= 10


def test_summary_mentions_age_when_provided():
    r = compute_risk_score(_answers(age=60))
    assert "yaş" in r.summary.lower() or "güncellendi" in r.summary.lower() or "koruma" in r.summary.lower()


def test_summary_mentions_income_when_irregular():
    r = compute_risk_score(_answers(income_stability="irregular"))
    assert "gelir" in r.summary.lower() or "düzensiz" in r.summary.lower()
