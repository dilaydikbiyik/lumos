import asyncio

from fastapi import APIRouter, Depends, Request
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
from backend.services.goal_planner import progress_and_drift, required_monthly_contribution
from backend.services.listing_bridge import build_listing_links
from backend.services.rent_vs_buy import compare_rent_vs_buy

router = APIRouter()


@router.post("/rent-vs-buy")
@limiter.limit("20/minute")
async def rent_vs_buy(
    request: Request,
    body: RentVsBuyRequest,
    user_id: str = Depends(get_current_user),
):
    """Rent or buy? — two honest side-by-side projections of the SAME home."""
    return compare_rent_vs_buy(
        body.down_payment, body.monthly_rent, body.years, home_price=body.home_price,
    )


@router.post("/goal-plan")
@limiter.limit("20/minute")
async def goal_plan(
    request: Request,
    body: GoalPlanRequest,
    user_id: str = Depends(get_current_user),
):
    """Required monthly contribution to hit a target amount by a deadline."""
    return required_monthly_contribution(body.target_amount, body.years, body.current_savings)


@router.post("/goal-progress")
@limiter.limit("20/minute")
async def goal_progress(
    request: Request,
    body: GoalProgressRequest,
    user_id: str = Depends(get_current_user),
):
    """Drift check: at the user's actual contribution rate, will they make the deadline?"""
    return progress_and_drift(
        body.target_amount, body.years_remaining,
        body.current_savings, body.actual_monthly_contribution,
    )


@router.get("/region-intelligence")
@limiter.limit("20/minute")
async def region_intelligence(
    request: Request,
    horizon_years: int = 1,
    user_id: str = Depends(get_current_user),
):
    """
    Appreciation potential — NUTS2 regions ranked by housing-index
    appreciation, nominal AND real (inflation-adjusted). Region-level
    honesty: no street/parcel claims, past != future.
    """
    from backend.services.region_intelligence import rank_regions

    horizon_years = min(max(horizon_years, 1), 3)
    return rank_regions(horizon_years)


@router.post("/listing-links")
@limiter.limit("20/minute")
async def listing_links(
    request: Request,
    body: ListingBridgeRequest,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Filter-ready deep links to real estate portals — no scraping, no listing data stored."""
    from backend.repositories import user_repository

    user = await user_repository.get_or_create(db, user_id)
    return {"links": build_listing_links(body.il, body.ilce, body.asset_type, market=user.market, detail=body.detail)}


@router.post("/projection/asset")
@limiter.limit("15/minute")
async def asset_projection(
    request: Request,
    body: AssetProjectionRequest,
    user_id: str = Depends(get_current_user),
):
    """
    Future scenarios — not a forecast: the distribution of every N-year
    window in the asset's own history (bad/typical/good), applied to the
    user's own amount.
    """
    from backend.services.projection import project_asset
    # project_asset fetches yfinance price history (blocking HTTP)
    return await asyncio.to_thread(project_asset, body.ticker.upper(), body.amount, body.years)


@router.post("/projection/region")
@limiter.limit("15/minute")
async def region_projection(
    request: Request,
    body: RegionProjectionRequest,
    user_id: str = Depends(get_current_user),
):
    """Region scenario band — TCMB housing-index window distribution + real terms."""
    from backend.services.projection import project_region
    return await asyncio.to_thread(project_region, body.region_code, body.amount, body.years)


@router.post("/projection/portfolio")
@limiter.limit("15/minute")
async def portfolio_projection(
    request: Request,
    body: PortfolioProjectionRequest,
    user_id: str = Depends(get_current_user),
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
    return await asyncio.to_thread(project_portfolio, body.weights, body.amount, body.years)


@router.get("/province-intelligence")
@limiter.limit("20/minute")
async def province_intelligence(
    request: Request,
    horizon_years: int = 3,
    user_id: str = Depends(get_current_user),
):
    """
    Per-province housing prices (TCMB unit price, TL/m²) — 81 provinces
    ranked by 1/3/5-year nominal + real appreciation.
    """
    from backend.services.province_intelligence import rank_provinces

    return rank_provinces(horizon_years)


@router.post("/projection/province")
@limiter.limit("15/minute")
async def province_projection(
    request: Request,
    body: RegionProjectionRequest,  # the region_code field carries a province code here (e.g. MUGLA)
    user_id: str = Depends(get_current_user),
):
    """Province scenario band — window distribution of 16 years of unit prices."""
    from backend.services.province_intelligence import project_province
    return await asyncio.to_thread(project_province, body.region_code.upper(), body.amount, body.years)
