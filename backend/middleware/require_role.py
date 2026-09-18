"""
Access dependencies.

`require_permission` is the one to use: an endpoint declares the capability it
needs and the role table decides who has it. `require_role` is kept because
role equality is still the honest check in the one place that manages roles
themselves.
"""
from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth import permissions as perms
from backend.db.database import get_db
from backend.i18n import t
from backend.middleware.language import get_language
from backend.middleware.verify_clerk import get_current_user
from backend.repositories import user_repository


def _forbidden(request: Request) -> HTTPException:
    return HTTPException(
        status_code=403, detail=t("error.forbidden", get_language(request))
    )


def require_permission(permission: str):
    """Gate an endpoint on a named capability rather than on a role name."""
    async def _check(
        request: Request,
        user_id: str = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ) -> str:
        user = await user_repository.get_or_create(db, user_id)
        if not perms.has_permission(user.role, permission):
            raise _forbidden(request)
        return user_id
    return _check


def require_role(role: str):
    """Exact-role gate. Prefer require_permission unless the role IS the point."""
    async def _check(
        request: Request,
        user_id: str = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ) -> str:
        user = await user_repository.get_or_create(db, user_id)
        if user.role != role:
            raise _forbidden(request)
        return user_id
    return _check
