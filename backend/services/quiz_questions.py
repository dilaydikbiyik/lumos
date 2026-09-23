"""
The risk quiz as DATA rather than as a script a model reads out.

Why this exists. The nine questions were written down in
`prompts/system_prompt.txt`, and the app then paid a frontier model to read
them out one at a time: one full chat call per answer, on the most
restricted provider tier, because weak models paraphrase the script and
corrupt the flow. A single new user spent roughly ten calls out of a fifty
a day free quota to be asked questions that were already written.

It was also where every reported failure lived — the Turkish sentence in an
English session, the nested-JSON profile that returned the wrong object, the
cold reads, the quota burn. All of it in the one flow that has to work,
because nothing else in the app happens before it.

So the questions are served as data, the client renders them as real inputs,
and the answers arrive already shaped like `RiskProfileAnswers` — no model,
no extraction, nothing to parse. The conversational path is untouched and
still there for anyone who would rather talk, which is a real preference and
not a fallback.

OPTION LABELS COME FROM THE RISK ENGINE'S OWN KEYS (`risk.*`). The score
breakdown already prints "your answer" using those, and a quiz that worded
them differently would show someone one phrase while asking and a different
one while explaining their score.
"""

from typing import Optional

from backend.i18n import t

# field -> the enum values the schema accepts, in the order to show them.
# Ordered low-to-high risk so the scale reads as a scale rather than a list.
_CHOICES: dict[str, list[str]] = {
    "time_horizon": ["short", "medium", "long"],
    "loss_tolerance": ["low", "medium", "high"],
    "goal": ["preservation", "income", "growth", "speculation"],
    "experience": ["none", "beginner", "intermediate", "advanced"],
    "income_stability": ["stable", "variable", "irregular"],
}


# The engine does not label every field under the same prefix: income
# stability is a MODIFIER in the score, so its labels live under
# `risk.mod.income.*`. Mapping it here keeps the quiz reading exactly what
# the score breakdown will later print back at the reader.
_LABEL_PREFIX = {"income_stability": "risk.mod.income"}


def _options(field: str, lang: str) -> list[dict]:
    prefix = _LABEL_PREFIX.get(field, f"risk.{field}")
    return [
        {
            "value": value,
            # The engine's own label, so asking and explaining use one wording.
            "label": t(f"{prefix}.{value}", lang),
            "help": t(f"quiz.q.{field}.opt.{value}", lang),
        }
        for value in _CHOICES[field]
    ]


def questions(lang: str = "tr", currency: str = "TRY") -> list[dict]:
    """
    The quiz, in order, shaped so the client can render it without knowing
    anything about risk scoring.

    `required` mirrors the schema exactly: budget, horizon, loss tolerance,
    goal and experience are required; age, contribution, debt and income
    stability are not. A question the schema lets you skip must be skippable
    on screen too, or the form is stricter than the model it feeds.
    """
    def ask(field: str, kind: str, required: bool, **extra) -> dict:
        return {
            "field": field,
            "type": kind,
            "required": required,
            "title": t(f"quiz.q.{field}.title", lang, currency=currency),
            "help": t(f"quiz.q.{field}.help", lang, currency=currency),
            **extra,
        }

    return [
        ask("budget", "amount", True),
        ask("monthly_contribution", "amount", False),
        ask("time_horizon", "choice", True, options=_options("time_horizon", lang)),
        ask("loss_tolerance", "choice", True, options=_options("loss_tolerance", lang)),
        ask("goal", "choice", True, options=_options("goal", lang)),
        ask("experience", "choice", True, options=_options("experience", lang)),
        ask("age", "number", False, min=18, max=100),
        # Asked LAST of the optional ones on purpose: it is the question most
        # likely to embarrass somebody, and by this point they have already
        # answered eight and can see the thing is nearly done.
        ask("high_interest_debt", "amount", False),
        ask("income_stability", "choice", False,
            options=_options("income_stability", lang)),
    ]


def required_fields() -> set[str]:
    return {q["field"] for q in questions("en") if q["required"]}


def choice_values(field: str) -> Optional[list[str]]:
    return _CHOICES.get(field)
