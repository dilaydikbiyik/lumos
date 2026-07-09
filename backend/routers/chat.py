from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field, ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import settings
from backend.db.database import get_db
from backend.limiter import limiter
from backend.middleware.verify_clerk import get_current_user
from backend.repositories import user_repository
from backend.schemas.user_profile import RiskProfileAnswers
from backend.services.ai_service import chat as ai_chat, extract_profile

router = APIRouter()


class WhatIfRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=500)
    risk_score: float = Field(..., ge=1, le=10)
    budget: float = Field(..., gt=0)


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(..., min_length=1, max_length=4000)


class ChatRequest(BaseModel):
    # Cap history length — blocks context-stuffing and runaway token cost
    messages: list[ChatMessage] = Field(..., min_length=1, max_length=80)


class ChatResponse(BaseModel):
    reply: str


@router.post("", response_model=ChatResponse)
@limiter.limit("20/minute")
async def chat_endpoint(
    request: Request,
    body: ChatRequest,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Multi-turn chat with the Lumos AI assistant. Requires a valid Clerk JWT."""
    from backend.services.ai_tiers import get_tier

    user = await user_repository.get_or_create(db, user_id)
    tier = get_tier(user.plan)
    # Dev ortamında tier limiti yerine settings'i kullan (9999)
    effective_quota = settings.DAILY_MESSAGE_QUOTA if settings.APP_ENV == "development" else tier["daily_quota"]
    allowed = await user_repository.consume_quota(db, user_id, effective_quota)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=(
                f"Günlük mesaj hakkın doldu ({tier['daily_quota']}/gün) — yarın yenilenir. "
                "Daha fazla mesaj için planını yükseltebilirsin. / Daily limit reached; resets tomorrow."
            ),
        )
    messages = [m.model_dump() for m in body.messages]
    reply = ai_chat(messages, tier=user.plan)
    return {"reply": reply}


@router.post("/extract-profile", response_model=RiskProfileAnswers)
@limiter.limit("10/minute")
async def extract_profile_endpoint(
    request: Request,
    body: ChatRequest,
    user_id: str = Depends(get_current_user),
):
    """
    Extract structured risk-profile answers from a completed profiling
    conversation (frontend calls this after seeing [PROFILE_COMPLETE]).
    Validation against RiskProfileAnswers happens via the response model.
    """
    messages = [m.model_dump() for m in body.messages]
    answers = extract_profile(messages)
    try:
        return RiskProfileAnswers(**answers)
    except ValidationError:
        raise HTTPException(
            status_code=422,
            detail="Extracted profile is incomplete — please continue the conversation.",
        )


@router.post("/what-if")
@limiter.limit("15/minute")
async def what_if_endpoint(
    request: Request,
    body: WhatIfRequest,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    'Ne olurdu?' asistanı — tool-use: AI matematiği uydurmaz, portfolio_engine'i
    gerçek before/after olarak çağırır, sadece sonucu yorumlar.
    """
    from backend.services.what_if import answer_what_if

    allowed = await user_repository.consume_quota(db, user_id, settings.DAILY_MESSAGE_QUOTA)
    if not allowed:
        raise HTTPException(status_code=429, detail="Günlük mesaj hakkın doldu — yarın yenilenir.")

    return answer_what_if(body.question, body.risk_score, body.budget)
