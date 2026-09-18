"""
Role-based access control.

The old model compared one string for equality, so every privileged job was
all-or-nothing: whoever could read the feedback queue could also change other
people's plans. Roles now grant named permissions and endpoints ask for the
permission they need.

The tests that matter most here are the lockout guards. An access system you
can accidentally lock yourself out of is worse than none, because the way back
in is a database console.
"""

import asyncio

import pytest

from backend.auth import permissions as perms
from backend.main import app
from backend.middleware.verify_clerk import get_current_user
from backend.repositories import user_repository
from backend.tests.conftest import _TestSession


def _set_role(clerk_id: str, role: str) -> None:
    async def _run():
        async with _TestSession() as db:
            user = await user_repository.get_or_create(db, clerk_id)
            user.role = role
            await db.commit()
    asyncio.run(_run())


def _as(clerk_id: str) -> None:
    app.dependency_overrides[get_current_user] = lambda: clerk_id


# ── The role table ────────────────────────────────────────────────────────────

def test_every_role_grants_only_known_permissions():
    for role, granted in perms.ROLE_PERMISSIONS.items():
        assert granted <= perms.ALL_PERMISSIONS, role


def test_a_plain_user_has_no_permissions():
    assert perms.permissions_for(perms.USER) == frozenset()
    assert perms.permissions_for(None) == frozenset()
    assert perms.permissions_for("nonsense-role") == frozenset()


def test_support_can_read_but_never_write():
    granted = perms.permissions_for(perms.SUPPORT)
    assert perms.FEEDBACK_READ in granted
    assert perms.STATS_READ in granted
    # The whole point of the role: triage without handing over control.
    assert perms.PLANS_WRITE not in granted
    assert perms.ROLES_WRITE not in granted


def test_admin_holds_every_permission():
    assert perms.permissions_for(perms.ADMIN) == perms.ALL_PERMISSIONS


# ── Enforcement ───────────────────────────────────────────────────────────────

@pytest.mark.parametrize("role,expected", [
    ("user", 403), ("support", 200), ("admin", 200),
])
def test_feedback_queue_is_gated_on_the_permission_not_the_role_name(
    client, role, expected,
):
    _as(f"rbac_feedback_{role}")
    _set_role(f"rbac_feedback_{role}", role)
    assert client.get("/feedback").status_code == expected


@pytest.mark.parametrize("role,expected", [
    ("user", 403), ("support", 403), ("admin", 200),
])
def test_changing_a_plan_needs_write_access(client, role, expected):
    _as(f"rbac_plan_{role}")
    _set_role(f"rbac_plan_{role}", role)
    res = client.patch("/admin/users/rbac_plan_target/plan", json={"plan": "plus"})
    assert res.status_code == expected


@pytest.mark.parametrize("role,expected", [
    ("user", 403), ("support", 200), ("admin", 200),
])
def test_the_user_list_is_readable_by_support(client, role, expected):
    _as(f"rbac_list_{role}")
    _set_role(f"rbac_list_{role}", role)
    assert client.get("/admin/users").status_code == expected


def test_the_user_list_never_exposes_holdings(client):
    _as("rbac_list_fields")
    _set_role("rbac_list_fields", "admin")
    rows = client.get("/admin/users").json()
    assert rows
    for row in rows:
        assert set(row) == {
            "clerk_user_id", "email", "role", "plan", "market", "has_profile",
        }


# ── Granting and withdrawing ──────────────────────────────────────────────────

def test_an_admin_can_grant_and_withdraw_support(client):
    _as("rbac_grantor")
    _set_role("rbac_grantor", "admin")

    granted = client.patch("/admin/users/rbac_grantee/role", json={"role": "support"})
    assert granted.status_code == 200
    assert granted.json()["role"] == "support"
    assert sorted(granted.json()["permissions"]) == sorted(
        perms.permissions_for(perms.SUPPORT))

    withdrawn = client.patch("/admin/users/rbac_grantee/role", json={"role": "user"})
    assert withdrawn.status_code == 200
    assert withdrawn.json()["permissions"] == []


def test_support_cannot_promote_itself(client):
    _as("rbac_climber")
    _set_role("rbac_climber", "support")
    res = client.patch("/admin/users/rbac_climber/role", json={"role": "admin"})
    assert res.status_code == 403


def test_an_unknown_role_is_rejected(client):
    _as("rbac_unknown")
    _set_role("rbac_unknown", "admin")
    res = client.patch("/admin/users/rbac_target/role", json={"role": "superuser"})
    assert res.status_code == 422


def test_an_admin_cannot_demote_themselves(client):
    """The classic way to lose the only account that can undo it."""
    _as("rbac_self")
    _set_role("rbac_self", "admin")
    _set_role("rbac_other_admin", "admin")   # so it isn't the last-admin guard

    res = client.patch("/admin/users/rbac_self/role", json={"role": "user"})
    assert res.status_code == 409

    _as("rbac_self")
    assert client.get("/feedback").status_code == 200   # still an admin


def test_the_last_admin_cannot_be_demoted(client):
    """A system with no admins left can only be fixed from a DB console."""
    async def _demote_everyone():
        from sqlalchemy import select, update

        from backend.models.user import User
        async with _TestSession() as db:
            await db.execute(update(User).values(role="user"))
            await db.commit()
            # sanity: nobody is an admin now
            rows = (await db.execute(select(User).where(User.role == "admin"))).scalars().all()
            assert rows == []

    asyncio.run(_demote_everyone())
    _set_role("rbac_only_admin", "admin")
    _set_role("rbac_demoter", "admin")

    # Two admins: demoting the other one is allowed.
    _as("rbac_demoter")
    assert client.patch("/admin/users/rbac_only_admin/role",
                        json={"role": "user"}).status_code == 200

    # Now there is one left, and it is the caller — both guards apply.
    res = client.patch("/admin/users/rbac_demoter/role", json={"role": "user"})
    assert res.status_code == 409


# ── What the client is told ───────────────────────────────────────────────────

def test_users_me_reports_derived_permissions(client):
    _as("rbac_me")
    _set_role("rbac_me", "support")
    body = client.get("/users/me").json()
    assert body["role"] == "support"
    assert sorted(body["permissions"]) == sorted(perms.permissions_for(perms.SUPPORT))


def test_permissions_are_derived_from_the_role_never_stored(client):
    """Two places holding the same truth is how a revoked role keeps powers."""
    _as("rbac_derive_admin")
    _set_role("rbac_derive_admin", "admin")
    client.patch("/admin/users/rbac_derive/role", json={"role": "admin"})

    _as("rbac_derive")
    assert client.get("/users/me").json()["permissions"] == sorted(perms.ALL_PERMISSIONS)

    _as("rbac_derive_admin")
    client.patch("/admin/users/rbac_derive/role", json={"role": "user"})

    _as("rbac_derive")
    assert client.get("/users/me").json()["permissions"] == []
    assert client.get("/feedback").status_code == 403


def test_the_role_table_is_served_rather_than_hard_coded_on_the_client(client):
    _as("rbac_table")
    _set_role("rbac_table", "admin")
    body = client.get("/admin/roles").json()

    assert {r["name"] for r in body["roles"]} == set(perms.ROLES)
    assert body["assignable"] == list(perms.ASSIGNABLE_ROLES)
