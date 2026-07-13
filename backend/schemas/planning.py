from typing import Literal, Optional

from pydantic import BaseModel, Field


class RentVsBuyRequest(BaseModel):
    down_payment: float = Field(..., gt=0, description="Cash available now (peşinat/birikim)")
    monthly_rent: float = Field(..., gt=0, description="Current monthly rent for the same home")
    years: int = Field(..., ge=1, le=40)
    # Optional: the real property price. If omitted it's estimated from the rent
    # so buy and rent describe the SAME home (consistency).
    home_price: Optional[float] = Field(None, gt=0, description="Property price (optional; estimated from rent if absent)")


class GoalPlanRequest(BaseModel):
    target_amount: float = Field(..., gt=0)
    years: float = Field(..., gt=0, le=50)
    current_savings: float = Field(0.0, ge=0)


class GoalProgressRequest(BaseModel):
    target_amount: float = Field(..., gt=0)
    years_remaining: float = Field(..., gt=0, le=50)
    current_savings: float = Field(..., ge=0)
    actual_monthly_contribution: float = Field(..., ge=0)


class ListingBridgeRequest(BaseModel):
    il: str = Field(..., min_length=2, max_length=40)
    ilce: str = Field("", max_length=40)
    asset_type: str = Field("arsa", pattern="^(arsa|daire|konut)$")
    # Micro-location like a village/quarter — the "Keşan Çeribaşı köyü" realism case
    detail: str = Field("", max_length=60)


class AssetProjectionRequest(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=20)
    amount: float = Field(..., gt=0)
    years: Literal[1, 3, 5] = 5


class RegionProjectionRequest(BaseModel):
    # Carries a NUTS2 code (TP.KFE.TR51) or a province code (MUGLA)
    region_code: str = Field(..., min_length=2, max_length=20)
    amount: float = Field(..., gt=0)
    years: Literal[1, 2, 3, 5] = 3


class PortfolioProjectionRequest(BaseModel):
    weights: dict[str, float] = Field(..., min_length=1, max_length=15)
    amount: float = Field(..., gt=0)
    years: Literal[1, 3, 5] = 5
