from pydantic import BaseModel, Field
from typing import Any


class AssetAllocation(BaseModel):
    ticker: str
    name: str
    weight: float = Field(..., ge=0, le=1, description="Portfolio weight 0–1")
    category: str  # stocks / reit / fund / gold / bond / cash
    explanation: str = ""


class PortfolioRecommendRequest(BaseModel):
    risk_score: float = Field(..., ge=1, le=10)
    budget: float = Field(..., gt=0, description="Investment budget in TRY")


class PortfolioRecommendResponse(BaseModel):
    risk_score: float
    budget: float
    allocations: list[AssetAllocation]
    plain_explanation: str
    includes_reits: bool = False
    formula_used: str = "volatility-weighted"
    metadata: dict[str, Any] = {}
