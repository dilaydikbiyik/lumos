from contextlib import asynccontextmanager
from typing import Callable, cast

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded


from backend.config import settings
from backend.limiter import limiter

# Error monitoring — activates only when SENTRY_DSN is configured; a fresh
# clone without an account runs exactly as before.
if settings.SENTRY_DSN:
    import sentry_sdk

    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.APP_ENV,
        traces_sample_rate=0.1,
        send_default_pii=False,  # never ship user content to a third party
    )
from backend.middleware.error_handler import register_error_handlers
from backend.middleware.request_id import RequestIDMiddleware
from backend.routers import admin, backtest, chat, coach, feedback, health, holdings, news, planning, practice, profile, recommend, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle.

    Schema is owned by Alembic — run `alembic upgrade head` before starting
    (the Dockerfile CMD does this automatically).
    """
    # Admin bootstrap: promote any IDs listed in ADMIN_CLERK_IDS to admin.
    # Safe to run on every start (idempotent — won't downgrade existing admins).
    if settings.ADMIN_CLERK_IDS:
        import logging
        from backend.db.database import AsyncSessionLocal
        from backend.repositories import user_repository

        _log = logging.getLogger("lumos.startup")
        ids = [uid.strip() for uid in settings.ADMIN_CLERK_IDS.split(",") if uid.strip()]
        async with AsyncSessionLocal() as db:
            for clerk_id in ids:
                try:
                    user = await user_repository.get_or_create(db, clerk_id)
                    if user.role != "admin":
                        user.role = "admin"
                        await db.flush()
                        _log.info("Admin promoted: %s", clerk_id)
                    await db.commit()
                except Exception as exc:
                    _log.warning("Admin bootstrap failed for %s: %s", clerk_id, exc)
                    await db.rollback()
    yield


app = FastAPI(
    title="Lumos — Smart Investment Assistant",
    description="AI-powered portfolio recommendation API",
    version="1.0.0",
    lifespan=lifespan,
)

# ── Rate Limiting ─────────────────────────────────────────────────────────────
app.state.limiter = limiter
# cast: slowapi's handler signature is narrower than the generic
# (Request, Exception) Starlette expects — cast sidesteps the type check
app.add_exception_handler(
    RateLimitExceeded,
    cast(Callable[[Request, Exception], Response], _rate_limit_exceeded_handler),
)

# ── Request ID (correlation) ──────────────────────────────────────────────────
app.add_middleware(RequestIDMiddleware)

# ── CORS ──────────────────────────────────────────────────────────────────────
_dev_origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
]
_allowed_origins = _dev_origins if settings.APP_ENV == "development" else [settings.FRONTEND_URL]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Global error handlers ─────────────────────────────────────────────────────
register_error_handlers(app)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(health.router, tags=["Health"])
app.include_router(chat.router,    prefix="/chat",      tags=["Chat"])
app.include_router(profile.router, prefix="/profile",   tags=["Profile"])
app.include_router(recommend.router, prefix="/recommend", tags=["Recommend"])
app.include_router(users.router,   prefix="/users",     tags=["Users"])
app.include_router(holdings.router, prefix="/holdings", tags=["Holdings"])
app.include_router(backtest.router, prefix="/backtest", tags=["Backtest"])
app.include_router(news.router,     prefix="/news",      tags=["News"])
app.include_router(coach.router,    prefix="/coach",     tags=["Coach"])
app.include_router(planning.router, prefix="/planning",  tags=["Planning"])
app.include_router(practice.router,  prefix="/practice",  tags=["Practice"])
app.include_router(admin.router,    prefix="/admin",     tags=["Admin"])
app.include_router(feedback.router, prefix="/feedback",  tags=["Feedback"])
