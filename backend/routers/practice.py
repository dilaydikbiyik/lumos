from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field

from backend.limiter import limiter
from backend.middleware.verify_clerk import get_current_user
from backend.services.practice_mode import DEFAULT_PRACTICE_BUDGET, practice_snapshot

router = APIRouter()


class PracticeSnapshotRequest(BaseModel):
    weights: dict[str, float] = Field(..., min_length=1, max_length=15)
    virtual_budget: float = Field(DEFAULT_PRACTICE_BUDGET, gt=0)


@router.post("/snapshot")
@limiter.limit("20/minute")
async def snapshot(
    request: Request,
    body: PracticeSnapshotRequest,
    user_id: str = Depends(get_current_user),
):
    """
    Practice portfolio — real market data, fake money. The bridge between
    'I understand the recommendation' and 'I'm ready to invest for real'.
    """
    return practice_snapshot(body.weights, body.virtual_budget)
