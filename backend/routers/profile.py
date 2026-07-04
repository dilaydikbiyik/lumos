from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.database import get_db
from backend.middleware.verify_clerk import get_current_user
from backend.repositories import user_repository
from backend.schemas.user_profile import RiskProfileAnswers, RiskProfileResponse
from backend.services.risk_engine import compute_risk_score

router = APIRouter()


@router.post("", response_model=RiskProfileResponse)
async def save_profile(
    answers: RiskProfileAnswers,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    POST /profile — receive risk-profiling answers, compute risk score,
    persist to DB linked to the Clerk user ID.
    """
    profile = compute_risk_score(answers)
    await user_repository.save_risk_profile(
        db, user_id,
        risk_score=profile.risk_score,
        budget=answers.budget,
        time_horizon=answers.time_horizon,
        loss_tolerance=answers.loss_tolerance,
        goal=answers.goal,
        experience=answers.experience,
    )
    return profile


@router.get("", response_model=Optional[RiskProfileResponse])
async def get_profile(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """GET /profile — return the saved risk profile for the current user."""
    user = await user_repository.get_by_clerk_id(db, user_id)
    if user is None or user.risk_score is None:
        return None

    answers = RiskProfileAnswers(
        budget=user.budget,
        time_horizon=user.time_horizon,
        loss_tolerance=user.loss_tolerance,
        goal=user.goal,
        experience=user.experience,
    )
    return compute_risk_score(answers)
