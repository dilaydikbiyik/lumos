from datetime import date

import logging

from fastapi import APIRouter, Depends, Request
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth import permissions as perms
from backend.db.database import get_db
from backend.middleware.require_role import require_permission
from backend.models.holding import Holding
from backend.models.user import User

router = APIRouter()
logger = logging.getLogger("lumos.admin")


@router.get("/stats")
async def admin_stats(
    user_id: str = Depends(require_permission(perms.STATS_READ)),
    db: AsyncSession = Depends(get_db),
):
    """Operations summary: user/holding volume, today's AI usage."""
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


class RoleUpdate(BaseModel):
    role: str


@router.patch("/users/{clerk_user_id}/plan")
async def set_user_plan(
    clerk_user_id: str,
    body: PlanUpdate,
    admin_id: str = Depends(require_permission(perms.PLANS_WRITE)),
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


# ── Role administration ───────────────────────────────────────────────────────

@router.get("/roles")
async def list_roles(
    user_id: str = Depends(require_permission(perms.USERS_READ)),
):
    """The role table itself, so the client never hard-codes what a role means."""
    return {
        "roles": [
            {"name": r.name, "permissions": list(r.permissions)}
            for r in perms.describe_roles()
        ],
        "assignable": list(perms.ASSIGNABLE_ROLES),
    }


@router.get("/users")
async def list_users(
    q: str = "",
    limit: int = 50,
    user_id: str = Depends(require_permission(perms.USERS_READ)),
    db: AsyncSession = Depends(get_db),
):
    """
    Who exists and what they can do. Deliberately thin: identity, access and
    the two numbers that explain a support ticket — never someone's holdings.
    """
    limit = max(1, min(limit, 200))
    stmt = select(User).order_by(User.id.desc()).limit(limit)
    if q.strip():
        needle = f"%{q.strip()}%"
        stmt = select(User).where(
            User.email.ilike(needle) | User.clerk_user_id.ilike(needle)
        ).order_by(User.id.desc()).limit(limit)

    rows = (await db.execute(stmt)).scalars().all()
    return [
        {
            "clerk_user_id": u.clerk_user_id,
            "email": u.email,
            "role": u.role,
            "plan": u.plan,
            "market": u.market,
            "has_profile": u.risk_score is not None,
        }
        for u in rows
    ]


@router.patch("/users/{clerk_user_id}/role")
async def set_user_role(
    clerk_user_id: str,
    body: RoleUpdate,
    request: Request,
    admin_id: str = Depends(require_permission(perms.ROLES_WRITE)),
    db: AsyncSession = Depends(get_db),
):
    """
    Grant or withdraw access from inside the app.

    Two guards, both about not locking everyone out of a running system:
    an admin cannot demote themselves (the classic way to lose the only
    account that can undo it), and the last remaining admin cannot be
    demoted by anyone.
    """
    from fastapi import HTTPException

    from backend.i18n import t
    from backend.middleware.language import get_language
    from backend.repositories import user_repository

    lang = get_language(request)

    if body.role not in perms.ASSIGNABLE_ROLES:
        raise HTTPException(
            status_code=422,
            detail=t("error.unknown_role", lang,
                     roles=", ".join(perms.ASSIGNABLE_ROLES)),
        )

    target = await user_repository.get_or_create(db, clerk_user_id)

    if target.role == perms.ADMIN and body.role != perms.ADMIN:
        if clerk_user_id == admin_id:
            raise HTTPException(
                status_code=409, detail=t("error.self_demote", lang)
            )
        admin_count = (await db.execute(
            select(func.count(User.id)).where(User.role == perms.ADMIN)
        )).scalar()
        if admin_count <= 1:
            raise HTTPException(
                status_code=409, detail=t("error.last_admin", lang)
            )

    previous = target.role
    target.role = body.role
    await db.flush()

    # Who changed whose access, and when. A role change that leaves no trace
    # is the one thing about RBAC you cannot reconstruct afterwards.
    logger.info(
        "role_changed actor=%s target=%s from=%s to=%s",
        admin_id, clerk_user_id, previous, body.role,
    )
    return {
        "clerk_user_id": clerk_user_id,
        "role": target.role,
        "permissions": sorted(perms.permissions_for(target.role)),
    }
