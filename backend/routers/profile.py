from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.db.database import get_db
from backend.middleware.verify_clerk import get_current_user
from backend.models.user import User
from backend.models.user_profile import RiskProfileAnswers, RiskProfileResponse
from backend.services.risk_engine import compute_risk_score

router = APIRouter()


@router.post("", response_model=RiskProfileResponse)
async def save_profile(
    answers: RiskProfileAnswers,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    POST /profile — receive 5-question answers, compute risk score,
    persist to DB linked to the Clerk user ID.
    """
    profile = compute_risk_score(answers)

    # Upsert user record
    result = await db.execute(select(User).where(User.clerk_user_id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        user = User(clerk_user_id=user_id)
        db.add(user)

    user.risk_score = profile.risk_score
    user.budget = answers.budget
    user.time_horizon = answers.time_horizon
    user.loss_tolerance = answers.loss_tolerance
    user.goal = answers.goal
    user.experience = answers.experience

    await db.flush()
    return profile


@router.get("", response_model=RiskProfileResponse | None)
async def get_profile(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """GET /profile — return the saved risk profile for the current user."""
    result = await db.execute(select(User).where(User.clerk_user_id == user_id))
    user = result.scalar_one_or_none()

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
