from typing import Literal, Optional

from pydantic import BaseModel, Field
from backend.schemas.limits import MAX_AMOUNT, Weight


class RentVsBuyRequest(BaseModel):
    down_payment: float = Field(..., gt=0, le=MAX_AMOUNT, description="Cash available now (peşinat/birikim)")
    monthly_rent: float = Field(..., gt=0, le=MAX_AMOUNT, description="Current monthly rent for the same home")
    years: int = Field(..., ge=1, le=40)
    # Optional: the real property price. If omitted it's estimated from the rent
    # so buy and rent describe the SAME home (consistency).
    home_price: Optional[float] = Field(None, gt=0, le=MAX_AMOUNT, description="Property price (optional; estimated from rent if absent)")
    # Loan terms differ hugely per bank and per campaign, so let the user use
    # the offer they actually have. Both default to the planning assumptions.
    mortgage_annual_rate_pct: Optional[float] = Field(None, gt=0, le=200, description="Mortgage interest rate, %/year")
    mortgage_term_years: Optional[int] = Field(None, ge=1, le=30, description="Mortgage term in years")
    # True = down_payment is all the cash the user has, so closing costs come
    # out of it rather than being found on top.
    down_payment_includes_costs: bool = False


class GoalPlanRequest(BaseModel):
    target_amount: float = Field(..., gt=0, le=MAX_AMOUNT)
    years: float = Field(..., gt=0, le=50)
    current_savings: float = Field(0.0, ge=0, le=MAX_AMOUNT)


class GoalProgressRequest(BaseModel):
    target_amount: float = Field(..., gt=0, le=MAX_AMOUNT)
    years_remaining: float = Field(..., gt=0, le=50)
    current_savings: float = Field(..., ge=0, le=MAX_AMOUNT)
    actual_monthly_contribution: float = Field(..., ge=0, le=MAX_AMOUNT)


class ListingBridgeRequest(BaseModel):
    il: str = Field(..., min_length=2, max_length=40)
    ilce: str = Field("", max_length=40)
    asset_type: str = Field("arsa", pattern="^(arsa|daire|konut)$")
    # Micro-location like a village/quarter — the "Keşan Çeribaşı köyü" realism case
    detail: str = Field("", max_length=60)


class AssetProjectionRequest(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=20)
    amount: float = Field(..., gt=0, le=MAX_AMOUNT)
    years: Literal[1, 3, 5] = 5


class RegionProjectionRequest(BaseModel):
    # Carries a NUTS2 code (TP.KFE.TR51) or a province code (MUGLA)
    region_code: str = Field(..., min_length=2, max_length=20)
    amount: float = Field(..., gt=0, le=MAX_AMOUNT)
    years: Literal[1, 2, 3, 5] = 3


class PortfolioProjectionRequest(BaseModel):
    weights: dict[str, Weight] = Field(..., min_length=1, max_length=15)
    amount: float = Field(..., gt=0, le=MAX_AMOUNT)
    years: Literal[1, 3, 5] = 5
