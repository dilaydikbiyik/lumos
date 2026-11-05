"""
The stock explorer endpoint. See backend/services/stock_explorer.py for why
it reads the user's market and nothing else about them.
"""
import asyncio

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.database import get_db
from backend.middleware.verify_clerk import get_current_user
from backend.repositories import user_repository
from backend.services import asset_classes, stock_explorer

router = APIRouter()


@router.get("/explore")
async def explore_stocks(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user = await user_repository.get_or_create(db, user_id)
    # The market only. Passing the user object along — or any field of the
    # profile — is the step that would turn a description into advice.
    return await asyncio.to_thread(stock_explorer.explore, user.market or "TR")


@router.get("/asset-classes")
async def compare_asset_classes(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Every kind of investment a reader here can make, measured the same way.
    The market only — see services/asset_classes.py.
    """
    user = await user_repository.get_or_create(db, user_id)
    return await asyncio.to_thread(asset_classes.compare, user.market or "TR")
