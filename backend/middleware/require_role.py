"""
Lightweight RBAC — a dependency that gates endpoints by User.role.
Deliberately minimal: two roles (user/admin), no permission matrix.
"""
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.database import get_db
from backend.middleware.verify_clerk import get_current_user
from backend.repositories import user_repository


def require_role(role: str):
    async def _check(
        user_id: str = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ) -> str:
        user = await user_repository.get_or_create(db, user_id)
        if user.role != role:
            raise HTTPException(status_code=403, detail="Bu işlem için yetkin yok.")
        return user_id
    return _check
