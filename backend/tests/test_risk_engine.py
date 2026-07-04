"""
Tests for the risk engine.
10 scenarios covering all user types described in Phase 5.
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
    return RiskProfileAnswers(**defaults)


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
    assert result.label == "Conservative"


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
    assert result.label == "Moderate"


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
    assert result.label == "Aggressive"


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
    assert result.label in {"Conservative", "Moderate", "Growth", "Aggressive"}
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
