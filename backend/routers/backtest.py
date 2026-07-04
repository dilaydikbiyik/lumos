from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from backend.limiter import limiter
from backend.middleware.verify_clerk import get_current_user
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
):
    """
    Time Machine: simulate holding this allocation for the chosen period.
    Returns final value, max drawdown, stagnation character per asset,
    and a chart-ready value series.
    """
    total = sum(body.weights.values())
    if not 0.95 <= total <= 1.05:
        raise HTTPException(status_code=422, detail=f"Weights must sum to ~1 (got {total:.2f}).")
    return run_backtest(body.weights, body.budget, body.period)
