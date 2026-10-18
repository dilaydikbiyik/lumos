import asyncio
import logging

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.database import get_db
from backend.limiter import limiter
from backend.middleware.verify_clerk import get_current_user
from backend.repositories import user_repository
from backend.schemas.portfolio import PortfolioRecommendRequest, PortfolioRecommendResponse
from backend.markets import get_market_pack
from backend.middleware.language import language
from backend.services.portfolio_engine import build_portfolio
from backend.services import explanation_check
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
    lang: str = Depends(language),
):
    """
    POST /recommend — risk score + budget in, portfolio weights + explanation out.
    """
    # Resolve the market BEFORE building: it selects the investable universe.
    user = await user_repository.get_by_clerk_id(db, user_id)
    market = (user.market if user else None) or "TR"
    pack = get_market_pack(market)
    portfolio = await asyncio.to_thread(
        build_portfolio, body.risk_score, body.budget, market, lang
    )

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
    explanation = await asyncio.to_thread(
        explain_portfolio, portfolio, user_profile, lang, pack.currency, market
    )
    # Checked against the figures it was given before it reaches the reader.
    #
    # The allocation is a formula and the same input produces the same
    # portfolio every time; the sentence beside it is not deterministic, so
    # a test cannot stand in for this. Prose that says one thing while the
    # chart says another leaves a reader unable to tell which half to
    # believe — and they will believe the sentence, because it is the half
    # written in their own language.
    #
    # A contradiction DROPS the paragraph rather than correcting it: the
    # allocation, the chart and the formula are all still on the page, and a
    # missing explanation is a smaller failure than a confident wrong one.
    portfolio.plain_explanation = explanation_check.verified_or_dropped(
        explanation, portfolio
    )

    if portfolio.includes_reits:
        reit_text = await asyncio.to_thread(
            explain_reit_inclusion, portfolio, user_profile, lang
        )
        portfolio.metadata["reit_explanation"] = explanation_check.verified_or_dropped(
            reit_text, portfolio
        )

    logger.info(
        "recommendation_served user=%s risk=%s budget=%s reits=%s",
        user_id, body.risk_score, body.budget, portfolio.includes_reits,
    )
    return portfolio
