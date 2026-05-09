"""
Risk score engine.

Maps the 5-question risk profile answers to a score between 1 and 10.

Scoring logic:
  Each dimension contributes a sub-score; the weighted average gives the final score.

  Dimension         Weight
  ──────────────    ──────
  time_horizon       25 %
  loss_tolerance     30 %
  goal               25 %
  experience         20 %

Budget is NOT included in the formula (it affects portfolio size, not risk tolerance).
"""

from backend.models.user_profile import RiskProfileAnswers, RiskProfileResponse

_TIME_HORIZON_SCORES = {"short": 2, "medium": 5, "long": 9}
_LOSS_TOLERANCE_SCORES = {"low": 2, "medium": 5, "high": 9}
_GOAL_SCORES = {
    "preservation": 1,
    "income": 4,
    "growth": 7,
    "speculation": 10,
}
_EXPERIENCE_SCORES = {"none": 1, "beginner": 3, "intermediate": 6, "advanced": 9}

_WEIGHTS = {
    "time_horizon": 0.25,
    "loss_tolerance": 0.30,
    "goal": 0.25,
    "experience": 0.20,
}


def _label(score: float) -> str:
    if score <= 3:
        return "Conservative"
    elif score <= 6:
        return "Moderate"
    elif score <= 8:
        return "Growth"
    else:
        return "Aggressive"


def compute_risk_score(answers: RiskProfileAnswers) -> RiskProfileResponse:
    """
    Compute a 1-10 risk score from the 5-question answers.

    Args:
        answers: Validated RiskProfileAnswers instance.

    Returns:
        RiskProfileResponse with score, label, and summary.
    """
    raw = (
        _TIME_HORIZON_SCORES[answers.time_horizon] * _WEIGHTS["time_horizon"]
        + _LOSS_TOLERANCE_SCORES[answers.loss_tolerance] * _WEIGHTS["loss_tolerance"]
        + _GOAL_SCORES[answers.goal] * _WEIGHTS["goal"]
        + _EXPERIENCE_SCORES[answers.experience] * _WEIGHTS["experience"]
    )
    score = round(min(max(raw, 1.0), 10.0), 1)
    label = _label(score)

    summary = (
        f"Your risk score is {score}/10 ({label}). "
        f"Based on your {answers.time_horizon} time horizon, "
        f"{answers.loss_tolerance} loss tolerance, "
        f"and {answers.goal} goal, Lumos will build a portfolio tailored to your profile."
    )

    return RiskProfileResponse(
        risk_score=score,
        label=label,
        summary=summary,
        answers=answers,
    )
