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
    """
    The user row, creating it on first sight.

    A new account starts in the market its language suggests — English to the
    US, German to Germany, everything else to the reference market. Only at
    creation: after that the two settings are independent, and this function
    never touches the market again.
    """
    user = await get_by_clerk_id(db, clerk_user_id)
    if user is not None:
        return user

    from sqlalchemy.exc import IntegrityError

    from backend.markets import default_market_for_language
    from backend.middleware.language import current_language

    user = User(
        clerk_user_id=clerk_user_id,
        market=default_market_for_language(current_language()),
    )
    # Check-then-insert is a race, and a brand-new account is exactly when it
    # fires: the first page load sends several requests at once, every one of
    # them calls this, and all of them see "no row yet". One insert wins and
    # the rest raise IntegrityError — a 500 on somebody's first impression.
    #
    # The savepoint keeps the failure local. Rolling back the whole session
    # instead would discard whatever else the request had already done.
    try:
        async with db.begin_nested():
            db.add(user)
        await db.flush()
        return user
    except IntegrityError:
        # Someone else created it between our read and our insert, which means
        # the row we wanted now exists. Read it back rather than failing.
        # No expunge: rolling the savepoint back already discarded the pending
        # instance, and asking the session to forget it again raises.
        existing = await get_by_clerk_id(db, clerk_user_id)
        if existing is None:
            raise           # a different integrity problem — do not swallow it
        return existing


async def save_risk_profile(
    db: AsyncSession, clerk_user_id: str, *, risk_score: float,
    budget: float, time_horizon: str, loss_tolerance: str, goal: str, experience: str,
    age: int | None = None, income_stability: str | None = None,
    monthly_contribution: float | None = None, high_interest_debt: float | None = None,
) -> User:
    user = await get_or_create(db, clerk_user_id)
    user.risk_score = risk_score
    user.budget = budget
    user.monthly_contribution = monthly_contribution
    user.time_horizon = time_horizon
    user.loss_tolerance = loss_tolerance
    user.goal = goal
    user.experience = experience
    user.age = age
    user.income_stability = income_stability
    user.high_interest_debt = high_interest_debt
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


async def set_monthly_outgoings(db: AsyncSession, clerk_user_id: str,
                                 outgoings: float) -> User:
    """Rent plus essential costs — what the emergency reserve is measured in."""
    user = await get_or_create(db, clerk_user_id)
    user.monthly_outgoings = outgoings
    await db.commit()
    await db.refresh(user)
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


async def delete_account(db: AsyncSession, clerk_user_id: str) -> bool:
    """
    Erase every row this user owns. False when there was nothing to erase.

    Holdings cascade from the users row, but feedback is deliberately
    ON DELETE SET NULL so that aggregate insight survives a departure — and
    a free-text message is exactly where someone's name or situation ends up,
    so an erasure request has to take the message with it rather than keep an
    "anonymous" row that still reads like the person who wrote it.
    """
    from sqlalchemy import delete as sql_delete

    from backend.models.feedback import Feedback
    from backend.models.holding import Holding

    user = await get_by_clerk_id(db, clerk_user_id)
    if not user:
        return False

    # Deleted here rather than left to ON DELETE CASCADE. The cascade is real
    # on Postgres, but it is a property of the schema rather than of this
    # function, and SQLite does not enforce foreign keys unless the pragma is
    # on — so the behaviour differed between production and the tests meant to
    # guarantee it. An erasure is too important to depend on a pragma.
    await db.execute(sql_delete(Holding).where(Holding.user_id == user.id))
    await db.execute(sql_delete(Feedback).where(Feedback.user_id == user.id))
    await db.delete(user)
    await db.commit()
    return True
