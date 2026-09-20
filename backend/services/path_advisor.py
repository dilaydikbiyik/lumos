"""
Suggest an investment path for someone who answered "not sure yet".

Deliberately RULE-BASED, not an LLM call. This follows `readiness_score`'s
principle — "no mystery algorithm: every point is explained" — for the same
reason: a beginner who is told which world to start in deserves to see why,
in terms they can argue with. "The model said so" is not a reason, and a
model asked the same question twice does not have to answer the same way.

The rules encode three things that genuinely decide this, and nothing else:

  HORIZON      Property is illiquid and its purchase costs are front-loaded.
               Under about five years those costs have no time to amortise,
               and the answer is not "buy a worse flat", it is "not yet".

  BUDGET       Below a market's entry threshold, physical property is not an
               option at all — and pretending otherwise wastes someone's time.
               REITs are the honest bridge, and they live on the stocks side.

  FEAR         The fear someone named at check-in is real information. Someone
               whose fear is "I don't understand any of it" should not be sent
               first into the side with notaries, deeds and transfer taxes.

Everything here is a SUGGESTION. The caller presents it as one, the user can
ignore it, and nothing is saved until they choose.
"""

import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger("lumos.path_advisor")

# Under this, purchase costs (transfer tax, agency, notary) have no time to
# amortise, so property is usually the wrong instrument whatever the market.
SHORT_HORIZON_YEARS = 5

# A horizon long enough that illiquidity stops being the binding constraint.
LONG_HORIZON_YEARS = 10


@dataclass(frozen=True)
class PathSuggestion:
    path: str                  # stocks | real_estate | hybrid
    reasons: list[str]         # i18n keys, so the client owns the wording
    confident: bool            # False when the inputs barely decide it


def _years(value) -> Optional[float]:
    """Horizon as a number of years, whatever shape the profile stored it in."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().lower()
    # The quiz stores words in the reader's language; these are the stable
    # values the profile schema uses, not free text.
    words = {
        "kisa": 2, "kısa": 2, "short": 2,
        "orta": 6, "medium": 6,
        "uzun": 15, "long": 15,
    }
    if text in words:
        return float(words[text])
    try:
        return float(text)
    except ValueError:
        return None


def suggest(*, horizon=None, budget: Optional[float] = None,
            primary_fear: Optional[str] = None,
            entry_threshold: Optional[float] = None) -> PathSuggestion:
    """
    A path, with the reasons that produced it.

    `entry_threshold` is the market's realistic minimum for buying property —
    it comes from the caller's market pack rather than being assumed here,
    because "enough to buy a flat" is a fact about a country.
    """
    reasons: list[str] = []
    years = _years(horizon)

    wants_property_later = False

    # 1. Horizon. The strongest single signal, and the least subjective.
    if years is not None and years < SHORT_HORIZON_YEARS:
        reasons.append("path.reason.short_horizon")
        suggested = "stocks"
    elif years is not None and years >= LONG_HORIZON_YEARS:
        reasons.append("path.reason.long_horizon")
        suggested = "hybrid"
        wants_property_later = True
    else:
        suggested = "stocks"
        if years is not None:
            reasons.append("path.reason.medium_horizon")

    # 2. Budget against this market's entry threshold.
    if budget is not None and entry_threshold:
        if budget < entry_threshold:
            reasons.append("path.reason.below_entry")
            # Property is not available at this size. Say so, and point at the
            # instrument that actually gives property exposure.
            suggested = "stocks"
        elif wants_property_later:
            reasons.append("path.reason.above_entry")

    # 3. The fear they named. It changes where to START, not what is possible.
    if primary_fear == "anlamiyorum":
        # "I don't understand any of it" — the side with deeds, notaries and
        # transfer taxes is the harder place to learn in.
        if suggested == "hybrid":
            suggested = "stocks"
        reasons.append("path.reason.fear_complexity")
    elif primary_fear == "param_eriyor" and suggested == "stocks":
        # "My money is melting" is an inflation fear, and property is one of
        # the things people reach for against it. Worth naming even when the
        # horizon says start elsewhere.
        reasons.append("path.reason.fear_inflation")

    if not reasons:
        # Nothing to go on. Say that rather than inventing a rationale.
        return PathSuggestion("hybrid", ["path.reason.no_signal"], confident=False)

    return PathSuggestion(suggested, reasons, confident=len(reasons) >= 2)
