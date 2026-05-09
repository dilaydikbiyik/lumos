from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.db.database import create_tables
from backend.middleware.error_handler import register_error_handlers
from backend.routers import chat, health, profile, recommend, users


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
