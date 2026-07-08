import logging
from typing import Literal, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.database import get_db
from backend.middleware.verify_clerk import get_current_user
from backend.repositories import holding_repository, user_repository
from backend.services.behavior_coach import drop_message, rise_message

router = APIRouter()
logger = logging.getLogger("lumos.coach")

# Panik anında gösterilen dürüst, statik gerçekler — LLM maliyeti sıfır,
# alarmizm sıfır. Kaynak: yaygın piyasa tarihi bilgisi, tahmin içermez.
PANIC_FACTS = [
    "Tarihte her büyük düşüşün bir toparlanma dönemi oldu — süresi değişir, yönü genelde değişmedi.",
    "Panik anında satanlar, düşüşü 'gerçekleşmiş zarara' çevirir. Satmadığın sürece kayıp kağıt üstündedir.",
    "En kötü günlerde satıp en iyi günleri kaçırmak, uzun vadeli getirinin en büyük düşmanıdır — en iyi günler çoğu zaman en kötü günlerin hemen yanındadır.",
    "Bu ekranı kapattıktan sonra hiçbir şey yapmaman da tamamen geçerli bir karardır.",
]


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


class PanicRequest(BaseModel):
    # null = düğmeye yeni basıldı; held/still_worried = akışın sonundaki seçim
    resolution: Optional[Literal["held", "still_worried"]] = None


@router.post("/panic")
async def panic_button(
    body: PanicRequest,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Panik Düğmesi 🫨 — piyasa korkuttuğunda basılır. Karanlık desen yok:
    satışı engellemiyoruz, sadece kullanıcının KENDİ profiline göre
    sakinleştirip dürüst gerçekleri hatırlatıyoruz. Basış ve sonuç
    loglanır — davranış aynasının ham verisi.
    """
    user = await user_repository.get_or_create(db, user_id)
    loss_tolerance = user.loss_tolerance or "medium"

    if body.resolution is not None:
        logger.info("panic_resolved user=%s resolution=%s", user_id, body.resolution)
        closing = (
            "Plana sadık kalmak, panik anında verilebilecek en güçlü karardır. 🕯️"
            if body.resolution == "held"
            else "Endişen meşru. Büyük bir karar vermeden önce 24 saat beklemek ve "
                 "lisanslı bir danışmanla konuşmak hiçbir şey kaybettirmez."
        )
        return {"message": closing}

    logger.info("panic_pressed user=%s loss_tolerance=%s", user_id, loss_tolerance)
    return {
        "loss_tolerance": loss_tolerance,
        "message": drop_message(loss_tolerance),
        "facts": PANIC_FACTS,
    }


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
