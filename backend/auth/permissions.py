"""
Role-based access control.

The previous model was a single string compared for equality: `role == "admin"`.
That works until there is a second thing to protect, and it forces every
privileged job to be all-or-nothing — someone who should read the feedback
queue also gets the ability to change other people's plans and roles.

Here a role grants a SET of named permissions, and endpoints ask for the
permission they need rather than for a role. Adding a role is then a line in
one table instead of an `or` in every dependency.

Deliberately small. Three roles, seven permissions, no per-user overrides and
no permission inheritance tree — this is an app with one operator, and an
access model nobody can hold in their head is its own kind of unsafe.
"""

from dataclasses import dataclass


# ── Permissions ───────────────────────────────────────────────────────────────
# Named for what they let you DO, not for the endpoint that happens to use
# them today, so a second caller doesn't force a rename.

FEEDBACK_READ = "feedback:read"
STATS_READ = "stats:read"
USERS_READ = "users:read"
PLANS_WRITE = "plans:write"
ROLES_WRITE = "roles:write"

ALL_PERMISSIONS = frozenset({
    FEEDBACK_READ, STATS_READ, USERS_READ, PLANS_WRITE, ROLES_WRITE,
})


# ── Roles ─────────────────────────────────────────────────────────────────────

USER = "user"
SUPPORT = "support"
ADMIN = "admin"

ROLE_PERMISSIONS: dict[str, frozenset[str]] = {
    # Everyone who signs in. Owns their own data; sees nobody else's.
    USER: frozenset(),
    # Reads what users reported and how the app is being used. Cannot change
    # anything about anyone — the common case for "help me triage feedback"
    # without handing over the ability to grant roles.
    SUPPORT: frozenset({FEEDBACK_READ, STATS_READ, USERS_READ}),
    # The operator.
    ADMIN: ALL_PERMISSIONS,
}

ROLES = tuple(ROLE_PERMISSIONS)

# Roles a user may be moved between from inside the app. USER is included so
# access can be taken away again, which is half of what access control is for.
ASSIGNABLE_ROLES = (USER, SUPPORT, ADMIN)


@dataclass(frozen=True)
class RoleInfo:
    name: str
    permissions: tuple[str, ...]


def permissions_for(role: str | None) -> frozenset[str]:
    """Permissions a role grants. An unknown role grants nothing."""
    return ROLE_PERMISSIONS.get(role or USER, frozenset())


def has_permission(role: str | None, permission: str) -> bool:
    return permission in permissions_for(role)


def describe_roles() -> list[RoleInfo]:
    """The role table, for the admin UI — no hard-coded copy on the client."""
    return [
        RoleInfo(name=name, permissions=tuple(sorted(perms)))
        for name, perms in ROLE_PERMISSIONS.items()
    ]
