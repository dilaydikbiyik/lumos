from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.database import get_db
from backend.middleware.language import language
from backend.middleware.verify_clerk import get_current_user
from backend.repositories import user_repository
from backend.schemas.user_profile import RiskProfileAnswers, RiskProfileResponse
from backend.services.risk_engine import compute_risk_score

router = APIRouter()


@router.get("/questions")
async def quiz_questions(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    lang: str = Depends(language),
):
    """
    The risk quiz as data, so the client can render it as real inputs.

    The nine questions were written down in the system prompt and a frontier
    model was paid to read them out — one chat call per answer, on the most
    restricted tier, roughly ten calls from a fifty-a-day quota before a new
    user saw anything. Served as data, the whole quiz costs zero model calls
    and the answers arrive already shaped like RiskProfileAnswers, with
    nothing to extract and nothing to parse.

    The conversational path is untouched and still offered, because some
    people would rather talk than fill in a form.
    """
    from backend.markets import get_market_pack
    from backend.services.quiz_questions import questions

    user = await user_repository.get_or_create(db, user_id)
    pack = get_market_pack(user.market or "TR")
    return {
        "questions": questions(lang, pack.currency),
        "currency": pack.currency,
    }


@router.post("", response_model=RiskProfileResponse)
async def save_profile(
    answers: RiskProfileAnswers,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    lang: str = Depends(language),
):
    """
    POST /profile — receive risk-profiling answers, compute risk score,
    persist to DB linked to the Clerk user ID.
    """
    profile = compute_risk_score(answers, lang)
    await user_repository.save_risk_profile(
        db, user_id,
        risk_score=profile.risk_score,
        budget=answers.budget,
        monthly_contribution=answers.monthly_contribution,
        time_horizon=answers.time_horizon,
        loss_tolerance=answers.loss_tolerance,
        goal=answers.goal,
        experience=answers.experience,
        age=answers.age,
        income_stability=answers.income_stability,
        high_interest_debt=answers.high_interest_debt,
    )
    return profile


@router.get("", response_model=Optional[RiskProfileResponse])
async def get_profile(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    lang: str = Depends(language),
):
    """GET /profile — return the saved risk profile for the current user."""
    user = await user_repository.get_by_clerk_id(db, user_id)
    if user is None or user.risk_score is None:
        return None

    # Recompute with ALL stored answers — age/income modifiers included,
    # so the score matches the quiz-time score exactly (consistency = trust).
    answers = RiskProfileAnswers(
        budget=user.budget,
        time_horizon=user.time_horizon,
        loss_tolerance=user.loss_tolerance,
        goal=user.goal,
        experience=user.experience,
        age=user.age,
        income_stability=user.income_stability,
        high_interest_debt=user.high_interest_debt,
    )
    return compute_risk_score(answers, lang)
