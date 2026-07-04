from pydantic import BaseModel, Field


class RentVsBuyRequest(BaseModel):
    down_payment: float = Field(..., gt=0)
    monthly_rent: float = Field(..., gt=0)
    years: int = Field(..., ge=1, le=40)


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
