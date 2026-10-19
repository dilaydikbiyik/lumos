"""
Behavioral coach — the thing robo-advisors don't do: react to how a
downturn FEELS for this specific person, not just show them a number.

Zero AI cost by default (template-based, keyed on loss_tolerance); an
optional richer AI-generated version is available for the chat surface.
"""
from typing import Optional

from backend.i18n import t
from backend.services.ai_service import generate_text

# Calm, profile-specific templates — no AI call needed for the common case.
# The wording lives in the catalogue so the message speaks the reader's
# language; only the profile→tone mapping belongs here.
_TONES = {"low", "medium", "high"}


def _tone(loss_tolerance: str) -> str:
    return loss_tolerance if loss_tolerance in _TONES else "medium"


def drop_message(loss_tolerance: str, drawdown_pct: Optional[float] = None,
                 lang: str = "tr") -> str:
    """Calming, profile-specific message for a market downturn."""
    return t(f"coach.drop.{_tone(loss_tolerance)}", lang)


def rise_message(loss_tolerance: str, lang: str = "tr") -> str:
    """Grounding message for a market upswing — prevents overconfidence."""
    return t(f"coach.rise.{_tone(loss_tolerance)}", lang)


def behavior_mirror(stated_loss_tolerance: str, recent_action: str,
                    lang: str = "tr") -> Optional[str]:
    """
    Gently hold up a mirror when stated risk tolerance and actual behavior
    diverge — e.g. profile says "I'd sell everything" but the user just
    bought more during a dip, or vice versa.

    recent_action: "bought_dip" | "sold_dip" | "bought_rise" | "sold_rise"
    """
    key = {
        ("low", "bought_dip"): "coach.mirror.brave",
        ("high", "sold_dip"): "coach.mirror.sold",
    }.get((stated_loss_tolerance, recent_action))
    return t(key, lang) if key else None


def ai_coach_message(loss_tolerance: str, context: str) -> str:
    """
    Richer, situation-specific coaching via the LLM.

    NOT CALLED ANYWHERE. Kept because the panic and market-move surfaces
    may want it, but it is an unguarded AI entry point sitting in a file
    everything else in imports, and the docstring used to claim the chat
    surface used it — which it does not, and never did.

    If it is wired up, it needs a rule of its own first. A coaching message
    makes no claim about an allocation, so the portfolio check does not
    apply; what it must not do is predict, exactly like the news sentence.
    `forecast_language.is_forecast` is the rule it wants, and the registry
    test in test_every_ai_field_is_accounted_for.py will fail until this
    function is either guarded or removed.
    """
    system = (
        "You are Lumos's behavioral coach. The user's loss tolerance is "
        f"'{loss_tolerance}' (low/medium/high). Respond in 2-3 calm sentences: "
        "acknowledge the situation, ground them in their own plan, never alarmist, "
        "never dismissive. Respond in the same language as the context."
    )
    return generate_text(context, system=system)
