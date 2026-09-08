import logging
from typing import Literal, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.database import get_db
from backend.middleware.verify_clerk import get_current_user
from backend.repositories import holding_repository, user_repository
from backend.i18n import t
from backend.middleware.language import language
from backend.services.behavior_coach import drop_message, rise_message

router = APIRouter()
logger = logging.getLogger("lumos.coach")

# Honest, static facts shown in a panic moment — zero LLM cost, zero
# alarmism. Source: common market history; contains no forecasts.
_PANIC_FACT_KEYS = [
    "panic.fact.recovery",
    "panic.fact.paper_loss",
    "panic.fact.best_days",
    "panic.fact.do_nothing",
]


def panic_facts(lang: str) -> list[str]:
    return [t(k, lang) for k in _PANIC_FACT_KEYS]


class MarketMoveRequest(BaseModel):
    direction: Literal["drop", "rise"]
    drawdown_pct: float = 0.0


@router.post("/market-move")
async def market_move_message(
    body: MarketMoveRequest,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    lang: str = Depends(language),
):
    """
    Profile-specific calming/grounding message for a market move — the
    behaviour coach reacts to how THIS user's stated loss tolerance
    should shape their reaction, not a generic headline.
    """
    user = await user_repository.get_or_create(db, user_id)
    loss_tolerance = user.loss_tolerance or "medium"

    if body.direction == "drop":
        message = drop_message(loss_tolerance, body.drawdown_pct, lang)
    else:
        message = rise_message(loss_tolerance, lang)

    return {"loss_tolerance": loss_tolerance, "message": message}


class PanicRequest(BaseModel):
    # null = button just pressed; held/still_worried = the choice at the end of the flow
    resolution: Optional[Literal["held", "still_worried"]] = None


@router.post("/panic")
async def panic_button(
    body: PanicRequest,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    lang: str = Depends(language),
):
    """
    Panic Button 🫨 — pressed when the market gets scary. No dark patterns:
    we never block selling, we only calm the user according to their OWN
    profile and recall honest facts. Press and outcome are logged — raw
    data for the behaviour mirror.
    """
    user = await user_repository.get_or_create(db, user_id)
    loss_tolerance = user.loss_tolerance or "medium"

    if body.resolution is not None:
        logger.info("panic_resolved user=%s resolution=%s", user_id, body.resolution)
        closing = t("panic.held" if body.resolution == "held" else "panic.sold", lang)
        return {"message": closing}

    logger.info("panic_pressed user=%s loss_tolerance=%s", user_id, loss_tolerance)
    return {
        "loss_tolerance": loss_tolerance,
        "message": drop_message(loss_tolerance, lang=lang),
        "facts": panic_facts(lang),
    }


@router.get("/behavior-mirror")
async def behavior_mirror_check(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    lang: str = Depends(language),
):
    """
    Compare stated loss tolerance against actual emotion-tagged purchases —
    a gentle mirror, not a judgment.
    """
    from backend.services.behavior_coach import behavior_mirror

    user = await user_repository.get_or_create(db, user_id)
    holdings = await holding_repository.list_for_user(db, user.id)

    tagged = [h for h in holdings if h.emotion_tag]
    fomo_count = sum(1 for h in tagged if h.emotion_tag == "fomo")
    panik_count = sum(1 for h in tagged if h.emotion_tag == "panik")
    plan_count = sum(1 for h in tagged if h.emotion_tag == "plan")

    note = None
    if user.loss_tolerance == "low" and fomo_count > plan_count:
        note = behavior_mirror("low", "bought_dip", lang) or t("coach.mirror.fomo", lang)

    return {
        "tagged_count": len(tagged),
        "by_emotion": {"plan": plan_count, "fomo": fomo_count, "panik": panik_count},
        "note": note,
    }
