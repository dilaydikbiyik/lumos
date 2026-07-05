"""
Risk score engine.

Maps the risk profile answers to a score between 1 and 10.

Scoring logic:
  Each dimension contributes a sub-score; the weighted average gives the final score.

  Dimension           Weight   Notes
  ──────────────────  ──────   ────────────────────────────────────────────────────
  time_horizon         25 %
  loss_tolerance       30 %
  goal                 25 %
  experience           20 %

  Optional modifiers (additive, capped at ±1.5):
  age                         ≥55 → −0.5 (preservation priority increases with age)
                              ≤30 → +0.5 (longer runway, more risk capacity)
  income_stability            irregular → −1.0   variable → −0.4   stable → 0

Budget is NOT included in the formula (it affects portfolio size, not risk tolerance).
"""

from backend.schemas.user_profile import RiskProfileAnswers, RiskProfileResponse

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

_INCOME_MODIFIER = {
    "stable": 0.0,
    "variable": -0.4,
    "irregular": -1.0,
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


def _age_modifier(age: int | None) -> float:
    """Older users need more capital preservation; younger users have longer runway."""
    if age is None:
        return 0.0
    if age >= 55:
        return -0.5
    if age <= 30:
        return 0.5
    return 0.0


def compute_risk_score(answers: RiskProfileAnswers) -> RiskProfileResponse:
    """
    Compute a 1-10 risk score from the profile answers.

    Args:
        answers: Validated RiskProfileAnswers instance.

    Returns:
        RiskProfileResponse with score, label, and Turkish summary.
    """
    base = (
        _TIME_HORIZON_SCORES[answers.time_horizon] * _WEIGHTS["time_horizon"]
        + _LOSS_TOLERANCE_SCORES[answers.loss_tolerance] * _WEIGHTS["loss_tolerance"]
        + _GOAL_SCORES[answers.goal] * _WEIGHTS["goal"]
        + _EXPERIENCE_SCORES[answers.experience] * _WEIGHTS["experience"]
    )

    # Optional modifiers — each capped so they can't dominate
    modifier = _age_modifier(answers.age)
    if answers.income_stability:
        modifier += _INCOME_MODIFIER[answers.income_stability]
    modifier = max(-1.5, min(1.5, modifier))

    score = round(min(max(base + modifier, 1.0), 10.0), 1)
    label = _label(score)

    # Modifier context for summary
    modifier_note = ""
    if answers.age and answers.age >= 55:
        modifier_note += " Yaşın göz önünde bulunduruldu — koruma ağırlığı artırıldı."
    elif answers.age and answers.age <= 30:
        modifier_note += " Genç yaşın uzun bir yatırım ufku sağlıyor — hafifçe yukarı güncellendi."
    if answers.income_stability == "irregular":
        modifier_note += " Düzensiz geliriniz risk kapasiteni sınırlıyor."
    elif answers.income_stability == "variable":
        modifier_note += " Değişken geliriniz hafifçe dikkate alındı."

    summary = (
        f"Risk skoru {score}/10 ({label}). "
        f"{answers.time_horizon.capitalize()} yatırım ufku, "
        f"{answers.loss_tolerance} kayıp toleransı ve "
        f"{answers.goal} hedefi temel alındı.{modifier_note}"
    )

    return RiskProfileResponse(
        risk_score=score,
        label=label,
        summary=summary,
        answers=answers,
    )
