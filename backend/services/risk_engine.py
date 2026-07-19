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


def _label(score: float) -> str:
    # Turkish labels — the UI language is Turkish; an English "Growth" badge
    # inside Turkish copy was an inconsistency (fixed 2026-07-11)
    if score <= 3:
        return "Muhafazakâr"
    elif score <= 6:
        return "Dengeli"
    elif score <= 8:
        return "Büyüme Odaklı"
    else:
        return "Atılgan"


def _age_modifier(age: int | None) -> float:
    """Older users need more capital preservation; younger users have longer runway."""
    if age is None:
        return 0.0
    if age >= 55:
        return -0.5
    if age <= 30:
        return 0.5
    return 0.0


_ANSWER_LABELS = {
    "time_horizon": {"short": "Kısa (<2 yıl)", "medium": "Orta (2-10 yıl)", "long": "Uzun (10+ yıl)"},
    "loss_tolerance": {"low": "Düşüşte satarım", "medium": "Bekler, tutarım", "high": "Düşüşte alırım"},
    "goal": {"preservation": "Koruma", "income": "Düzenli gelir", "growth": "Büyüme", "speculation": "Spekülasyon"},
    "experience": {"none": "Hiç yok", "beginner": "Yeni başlayan", "intermediate": "Orta", "advanced": "İleri"},
}

_FACTOR_EXPLANATIONS = {
    "time_horizon": "Vade uzadıkça kısa vadeli dalgalanmaların önemi azalır — en belirleyici faktör budur",
    "loss_tolerance": "Düşüş anındaki gerçek davranışın, teoriden daha önemlidir — en yüksek ağırlık bunda",
    "goal": "Hedefin, kabul etmen gereken risk seviyesini belirler",
    "experience": "Deneyim, dalgalanmayı tanımayı ve panik yapmamayı kolaylaştırır",
}


def compute_risk_score(answers: RiskProfileAnswers) -> RiskProfileResponse:
    """
    Compute a 1-10 risk score from the profile answers.

    Args:
        answers: Validated RiskProfileAnswers instance.

    Returns:
        RiskProfileResponse with score, label, and Turkish summary.
    """
    dimension_scores = {
        "time_horizon": _TIME_HORIZON_SCORES[answers.time_horizon],
        "loss_tolerance": _LOSS_TOLERANCE_SCORES[answers.loss_tolerance],
        "goal": _GOAL_SCORES[answers.goal],
        "experience": _EXPERIENCE_SCORES[answers.experience],
    }
    base = sum(dimension_scores[d] * _WEIGHTS[d] for d in dimension_scores)

    # ── transparent breakdown: where every point comes from ──
    factor_names = {
        "time_horizon": "Yatırım vaden",
        "loss_tolerance": "Kayıp toleransın",
        "goal": "Hedefin",
        "experience": "Deneyimin",
    }
    factors = [
        RiskFactor(
            factor=f"{factor_names[d]} (ağırlık %{round(_WEIGHTS[d] * 100)})",
            answer=_ANSWER_LABELS[d][getattr(answers, d)],
            contribution=round(dimension_scores[d] * _WEIGHTS[d], 2),
            explanation=_FACTOR_EXPLANATIONS[d],
        )
        for d in dimension_scores
    ]

    # Optional modifiers — each capped so they can't dominate
    age_mod = _age_modifier(answers.age)
    income_mod = _INCOME_MODIFIER[answers.income_stability] if answers.income_stability else 0.0
    modifier = max(-1.5, min(1.5, age_mod + income_mod))

    if age_mod != 0 and answers.age is not None:
        factors.append(RiskFactor(
            factor="Yaş düzeltmesi",
            answer=f"{answers.age} yaş",
            contribution=age_mod,
            explanation=("55+ yaşta koruma önceliği artar" if age_mod < 0
                         else "30 yaş altı: uzun toparlanma süresi risk kapasitesini artırır"),
        ))
    if income_mod != 0:
        factors.append(RiskFactor(
            factor="Gelir istikrarı düzeltmesi",
            answer={"variable": "Değişken gelir", "irregular": "Düzensiz gelir"}.get(answers.income_stability, str(answers.income_stability)),
            contribution=income_mod,
            explanation="Öngörülemeyen gelir daha büyük güvenlik payı gerektirir — skor aşağı çekilir",
        ))

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

    # Readable Turkish answers — raw enum values ("long", "growth") leaked
    # English words into a Turkish sentence
    summary = (
        f"Risk skoru {score}/10 ({label}). "
        f"{_ANSWER_LABELS['time_horizon'][answers.time_horizon]} yatırım ufku, "
        f"\"{_ANSWER_LABELS['loss_tolerance'][answers.loss_tolerance]}\" kayıp toleransı ve "
        f"{_ANSWER_LABELS['goal'][answers.goal].lower()} hedefi temel alındı.{modifier_note}"
    )

    return RiskProfileResponse(
        risk_score=score,
        label=label,
        summary=summary,
        factors=factors,
        answers=answers,
        debt_check=debt_check.check(answers.high_interest_debt, answers.budget),
    )
