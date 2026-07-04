from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.database import get_db
from backend.middleware.verify_clerk import get_current_user
from backend.repositories import holding_repository, user_repository
from backend.schemas.holding import (
    OFF_EXCHANGE_TYPES,
    CashErosion,
    HoldingCreate,
    HoldingRead,
    HoldingUpdate,
    PortfolioSummary,
)
from backend.services import inflation_service

router = APIRouter()


def _current_value(holding) -> float:
    """Best-known value: manual valuation wins, else purchase price."""
    if holding.manual_current_value is not None:
        return holding.manual_current_value
    return holding.purchase_amount


@router.get("", response_model=list[HoldingRead])
async def list_holdings(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user = await user_repository.get_or_create(db, user_id)
    return await holding_repository.list_for_user(db, user.id)


@router.post("", response_model=HoldingRead, status_code=201)
async def create_holding(
    body: HoldingCreate,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if body.asset_type not in OFF_EXCHANGE_TYPES and not body.ticker:
        raise HTTPException(
            status_code=422,
            detail="Exchange-traded assets (stock/fund/etf/gold/crypto) require a ticker.",
        )
    user = await user_repository.get_or_create(db, user_id)
    return await holding_repository.create(db, user.id, body.model_dump())


@router.patch("/{holding_id}", response_model=HoldingRead)
async def update_holding(
    holding_id: int,
    body: HoldingUpdate,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user = await user_repository.get_or_create(db, user_id)
    holding = await holding_repository.get_for_user(db, user.id, holding_id)
    if holding is None:
        raise HTTPException(status_code=404, detail="Holding not found.")
    changes = body.model_dump(exclude_unset=True)
    return await holding_repository.update(db, holding, changes)


@router.delete("/{holding_id}", status_code=204)
async def delete_holding(
    holding_id: int,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user = await user_repository.get_or_create(db, user_id)
    holding = await holding_repository.get_for_user(db, user.id, holding_id)
    if holding is None:
        raise HTTPException(status_code=404, detail="Holding not found.")
    await holding_repository.delete(db, holding)


@router.get("/health")
async def health_score(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Fener: 0-100 portfolio health with plain-language notes."""
    from backend.services.health_score import compute_health

    user = await user_repository.get_or_create(db, user_id)
    holdings = await holding_repository.list_for_user(db, user.id)
    by_type: dict[str, float] = {}
    for h in holdings:
        by_type[h.asset_type] = by_type.get(h.asset_type, 0.0) + _current_value(h)
    return compute_health(by_type)


@router.get("/summary", response_model=PortfolioSummary)
async def portfolio_summary(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Wealth snapshot: total invested, best-known current value, and how much
    of the declared budget is still uninvested.
    """
    user = await user_repository.get_or_create(db, user_id)
    holdings = await holding_repository.list_for_user(db, user.id)

    total_invested = sum(h.purchase_amount for h in holdings)
    total_value = sum(_current_value(h) for h in holdings)
    by_type: dict[str, float] = {}
    for h in holdings:
        by_type[h.asset_type] = by_type.get(h.asset_type, 0.0) + _current_value(h)

    remaining = None
    if user.budget is not None:
        remaining = max(user.budget - total_invested, 0.0)

    # "Param eriyor mu?" — idle cash + uninvested budget both lose real value monthly
    idle_cash = by_type.get("cash", 0.0) + (remaining or 0.0)
    cash_erosion = None
    if idle_cash > 0:
        erosion = inflation_service.monthly_cash_erosion(idle_cash)
        cash_erosion = CashErosion(**erosion)

    return PortfolioSummary(
        total_budget=user.budget,
        total_invested=total_invested,
        remaining_budget=remaining,
        total_current_value=total_value,
        holdings_count=len(holdings),
        by_type=by_type,
        cash_erosion=cash_erosion,
    )
