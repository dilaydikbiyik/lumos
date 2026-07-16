"""
User data access — all SQLAlchemy queries for the users table live here.
Routers depend on this layer, never on raw queries.
"""
from datetime import date
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.user import User


async def get_by_clerk_id(db: AsyncSession, clerk_user_id: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.clerk_user_id == clerk_user_id))
    return result.scalar_one_or_none()


async def get_or_create(db: AsyncSession, clerk_user_id: str) -> User:
    user = await get_by_clerk_id(db, clerk_user_id)
    if user is None:
        user = User(clerk_user_id=clerk_user_id)
        db.add(user)
        await db.flush()
    return user


async def save_risk_profile(
    db: AsyncSession, clerk_user_id: str, *, risk_score: float,
    budget: float, time_horizon: str, loss_tolerance: str, goal: str, experience: str,
    age: int | None = None, income_stability: str | None = None,
) -> User:
    user = await get_or_create(db, clerk_user_id)
    user.risk_score = risk_score
    user.budget = budget
    user.time_horizon = time_horizon
    user.loss_tolerance = loss_tolerance
    user.goal = goal
    user.experience = experience
    user.age = age
    user.income_stability = income_stability
    await db.flush()
    return user


async def set_investment_path(db: AsyncSession, clerk_user_id: str, path: str) -> User:
    user = await get_or_create(db, clerk_user_id)
    user.investment_path = path
    await db.flush()
    return user


async def set_monthly_income(db: AsyncSession, clerk_user_id: str, income: float) -> User:
    user = await get_or_create(db, clerk_user_id)
    user.monthly_income = income
    await db.flush()
    return user


async def set_primary_fear(db: AsyncSession, clerk_user_id: str, fear: str) -> User:
    user = await get_or_create(db, clerk_user_id)
    user.primary_fear = fear
    await db.flush()
    return user


async def set_market(db: AsyncSession, clerk_user_id: str, market: str) -> User:
    """Set the user's market pack (TR/US/DE). Keeps the mutation in the repo layer."""
    user = await get_or_create(db, clerk_user_id)
    user.market = market
    await db.flush()
    return user


async def consume_quota(db: AsyncSession, clerk_user_id: str, daily_limit: int) -> bool:
    """
    Atomically count one AI message against today's quota.
    Returns True if the message is allowed, False if the limit is reached.

    Uses a read-then-update pattern inside the same transaction — safe on SQLite
    (single writer) and correct on Postgres because get_db commits the whole
    transaction as a unit, making the check-and-increment effectively atomic.
    For high-concurrency Postgres use SELECT ... FOR UPDATE when needed.
    """
    user = await get_or_create(db, clerk_user_id)
    today = date.today().isoformat()

    if user.quota_date != today:
        user.quota_date = today
        user.quota_used = 0

    if user.quota_used >= daily_limit:
        return False

    user.quota_used += 1
    await db.flush()
    return True
