from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from backend.config import settings
from backend.limiter import limiter
from backend.middleware.error_handler import register_error_handlers
from backend.routers import backtest, chat, coach, health, holdings, news, planning, practice, profile, recommend, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle.

    Schema is owned by Alembic — run `alembic upgrade head` before starting
    (the Dockerfile CMD does this automatically).
    """
    yield


app = FastAPI(
    title="Lumos — Smart Investment Assistant",
    description="AI-powered portfolio recommendation API",
    version="0.1.0",
    lifespan=lifespan,
)

# ── Rate Limiting ─────────────────────────────────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
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
