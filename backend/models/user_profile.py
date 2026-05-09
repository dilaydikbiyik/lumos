from pydantic import BaseModel, Field
from typing import Literal


class RiskProfileAnswers(BaseModel):
    """5 questions collected during the onboarding conversation."""
    budget: float = Field(..., gt=0, description="Available investment budget in TRY")
    time_horizon: Literal["short", "medium", "long"] = Field(
        ..., description="short (<2yr) / medium (2-10yr) / long (>10yr)"
    )
    loss_tolerance: Literal["low", "medium", "high"] = Field(
        ..., description="How much loss can the user tolerate?"
    )
    goal: Literal["preservation", "growth", "income", "speculation"] = Field(
        ..., description="Primary investment goal"
    )
    experience: Literal["none", "beginner", "intermediate", "advanced"] = Field(
        ..., description="User's investment experience level"
    )


class RiskProfileResponse(BaseModel):
    """Computed risk profile returned to the client."""
    risk_score: float = Field(..., ge=1, le=10, description="Risk score from 1 (safe) to 10 (aggressive)")
    label: str = Field(..., description="Human-readable label: Conservative / Moderate / Aggressive")
    summary: str = Field(..., description="Brief explanation of the score")
    answers: RiskProfileAnswers
