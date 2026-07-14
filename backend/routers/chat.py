import asyncio
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
    # In development use the settings limit (9999) instead of the tier limit
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
    # ai_chat uses blocking I/O (httpx sync + google-genai SDK) — run in a
    # thread pool so the async event loop stays free for other requests.
    reply = await asyncio.to_thread(ai_chat, messages, user.plan)
    return {"reply": reply}


def _advisor_context(user) -> str:
    """A compact 'USER CONTEXT' block so the advisor answers personally."""
    lines = []
    if user.risk_score is not None:
        lines.append(f"- Risk skoru: {user.risk_score}/10")
    if user.budget:
        lines.append(f"- Bütçe: {user.budget:,.0f} TL")
    if user.time_horizon:
        lines.append(f"- Vade tercihi: {user.time_horizon}")
    if user.goal:
        lines.append(f"- Hedef: {user.goal}")
    if user.experience:
        lines.append(f"- Deneyim: {user.experience}")
    if user.investment_path:
        lines.append(f"- Seçtiği yol: {user.investment_path}")
    if user.primary_fear:
        lines.append(f"- Onboarding korkusu: {user.primary_fear}")
    if not lines:
        return "\n\nUSER CONTEXT: (Kullanıcı henüz risk profilini tamamlamadı.)\n"
    return "\n\nUSER CONTEXT (bu kullanıcının gerçek profili):\n" + "\n".join(lines) + "\n"


@router.post("/advisor", response_model=ChatResponse)
@limiter.limit("20/minute")
async def advisor_endpoint(
    request: Request,
    body: ChatRequest,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Free-form education assistant reachable from anywhere (NOT the risk quiz)."""
    from backend.services.ai_tiers import get_tier

    user = await user_repository.get_or_create(db, user_id)
    tier = get_tier(user.plan)
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
    context = _advisor_context(user)
    # ai_chat is synchronous (blocking I/O) — run off the event loop
    reply = await asyncio.to_thread(
        ai_chat, messages, user.plan, "advisor", context
    )
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
    answers = await asyncio.to_thread(extract_profile, messages)
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
    "What if?" assistant — tool-use: the AI never invents the math; it calls
    portfolio_engine for a real before/after and only narrates the result.
    """
    from backend.services.what_if import answer_what_if

    allowed = await user_repository.consume_quota(db, user_id, settings.DAILY_MESSAGE_QUOTA)
    if not allowed:
        raise HTTPException(status_code=429, detail="Günlük mesaj hakkın doldu — yarın yenilenir.")

    return await asyncio.to_thread(answer_what_if, body.question, body.risk_score, body.budget)
