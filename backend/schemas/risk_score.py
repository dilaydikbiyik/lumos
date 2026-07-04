from pydantic import BaseModel, Field
from datetime import datetime


class RiskScoreCreate(BaseModel):
    clerk_user_id: str
    risk_score: float = Field(..., ge=1, le=10)
    budget: float
    time_horizon: str
    loss_tolerance: str
    goal: str
    experience: str


class RiskScoreRead(BaseModel):
    risk_score: float
    label: str
    budget: float
    created_at: datetime

    class Config:
        from_attributes = True
