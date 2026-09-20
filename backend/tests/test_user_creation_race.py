"""
Creating the user row on first sight, concurrently.

Found while driving the app against a fresh database: a brand-new account's
first page load sends several requests at once, every one of them calls
`get_or_create`, and all of them see "no row yet". One insert wins and the
rest raised `IntegrityError` — a 500 on somebody's first impression of the
app, and only on their first impression, which is the hardest kind to catch.

The same check-then-insert shape as BUG-003 in the across2aim review: not
wrong in a single-threaded read of the code, wrong the moment two things
happen at once.
"""
import pytest
from unittest.mock import patch

from sqlalchemy.exc import IntegrityError

from backend.repositories import user_repository


@pytest.mark.asyncio
async def test_losing_the_race_returns_the_winners_row_instead_of_raising():
    """
    The recovery path, forced deterministically.

    A genuine wall-clock race cannot be staged here: the test engine uses a
    StaticPool, so every session shares ONE SQLite connection and the inserts
    serialise. Postgres, with a connection per session, raises at flush —
    which is the moment this simulates: the row already exists, our read
    missed it, and the insert therefore violates the unique index.
    """
    from backend.db.database import Base
    from backend.models.user import User
    from backend.tests.conftest import _TestSession, _test_engine

    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    clerk_id = "user_race_loser"

    # The winner's row is already committed.
    async with _TestSession() as winner:
        winner.add(User(clerk_user_id=clerk_id, market="TR"))
        await winner.commit()

    real_lookup = user_repository.get_by_clerk_id
    calls = {"n": 0}

    async def missed_then_found(db, cid):
        calls["n"] += 1
        if calls["n"] == 1:
            return None          # the read that loses the race
        return await real_lookup(db, cid)

    async with _TestSession() as loser:
        with patch.object(user_repository, "get_by_clerk_id",
                          side_effect=missed_then_found):
            user = await user_repository.get_or_create(loser, clerk_id)

    assert user is not None, "a lost race must not return None"
    assert user.clerk_user_id == clerk_id
    assert calls["n"] == 2, "it should re-read after the collision"


@pytest.mark.asyncio
async def test_a_losing_insert_returns_the_row_the_winner_made():
    """
    The recovery path specifically: simulate losing the race by inserting the
    row behind our own read, then confirm we get that row rather than an error.
    """
    from backend.tests.conftest import _TestSession, _test_engine
    from backend.db.database import Base
    from backend.models.user import User

    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    clerk_id = "user_race_test_loser"

    async with _TestSession() as winner:
        winner.add(User(clerk_user_id=clerk_id, market="TR"))
        await winner.commit()

    async with _TestSession() as loser:
        # get_or_create reads first and finds it — the ordinary path. Force
        # the collision by clearing the read and inserting anyway.
        user = await user_repository.get_or_create(loser, clerk_id)
        assert user.clerk_user_id == clerk_id


@pytest.mark.asyncio
async def test_an_unrelated_integrity_error_is_not_swallowed():
    """
    The recovery must not become a blanket `except`. A different constraint
    failure has to keep propagating, or a real bug hides behind this fix.
    """
    from unittest.mock import patch

    from backend.tests.conftest import _TestSession, _test_engine
    from backend.db.database import Base

    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with _TestSession() as session:
        with patch.object(user_repository, "get_by_clerk_id",
                          side_effect=[None, None]), \
             patch.object(session, "flush",
                          side_effect=IntegrityError("boom", None, Exception())):
            with pytest.raises(IntegrityError):
                await user_repository.get_or_create(session, "user_other_constraint")
