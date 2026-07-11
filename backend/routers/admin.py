from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.database import get_db
from backend.middleware.require_role import require_role
from backend.models.holding import Holding
from backend.models.user import User

router = APIRouter()


@router.get("/stats")
async def admin_stats(
    user_id: str = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """Operations summary — admin only: user/holding volume, today's AI usage."""
    total_users = (await db.execute(select(func.count(User.id)))).scalar()
    profiled_users = (await db.execute(
        select(func.count(User.id)).where(User.risk_score.is_not(None))
    )).scalar()
    total_holdings = (await db.execute(select(func.count(Holding.id)))).scalar()

    today = date.today().isoformat()
    messages_today = (await db.execute(
        select(func.coalesce(func.sum(User.quota_used), 0)).where(User.quota_date == today)
    )).scalar()

    by_path = dict((await db.execute(
        select(User.investment_path, func.count(User.id))
        .where(User.investment_path.is_not(None))
        .group_by(User.investment_path)
    )).all())

    return {
        "total_users": total_users,
        "profiled_users": profiled_users,
        "total_holdings": total_holdings,
        "ai_messages_today": messages_today,
        "users_by_path": by_path,
    }


from pydantic import BaseModel  # noqa: E402


class PlanUpdate(BaseModel):
    plan: str


@router.patch("/users/{clerk_user_id}/plan")
async def set_user_plan(
    clerk_user_id: str,
    body: PlanUpdate,
    admin_id: str = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """
    Billing integration point: a payment webhook (Stripe/Iyzico) or an
    admin flips the plan — model chain and quota adapt automatically.
    """
    from fastapi import HTTPException

    from backend.repositories import user_repository
    from backend.services.ai_tiers import AI_TIERS

    if body.plan not in AI_TIERS:
        raise HTTPException(status_code=422, detail=f"Unknown plan '{body.plan}'. Available: {list(AI_TIERS)}")

    user = await user_repository.get_or_create(db, clerk_user_id)
    user.plan = body.plan
    await db.flush()
    return {"clerk_user_id": clerk_user_id, "plan": user.plan}
