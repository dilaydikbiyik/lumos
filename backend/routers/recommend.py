import asyncio
import logging

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.database import get_db
from backend.limiter import limiter
from backend.middleware.verify_clerk import get_current_user
from backend.repositories import user_repository
from backend.schemas.portfolio import PortfolioRecommendRequest, PortfolioRecommendResponse
from backend.services.portfolio_engine import build_portfolio
from backend.services.explainer import explain_portfolio, explain_reit_inclusion

router = APIRouter()
logger = logging.getLogger("lumos.recommend")


@router.post("", response_model=PortfolioRecommendResponse)
@limiter.limit("10/minute")
async def recommend(
    request: Request,
    body: PortfolioRecommendRequest,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    POST /recommend — risk score + budget in, portfolio weights + explanation out.
    """
    portfolio = build_portfolio(risk_score=body.risk_score, budget=body.budget)

    # Fetch user profile for personalised explanation
    user = await user_repository.get_by_clerk_id(db, user_id)
    user_profile = {}
    if user:
        user_profile = {
            "time_horizon": user.time_horizon,
            "loss_tolerance": user.loss_tolerance,
            "goal": user.goal,
            "experience": user.experience,
        }

    # explain_portfolio / explain_reit_inclusion call generate_text() which is
    # synchronous blocking I/O — run in a thread so the event loop stays free.
    portfolio.plain_explanation = await asyncio.to_thread(
        explain_portfolio, portfolio, user_profile
    )

    if portfolio.includes_reits:
        reit_text = await asyncio.to_thread(
            explain_reit_inclusion, portfolio, user_profile
        )
        portfolio.metadata["reit_explanation"] = reit_text

    logger.info(
        "recommendation_served user=%s risk=%s budget=%s reits=%s",
        user_id, body.risk_score, body.budget, portfolio.includes_reits,
    )
    return portfolio
