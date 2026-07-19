from pydantic import BaseModel, Field
from typing import Literal, Optional


class RiskProfileAnswers(BaseModel):
    """Structured answers collected during the risk-profiling conversation."""
    budget: float = Field(..., gt=0, description="Available investment budget in TRY")
    monthly_contribution: Optional[float] = Field(
        None, ge=0,
        description="TRY the user plans to add every month (null = one-time investment)"
    )
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
    age: Optional[int] = Field(
        None, ge=18, le=100,
        description="User age — older users get a mild risk reduction (capital preservation priority)"
    )
    income_stability: Optional[Literal["stable", "variable", "irregular"]] = Field(
        None,
        description="Income stability — irregular income lowers risk capacity"
    )
    high_interest_debt: Optional[float] = Field(
        None, ge=0,
        description=(
            "Outstanding credit-card / consumer-loan debt in TRY (null = unknown, "
            "0 = none). Carrying it makes investing a losing trade, so it is "
            "surfaced before any allocation."
        )
    )


class RiskFactor(BaseModel):
    """A single component of the score — no black box, every point is traceable."""
    factor: str          # human-readable name, e.g. "Kayıp toleransı"
    answer: str          # the user's answer, in readable form
    contribution: float  # net contribution to the score (weighted points or modifier)
    explanation: str     # why this contribution


class RiskProfileResponse(BaseModel):
    """Computed risk profile returned to the client."""
    risk_score: float = Field(..., ge=1, le=10, description="Risk score from 1 (safe) to 10 (aggressive)")
    label: str = Field(..., description="Human-readable label: Conservative / Moderate / Aggressive")
    summary: str = Field(..., description="Brief explanation of the score")
    factors: list[RiskFactor] = Field(default_factory=list, description="Skorun şeffaf dökümü")
    answers: RiskProfileAnswers
    # Present only when the user carries material high-interest debt: the
    # arithmetic showing repayment beats investing. None = nothing to say.
    debt_check: Optional[dict] = None
