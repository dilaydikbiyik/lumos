from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional

from backend.db.database import get_db
from backend.middleware.verify_clerk import get_current_user
from backend.models.user import User

router = APIRouter()


class UserRead(BaseModel):
    clerk_user_id: str
    email: Optional[str]
    risk_score: Optional[float]
    budget: Optional[float]

    class Config:
        from_attributes = True


@router.get("/me", response_model=UserRead)
async def get_me(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """GET /users/me — return the current user's saved data."""
    result = await db.execute(select(User).where(User.clerk_user_id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        # Create a minimal record on first visit
        user = User(clerk_user_id=user_id)
        db.add(user)
        await db.flush()

    return user
