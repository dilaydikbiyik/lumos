from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.database import get_db
from backend.limiter import limiter
from backend.middleware.require_role import require_role
from backend.middleware.verify_clerk import get_current_user
from backend.models.feedback import Feedback
from backend.repositories import user_repository

router = APIRouter()

CATEGORIES = {"bug", "confusing", "idea", "other"}


class FeedbackRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    category: str | None = Field(None, description="bug | confusing | idea | other")
    page: str | None = Field(None, max_length=200)


@router.post("")
@limiter.limit("5/minute")
async def submit_feedback(
    request: Request,
    body: FeedbackRequest,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Record a message the user sent from inside the app."""
    user = await user_repository.get_by_clerk_id(db, user_id)
    entry = Feedback(
        user_id=user.id if user else None,
        message=body.message.strip(),
        category=body.category if body.category in CATEGORIES else None,
        page=body.page,
    )
    db.add(entry)
    await db.commit()
    return {"ok": True}


@router.get("")
async def list_feedback(
    user_id: str = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """Everything users have reported, newest first — admin only."""
    rows = (await db.execute(
        select(Feedback).order_by(Feedback.created_at.desc()).limit(200)
    )).scalars().all()
    return [
        {
            "id": r.id,
            "message": r.message,
            "category": r.category,
            "page": r.page,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]
