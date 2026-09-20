from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.database import get_db
from backend.limiter import limiter
from backend.middleware.language import language
from backend.middleware.verify_clerk import get_current_user
from backend.repositories import user_repository
from backend.services.backtest import run_backtest

router = APIRouter()


class BacktestRequest(BaseModel):
    # ticker -> weight; must roughly sum to 1
    weights: dict[str, float] = Field(..., min_length=1, max_length=15)
    budget: float = Field(..., gt=0)
    period: Literal["1y", "3y", "5y"] = "5y"


@router.post("")
@limiter.limit("10/minute")
async def backtest(
    request: Request,
    body: BacktestRequest,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    lang: str = Depends(language),
):
    """
    Time Machine: simulate holding this allocation for the chosen period.
    Returns final value, max drawdown, stagnation character per asset,
    and a chart-ready value series.
    """
    total = sum(body.weights.values())
    if not 0.95 <= total <= 1.05:
        raise HTTPException(status_code=422, detail=f"Weights must sum to ~1 (got {total:.2f}).")

    import asyncio

    from backend.services import asset_character

    result = await asyncio.to_thread(run_backtest, body.weights, body.budget, body.period)

    # The character metrics were already computed and returned, and nothing
    # rendered them — which is the least useful place for them. A beginner
    # cannot read "-42% over 18 months" and know whether that is survivable
    # for THEM, so each asset is judged against their own answers.
    user = await user_repository.get_or_create(db, user_id)
    result["per_asset"] = asset_character.describe_all(
        result.get("per_asset") or {},
        loss_tolerance=user.loss_tolerance,
        time_horizon=user.time_horizon,
        lang=lang,
    )
    return result
