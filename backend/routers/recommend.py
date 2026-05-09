from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.db.database import get_db
from backend.middleware.verify_clerk import get_current_user
from backend.models.portfolio import PortfolioRecommendRequest, PortfolioRecommendResponse
from backend.models.user import User
from backend.services.portfolio_engine import build_portfolio
from backend.services.explainer import explain_portfolio, explain_reit_inclusion

router = APIRouter()


@router.post("", response_model=PortfolioRecommendResponse)
async def recommend(
    body: PortfolioRecommendRequest,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    POST /recommend — risk score + budget in, portfolio weights + explanation out.
    """
    portfolio = build_portfolio(risk_score=body.risk_score, budget=body.budget)

    # Fetch user profile for personalised explanation
    result = await db.execute(select(User).where(User.clerk_user_id == user_id))
    user = result.scalar_one_or_none()
    user_profile = {}
    if user:
        user_profile = {
            "time_horizon": user.time_horizon,
            "loss_tolerance": user.loss_tolerance,
            "goal": user.goal,
            "experience": user.experience,
        }

    # Generate plain-language explanation
    portfolio.plain_explanation = explain_portfolio(portfolio, user_profile)

    # Add REIT explanation if applicable
    if portfolio.includes_reits:
        reit_text = explain_reit_inclusion(portfolio, user_profile)
        portfolio.metadata["reit_explanation"] = reit_text

    return portfolio
