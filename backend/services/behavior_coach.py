"""
Behavioral coach — the thing robo-advisors don't do: react to how a
downturn FEELS for this specific person, not just show them a number.

Zero AI cost by default (template-based, keyed on loss_tolerance); an
optional richer AI-generated version is available for the chat surface.
"""
from typing import Optional

from backend.i18n import t

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
