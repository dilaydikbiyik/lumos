from fastapi import APIRouter, Depends, Request

from backend.limiter import limiter
from backend.middleware.verify_clerk import get_current_user
from backend.schemas.planning import (
    AssetProjectionRequest,
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
    """'Kirada mı otur, ev mi al?' — two honest side-by-side projections."""
    return compare_rent_vs_buy(body.down_payment, body.monthly_rent, body.years)


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
    'Değerlenme Potansiyeli' — NUTS2 regions ranked by housing-index
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
):
    """Filter-ready deep links to real estate portals — no scraping, no listing data stored."""
    return {"links": build_listing_links(body.il, body.ilce, body.asset_type)}


@router.post("/projection/asset")
@limiter.limit("15/minute")
async def asset_projection(
    request: Request,
    body: AssetProjectionRequest,
    user_id: str = Depends(get_current_user),
):
    """
    Gelecek senaryoları — tahmin değil: varlığın kendi geçmişindeki tüm
    N-yıllık pencerelerin dağılımı (kötü/tipik/iyi), kullanıcının kendi
    tutarına uygulanmış.
    """
    from backend.services.projection import project_asset

    return project_asset(body.ticker.upper(), body.amount, body.years)


@router.post("/projection/region")
@limiter.limit("15/minute")
async def region_projection(
    request: Request,
    body: RegionProjectionRequest,
    user_id: str = Depends(get_current_user),
):
    """Bölge senaryo bandı — TCMB konut endeksi pencere dağılımı + reel karşılık."""
    from backend.services.projection import project_region

    return project_region(body.region_code, body.amount, body.years)
