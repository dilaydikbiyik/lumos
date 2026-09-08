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

from backend.i18n import t
from backend.schemas.user_profile import RiskFactor, RiskProfileAnswers, RiskProfileResponse
from backend.services import debt_check

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


def _label(score: float, lang: str) -> str:
    if score <= 3:
        key = "conservative"
    elif score <= 6:
        key = "balanced"
    elif score <= 8:
        key = "growth"
    else:
        key = "aggressive"
    return t(f"risk.label.{key}", lang)


def _age_modifier(age: int | None) -> float:
    """Older users need more capital preservation; younger users have longer runway."""
    if age is None:
        return 0.0
    if age >= 55:
        return -0.5
    if age <= 30:
        return 0.5
    return 0.0


def _answer_label(dimension: str, value: str, lang: str) -> str:
    return t(f"risk.{dimension}.{value}", lang)


def _goal_in_sentence(goal: str, lang: str) -> str:
    label = _answer_label("goal", goal, lang)
    return label if lang == "de" else label.lower()


def compute_risk_score(answers: RiskProfileAnswers, lang: str = "tr") -> RiskProfileResponse:
    """
    Compute a 1-10 risk score from the profile answers.

    Args:
        answers: Validated RiskProfileAnswers instance.
        lang: Request language — the score is language-independent, the
            sentences explaining it are not.

    Returns:
        RiskProfileResponse with score, label, and a summary in `lang`.
    """
    dimension_scores = {
        "time_horizon": _TIME_HORIZON_SCORES[answers.time_horizon],
        "loss_tolerance": _LOSS_TOLERANCE_SCORES[answers.loss_tolerance],
        "goal": _GOAL_SCORES[answers.goal],
        "experience": _EXPERIENCE_SCORES[answers.experience],
    }
    base = sum(dimension_scores[d] * _WEIGHTS[d] for d in dimension_scores)

    # ── transparent breakdown: where every point comes from ──
    factors = [
        RiskFactor(
            factor=t("risk.factor.weighted", lang,
                     name=t(f"risk.factor.{d}", lang),
                     pct=round(_WEIGHTS[d] * 100)),
            answer=_answer_label(d, getattr(answers, d), lang),
            contribution=round(dimension_scores[d] * _WEIGHTS[d], 2),
            explanation=t(f"risk.why.{d}", lang),
        )
        for d in dimension_scores
    ]

    # Optional modifiers — each capped so they can't dominate
    age_mod = _age_modifier(answers.age)
    income_mod = _INCOME_MODIFIER[answers.income_stability] if answers.income_stability else 0.0
    modifier = max(-1.5, min(1.5, age_mod + income_mod))

    if age_mod != 0 and answers.age is not None:
        factors.append(RiskFactor(
            factor=t("risk.mod.age", lang),
            answer=t("risk.mod.age.answer", lang, age=answers.age),
            contribution=age_mod,
            explanation=t("risk.mod.age.older" if age_mod < 0
                          else "risk.mod.age.younger", lang),
        ))
    if income_mod != 0:
        factors.append(RiskFactor(
            factor=t("risk.mod.income", lang),
            answer=t(f"risk.mod.income.{answers.income_stability}", lang),
            contribution=income_mod,
            explanation=t("risk.mod.income.why", lang),
        ))

    score = round(min(max(base + modifier, 1.0), 10.0), 1)
    label = _label(score, lang)

    # Modifier context for summary
    modifier_note = ""
    if answers.age and answers.age >= 55:
        modifier_note += t("risk.note.older", lang)
    elif answers.age and answers.age <= 30:
        modifier_note += t("risk.note.younger", lang)
    if answers.income_stability == "irregular":
        modifier_note += t("risk.note.irregular", lang)
    elif answers.income_stability == "variable":
        modifier_note += t("risk.note.variable", lang)

    # Readable answers — raw enum values ("long", "growth") used to leak
    # English words into the sentence whatever the language was
    summary = t(
        "risk.summary", lang,
        score=score, label=label,
        horizon=_answer_label("time_horizon", answers.time_horizon, lang),
        tolerance=_answer_label("loss_tolerance", answers.loss_tolerance, lang),
        # German capitalises nouns; lowercasing "Wachstum" mid-sentence is
        # a Turkish/English habit that reads as a typo in German.
        goal=_goal_in_sentence(answers.goal, lang),
        note=modifier_note,
    )

    return RiskProfileResponse(
        risk_score=score,
        label=label,
        summary=summary,
        factors=factors,
        answers=answers,
        debt_check=debt_check.check(answers.high_interest_debt, answers.budget),
    )
