import asyncio
import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.database import get_db
from backend.exceptions import AIServiceError
from backend.limiter import limiter
from backend.middleware.verify_clerk import get_current_user
from backend.repositories import user_repository
from backend.schemas.portfolio import PortfolioRecommendRequest, PortfolioRecommendResponse
from backend.markets import get_market_pack
from backend.middleware.language import language
from backend.services import explanation_check
from backend.services.explainer import explain_portfolio, explain_reit_inclusion

router = APIRouter()
logger = logging.getLogger("lumos.recommend")



async def _prose_or_nothing(fn, *args) -> str:
    """
    The model's sentence, or an empty string when the model is unavailable.

    The portfolio is a formula and needs no model; only the sentence beside
    it does. But the whole AI chain being down raised a 503 straight through
    this endpoint, so when the free-tier quota ran out — measured by
    scripts/live_smoke.py — the reader lost their RECOMMENDATION, not just
    its explanation. The one feature built to not depend on a model was
    taken down by the model being unavailable.

    Narrow on purpose: only the outage itself is absorbed. A 503 from the
    provider chain and AIServiceError mean "no sentence today"; anything
    else is a bug and still raises. The page already renders without the
    paragraph, the same way it does when explanation_check drops one.
    """
    try:
        return await asyncio.to_thread(fn, *args)
    except AIServiceError as exc:
        logger.warning("explanation skipped — AI unavailable: %s", exc)
    except HTTPException as exc:
        if exc.status_code != 503:
            raise
        logger.warning("explanation skipped — every AI provider unavailable")
    return ""

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
    # Built for the reader's chosen path: a stocks-only reader gets no
    # property fund, and a hybrid reader's portfolio is the market part of
    # their budget split rather than a second plan for the whole budget.
    from backend.services import path_portfolio

    committed = await path_portfolio.committed_property(db, user) if user else 0.0
    portfolio, _plan = await asyncio.to_thread(
        lambda: path_portfolio.build_for_path(
            user.investment_path if user else None, body.risk_score, body.budget,
            market, lang,
            monthly_outgoings=user.monthly_outgoings if user else None,
            committed_property=committed,
        )
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
    explanation = await _prose_or_nothing(
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
        reit_text = await _prose_or_nothing(
            explain_reit_inclusion, portfolio, user_profile, lang
        )
        # The REIT-specific checker, NOT the portfolio one. Its prompt
        # instructs regulatory and historical figures ("at least 90% of
        # taxable income", "~8-10% annualized over 20 years") that are not
        # portfolio weights, so the percentage rule deletes every correct
        # REIT explanation — which it did, until this line.
        portfolio.metadata["reit_explanation"] = explanation_check.reit_verified_or_dropped(
            reit_text, portfolio
        )

    logger.info(
        "recommendation_served user=%s risk=%s budget=%s reits=%s",
        user_id, body.risk_score, body.budget, portfolio.includes_reits,
    )
    return portfolio
