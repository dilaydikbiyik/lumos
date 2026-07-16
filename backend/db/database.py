import re

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from backend.config import settings


def normalize_db_url(url: str) -> str:
    """
    Accept connection strings exactly as providers hand them out.

    Neon/Heroku-style URLs say `postgresql://` and carry libpq params
    (`sslmode`, `channel_binding`) that the asyncpg driver rejects —
    a pasted-verbatim string must work rather than crash the app.
    """
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    if url.startswith("postgresql://"):
        url = "postgresql+asyncpg://" + url[len("postgresql://"):]
    if url.startswith("postgresql+asyncpg://"):
        url = re.sub(r"[?&]channel_binding=[^&]*", "", url)
        url = url.replace("sslmode=", "ssl=")
        # stripping the first param may leave "...&x=y" without a "?"
        if "?" not in url and "&" in url:
            url = url.replace("&", "?", 1)
        url = url.rstrip("?")
    return url


engine = create_async_engine(
    normalize_db_url(settings.DATABASE_URL),
    echo=settings.APP_ENV == "development",
    future=True,
)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db():
    """FastAPI dependency — yields an async DB session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def create_tables():
    """Create all tables on startup (dev only)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
