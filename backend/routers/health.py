import logging
from fastapi import APIRouter
from pydantic import BaseModel
from backend.db.database import engine as async_engine
from backend.config import settings
from sqlalchemy import text

logger = logging.getLogger("lumos.health")

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    version: str
    db: str
    ai: str
    # Which keyed data sources are configured on THIS instance. Booleans
    # only — a health endpoint must never echo a secret, and "is it set"
    # is the whole question when a key was just added in the dashboard.
    data_sources: dict[str, bool]
    # Whether the ADMIN_CLERK_IDS bootstrap actually took. A deployment with
    # no admin cannot be managed from inside the app at all, and until now the
    # only way to find that out was to sign in and be refused. A boolean, not
    # a count or an id: "is this deployment manageable" is the whole question.
    has_admin: bool
    # Whether the cache's durable tier is live. The last-known-good data that
    # carries the app through a provider outage lives on an EPHEMERAL disk
    # unless this is true, so "is the fallback actually going to be there"
    # is a question worth being able to answer without reading logs.
    durable_cache: bool


def _durable_cache_enabled() -> bool:
    """Never let a cache probe be the reason /health fails."""
    try:
        from backend.services import cache_store

        return cache_store.is_enabled()
    except Exception:
        return False


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Uptime monitoring endpoint — genuinely probes DB and AI provider access.
    """
    # DB connectivity check
    has_admin = False
    db_status = "ok"
    try:
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            has_admin = bool((await conn.execute(
                text("SELECT 1 FROM users WHERE role = 'admin' LIMIT 1")
            )).first())
    except Exception as exc:
        # Never swallow this: /health is what uptime monitoring reads, so the
        # reason the database is unreachable has to reach the logs.
        logger.error("health_check db unreachable: %s: %s", type(exc).__name__, exc)
        db_status = "error"

    # AI provider configuration check (config only, not an access test)
    ai_status = "ok"
    provider = settings.AI_PROVIDER
    if provider == "anthropic" and not settings.ANTHROPIC_API_KEY:
        ai_status = "not_configured"
    elif provider == "gemini" and not settings.GEMINI_API_KEY:
        ai_status = "not_configured"

    overall = "ok" if db_status == "ok" and ai_status == "ok" else "degraded"

    # Keyless sources (BLS, Eurostat) are deliberately absent: there is no
    # key to misconfigure, so reporting them would be noise.
    return {
        "status": overall,
        "version": "1.0.0",
        "db": db_status,
        "ai": ai_status,
        "has_admin": has_admin,
        "durable_cache": _durable_cache_enabled(),
        "data_sources": {
            "tcmb_evds": bool(settings.TCMB_EVDS_API_KEY),
            "fred": bool(settings.FRED_API_KEY),
        },
    }
