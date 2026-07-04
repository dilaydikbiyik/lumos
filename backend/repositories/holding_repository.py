"""
Holding data access — CRUD for user assets.
"""
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.holding import Holding


async def list_for_user(db: AsyncSession, user_id: int) -> list[Holding]:
    result = await db.execute(
        select(Holding).where(Holding.user_id == user_id).order_by(Holding.created_at.desc())
    )
    return list(result.scalars().all())


async def get_for_user(db: AsyncSession, user_id: int, holding_id: int) -> Optional[Holding]:
    result = await db.execute(
        select(Holding).where(Holding.id == holding_id, Holding.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def create(db: AsyncSession, user_id: int, data: dict) -> Holding:
    holding = Holding(user_id=user_id, **data)
    db.add(holding)
    await db.flush()
    return holding


async def update(db: AsyncSession, holding: Holding, changes: dict) -> Holding:
    for field, value in changes.items():
        setattr(holding, field, value)
    await db.flush()
    return holding


async def delete(db: AsyncSession, holding: Holding) -> None:
    await db.delete(holding)
    await db.flush()
