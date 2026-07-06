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
    """Operasyon özeti — sadece admin: kullanıcı/varlık hacmi, bugünkü AI kullanımı."""
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
