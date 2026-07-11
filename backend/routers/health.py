from fastapi import APIRouter
from pydantic import BaseModel
from backend.db.database import engine as async_engine
from backend.config import settings
from sqlalchemy import text

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    version: str
    db: str
    ai: str


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Uptime monitoring endpoint — genuinely probes DB and AI provider access.
    """
    # DB connectivity check
    db_status = "ok"
    try:
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception:
        db_status = "error"

    # AI provider configuration check (config only, not an access test)
    ai_status = "ok"
    provider = settings.AI_PROVIDER
    if provider == "anthropic" and not settings.ANTHROPIC_API_KEY:
        ai_status = "not_configured"
    elif provider == "gemini" and not settings.GEMINI_API_KEY:
        ai_status = "not_configured"

    overall = "ok" if db_status == "ok" and ai_status == "ok" else "degraded"

    return {
        "status": overall,
        "version": "0.2.0",
        "db": db_status,
        "ai": ai_status,
    }
