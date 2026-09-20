import asyncio

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.database import get_db
from backend.limiter import limiter
from backend.middleware.verify_clerk import get_current_user
from backend.schemas.planning import (
    AssetProjectionRequest,
    PortfolioProjectionRequest,
    RegionProjectionRequest,
    GoalPlanRequest,
    GoalProgressRequest,
    ListingBridgeRequest,
    RentVsBuyRequest,
)
from backend.repositories import user_repository
from backend.middleware.language import language
from backend.services.goal_planner import progress_and_drift, required_monthly_contribution
from backend.services.listing_bridge import build_listing_links
from backend.services.rent_vs_buy import compare_rent_vs_buy

router = APIRouter()


async def _market_of(db: AsyncSession, user_id: str) -> str:
    """
    The user's market drives every rate below. Mortgage rates, transfer taxes
    and inflation are facts about a country, not constants: running a German
    buyer through Türkiye's 39% mortgage produced a confident wrong answer.
    """
    user = await user_repository.get_or_create(db, user_id)
    return user.market or "TR"


@router.post("/rent-vs-buy")
@limiter.limit("20/minute")
async def rent_vs_buy(
    request: Request,
    body: RentVsBuyRequest,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    lang: str = Depends(language),
):
    """Rent or buy? — two honest side-by-side projections of the SAME home."""
    market = await _market_of(db, user_id)
    return await asyncio.to_thread(
        compare_rent_vs_buy,
        body.down_payment, body.monthly_rent, body.years, body.home_price,
        None, None, None,
        body.mortgage_annual_rate_pct,
        body.mortgage_term_years,
        body.down_payment_includes_costs,
        market,
        lang,
    )


@router.post("/goal-plan")
@limiter.limit("20/minute")
async def goal_plan(
    request: Request,
    body: GoalPlanRequest,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Required monthly contribution to hit a target amount by a deadline."""
    market = await _market_of(db, user_id)
    return await asyncio.to_thread(
        required_monthly_contribution,
        body.target_amount, body.years, body.current_savings, None, market,
    )


@router.post("/goal-progress")
@limiter.limit("20/minute")
async def goal_progress(
    request: Request,
    body: GoalProgressRequest,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Drift check: at the user's actual contribution rate, will they make the deadline?"""
    market = await _market_of(db, user_id)
    return await asyncio.to_thread(
        progress_and_drift,
        body.target_amount, body.years_remaining,
        body.current_savings, body.actual_monthly_contribution, None, market,
    )


@router.get("/region-intelligence")
@limiter.limit("20/minute")
async def region_intelligence(
    request: Request,
    horizon_years: int = 1,
    user_id: str = Depends(get_current_user),
    lang: str = Depends(language),
):
    """
    Appreciation potential — NUTS2 regions ranked by housing-index
    appreciation, nominal AND real (inflation-adjusted). Region-level
    honesty: no street/parcel claims, past != future.
    """
    from backend.services.region_intelligence import rank_regions

    horizon_years = min(max(horizon_years, 1), 3)
    return await asyncio.to_thread(rank_regions, horizon_years, lang)


@router.post("/listing-links")
@limiter.limit("20/minute")
async def listing_links(
    request: Request,
    body: ListingBridgeRequest,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Filter-ready deep links to real estate portals — no scraping, no listing data stored."""
    
    user = await user_repository.get_or_create(db, user_id)
    return {"links": build_listing_links(body.il, body.ilce, body.asset_type, market=user.market, detail=body.detail)}


async def _scenario_context(db, user_id: str, lang: str):
    """
    The current-context sentence for a scenario card, or None.

    None rather than filler: a card with no sentence reads fine, a card with
    an invented one is the app making something up next to numbers it went to
    some trouble to measure honestly.
    """
    from backend.services.news_service import context_sentence

    try:
        user = await user_repository.get_or_create(db, user_id)
        return await asyncio.to_thread(
            context_sentence, user.investment_path or "hybrid",
            user.market or "TR", lang,
        )
    except Exception:
        return None


@router.post("/projection/asset")
@limiter.limit("15/minute")
async def asset_projection(
    request: Request,
    body: AssetProjectionRequest,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    lang: str = Depends(language),
):
    """
    Future scenarios — not a forecast: the distribution of every N-year
    window in the asset's own history (bad/typical/good), applied to the
    user's own amount.
    """
    from backend.services.projection import project_asset

    # project_asset fetches yfinance price history (blocking HTTP)
    result = await asyncio.to_thread(
        project_asset, body.ticker.upper(), body.amount, body.years, lang
    )

    # One calm sentence about right now, BESIDE the band and never into it.
    # The band is the distribution of this asset's own history; letting a
    # model touch those figures would turn a measurement into a forecast,
    # which is the one thing every projection here refuses to be.
    result["context"] = await _scenario_context(db, user_id, lang)
    return result


@router.post("/projection/region")
@limiter.limit("15/minute")
async def region_projection(
    request: Request,
    body: RegionProjectionRequest,
    user_id: str = Depends(get_current_user),
    lang: str = Depends(language),
):
    """Region scenario band — TCMB housing-index window distribution + real terms."""
    from backend.services.projection import project_region
    return await asyncio.to_thread(
        project_region, body.region_code, body.amount, body.years, lang
    )


@router.post("/projection/portfolio")
@limiter.limit("15/minute")
async def portfolio_projection(
    request: Request,
    body: PortfolioProjectionRequest,
    user_id: str = Depends(get_current_user),
    lang: str = Depends(language),
):
    """
    Combined portfolio scenario band — the weighted whole-portfolio
    distribution over its own history, not a single asset (shows the
    effect of diversification).
    """
    from backend.services.projection import project_portfolio

    total = sum(body.weights.values())
    if not 0.95 <= total <= 1.05:
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail=f"Weights must sum to ~1 (got {total:.2f}).")
    return await asyncio.to_thread(
        project_portfolio, body.weights, body.amount, body.years, lang
    )


@router.get("/province-intelligence")
@limiter.limit("20/minute")
async def province_intelligence(
    request: Request,
    horizon_years: int = 3,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    lang: str = Depends(language),
):
    """
    Sub-national housing breakdown, ranked by 1/3/5-year nominal + real
    appreciation: 81 provinces in Türkiye (TCMB unit prices, TL/m²) or 50
    states plus DC in the US (FHFA index via FRED). The payload says which
    kind of number it carries.
    """
    from backend.i18n import t as translate
    from backend.services.province_intelligence import rank_provinces

    market = await _market_of(db, user_id)
    result = await asyncio.to_thread(rank_provinces, horizon_years, market, lang)

    # Which window the READER should be looking at. A table ranked over one
    # year and a table ranked over five answer different questions, and a
    # default of three was answering neither: somebody who can wait twenty
    # years should not be shown last year's movers, and somebody who needs
    # the money in three should not be shown a twenty-year story.
    user = await user_repository.get_or_create(db, user_id)
    suggested = {"short": 1, "medium": 3, "long": 5}.get(user.time_horizon or "", 3)
    result["suggested_horizon"] = suggested
    result["horizon_note"] = translate(
        f"region.horizon.{user.time_horizon or 'unknown'}", lang, years=suggested
    )
    return result


@router.post("/projection/province")
@limiter.limit("15/minute")
async def province_projection(
    request: Request,
    body: RegionProjectionRequest,  # region_code carries an area code here (MUGLA, CA)
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    lang: str = Depends(language),
):
    """Area scenario band — window distribution over that area's own history."""
    from backend.services.province_intelligence import project_province

    market = await _market_of(db, user_id)
    return await asyncio.to_thread(
        project_province, body.region_code.upper(), body.amount, body.years,
        market, lang,
    )


@router.get("/budget-split")
@limiter.limit("30/minute")
async def budget_split_plan(
    request: Request,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    lang: str = Depends(language),
):
    """
    "I have this much — what goes where?"

    The entry point for the hybrid and undecided paths. A single-world path
    still gets an answer, but the whole budget is planned inside the world
    that reader chose: that is the point of having chosen it.

    Rule-based and explained, like every other planning engine here. Someone
    told to put six tenths of their savings into a flat deserves the
    reasoning in terms they can push back on.
    """
    from backend.i18n import t as translate
    from backend.markets import get_market_pack
    from backend.services import budget_split as split_service

    user = await user_repository.get_or_create(db, user_id)
    pack = get_market_pack(user.market or "TR")

    # What is already in property. Without this the plan keeps telling
    # somebody who has just bought a flat to put another 40% into property —
    # the moment a plan stops being believable, and the moment they most need
    # the rest of it replanned.
    from backend.repositories import holding_repository
    from backend.services.holdings_valuation import REAL_ESTATE_TYPES

    holdings = await holding_repository.list_for_user(db, user.id)
    committed = sum(
        (h.manual_current_value or h.purchase_amount or 0)
        for h in holdings if h.asset_type in REAL_ESTATE_TYPES
    )

    result = split_service.split(
        budget=user.budget or 0,
        risk_score=user.risk_score,
        # Outgoings, NOT income: the reserve is six months of spending.
        monthly_outgoings=user.monthly_outgoings,
        entry_threshold=pack.property_entry_threshold,
        committed_property=committed,
        path=user.investment_path or "hybrid",
    )

    payload = result.as_dict()
    payload["reasons"] = [
        translate(key, lang, months=split_service.RESERVE_MONTHS)
        for key in payload["reasons"]
    ]
    payload["currency"] = pack.currency
    payload["path"] = user.investment_path or "hybrid"
    return payload


@router.get("/property-vs-portfolio")
@limiter.limit("20/minute")
async def property_vs_portfolio_compare(
    request: Request,
    region: str,
    amount: float,
    period: str = "5y",
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    lang: str = Depends(language),
):
    """
    The same amount, the same window, both worlds — as it actually went.

    Backward-looking on both sides on purpose: a forecast comparison would be
    two guesses dressed as an answer, and whichever side had the friendlier
    assumptions would always win.
    """
    from backend.services import property_vs_portfolio
    from backend.services.portfolio_engine import build_portfolio

    user = await user_repository.get_or_create(db, user_id)
    market = user.market or "TR"

    # The portfolio side is the reader's OWN allocation, not a generic index:
    # the question is "this amount in property or in MY portfolio".
    portfolio = await asyncio.to_thread(
        build_portfolio, user.risk_score or 5.0, amount, market, lang
    )
    weights = {a.ticker: a.weight for a in portfolio.allocations}

    return await asyncio.to_thread(
        property_vs_portfolio.compare,
        amount=amount, region_code=region, weights=weights,
        period=period, market=market, lang=lang,
    )


@router.get("/yield-comparison")
async def yield_comparison(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    lang: str = Depends(language),
):
    """Rent yield against dividend yield, with rent NET of upkeep."""
    from backend.services import property_vs_portfolio

    user = await user_repository.get_or_create(db, user_id)
    return property_vs_portfolio.yield_comparison(
        market=user.market or "TR", lang=lang
    )


@router.get("/purchase-checks")
async def purchase_checks(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    lang: str = Depends(language),
):
    """
    What to check before buying property in THIS market.

    Market-keyed, not language-keyed. The broker guide was written for
    Türkiye and keyed by language, so a German reader was told to verify an
    SPK licence — a checklist is even less forgiving, since these are the
    checks that stop somebody buying a plot they cannot build on.
    """
    from backend.content import purchase_checks as content

    user = await user_repository.get_or_create(db, user_id)
    market = user.market or "TR"
    checks = content.for_market(market, lang)

    return {
        "market": market,
        "available": checks is not None,
        "checks": checks or [],
    }


class ListingEvalRequest(BaseModel):
    area_code: str
    size_m2: float = Field(..., gt=0, le=100_000)
    asking_price: float = Field(..., gt=0)


@router.post("/listing-eval")
@limiter.limit("20/minute")
async def listing_eval(
    request: Request,
    body: ListingEvalRequest,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    lang: str = Depends(language),
):
    """
    "Is this listing a fair price?" — the asking price per m² against what
    the area actually trades at.

    Refuses in markets that publish an INDEX rather than a price level,
    because dividing an asking price by an index number produces a number
    that means nothing. A wrong verdict here costs somebody a fair property
    or an unfair price.
    """
    from backend.services import listing_eval as service

    market = await _market_of(db, user_id)
    return await asyncio.to_thread(
        service.evaluate,
        area_code=body.area_code, size_m2=body.size_m2,
        asking_price=body.asking_price, market=market, lang=lang,
    )
