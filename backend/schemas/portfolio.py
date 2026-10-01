from typing import Any, Optional

from pydantic import BaseModel, Field


class AssetAllocation(BaseModel):
    ticker: str
    name: str
    weight: float = Field(..., ge=0, le=1, description="Portfolio weight 0–1")
    category: str  # stocks / reit / fund / gold / bond / cash
    explanation: str = ""
    # What this holding is QUOTED in. The client needs it to say whether a
    # position carries currency risk for THIS reader, which is a fact about
    # the market they are in and not about the language they read: the SPY
    # copy carried "TL eriyor derdine karşı bir kalkan" in Turkish and
    # nothing at all in English, so a Turkish reader in the US market was
    # told a dollar holding shields them from lira erosion they do not have,
    # and an English reader in the Turkish market was never warned at all.
    # None when the symbol cannot be resolved — a guessed currency here
    # would print a confident wrong warning.
    currency: Optional[str] = None


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
