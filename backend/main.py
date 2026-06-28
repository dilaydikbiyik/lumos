from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from backend.config import settings
from backend.db.database import create_tables
from backend.middleware.error_handler import register_error_handlers
from backend.routers import chat, health, profile, recommend, users

limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle."""
    await create_tables()
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
