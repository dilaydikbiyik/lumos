from typing import Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.database import get_db
from backend.middleware.verify_clerk import get_current_user
from backend.repositories import holding_repository, user_repository
from backend.services.behavior_coach import drop_message, rise_message

router = APIRouter()


class MarketMoveRequest(BaseModel):
    direction: Literal["drop", "rise"]
    drawdown_pct: float = 0.0


@router.post("/market-move")
async def market_move_message(
    body: MarketMoveRequest,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Profile-specific calming/grounding message for a market move — the
    'davranışsal koç' reacts to how THIS user's stated loss tolerance
    should shape their reaction, not a generic headline.
    """
    user = await user_repository.get_or_create(db, user_id)
    loss_tolerance = user.loss_tolerance or "medium"

    if body.direction == "drop":
        message = drop_message(loss_tolerance, body.drawdown_pct)
    else:
        message = rise_message(loss_tolerance)

    return {"loss_tolerance": loss_tolerance, "message": message}


@router.get("/behavior-mirror")
async def behavior_mirror_check(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
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
        note = behavior_mirror("low", "bought_dip") or (
            "Kararların çoğu FOMO etiketli görünüyor — bu tamamen normal, ama "
            "farkında olmak bir sonraki kararını daha bilinçli hale getirir."
        )

    return {
        "tagged_count": len(tagged),
        "by_emotion": {"plan": plan_count, "fomo": fomo_count, "panik": panik_count},
        "note": note,
    }
