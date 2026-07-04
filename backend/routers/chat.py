from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, ValidationError
from backend.limiter import limiter
from backend.middleware.verify_clerk import get_current_user
from backend.models.user_profile import RiskProfileAnswers
from backend.services.ai_service import chat as ai_chat, extract_profile

router = APIRouter()


class ChatMessage(BaseModel):
    role: str   # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]


class ChatResponse(BaseModel):
    reply: str


@router.post("", response_model=ChatResponse)
@limiter.limit("20/minute")
async def chat_endpoint(
    request: Request,
    body: ChatRequest,
    user_id: str = Depends(get_current_user),
):
    """Multi-turn chat with the Lumos AI assistant. Requires a valid Clerk JWT."""
    messages = [m.model_dump() for m in body.messages]
    reply = ai_chat(messages)
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
