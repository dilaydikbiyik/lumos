from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.database import get_db
from backend.limiter import limiter
from backend.middleware.verify_clerk import get_current_user
from backend.repositories import user_repository
from backend.services.practice_mode import practice_snapshot

router = APIRouter()


class PracticeSnapshotRequest(BaseModel):
    weights: dict[str, float] = Field(..., min_length=1, max_length=15)
    # Omitted: the market's own practice sum (MarketPack.practice_budget).
    virtual_budget: float | None = Field(None, gt=0)


@router.post("/snapshot")
@limiter.limit("20/minute")
async def snapshot(
    request: Request,
    body: PracticeSnapshotRequest,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Practice portfolio — real market data, fake money. The bridge between
    'I understand the recommendation' and 'I'm ready to invest for real'.
    """
    user = await user_repository.get_or_create(db, user_id)
    return practice_snapshot(body.weights, body.virtual_budget, user.market or "TR")
