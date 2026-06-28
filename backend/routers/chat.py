from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from backend.limiter import limiter
from backend.middleware.verify_clerk import get_current_user
from backend.services.ai_service import chat as ai_chat

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
