import asyncio
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.database import get_db
from backend.limiter import limiter
from backend.middleware.verify_clerk import get_current_user
from backend.repositories import user_repository
from backend.services.news_service import get_daily_digest

router = APIRouter()


@router.get("/digest")
@limiter.limit("20/minute")
async def news_digest(
    request: Request,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    'Bugün Ne Oldu?' — at most 3 calm, beginner-framed news items,
    filtered for the user's investment path. Cached per day.
    """
    user = await user_repository.get_or_create(db, user_id)
    path = user.investment_path or "hybrid"
    # get_daily_digest calls generate_text + httpx on first call (cached after)
    items = await asyncio.to_thread(get_daily_digest, path)
    return {"path": path, "items": items}
