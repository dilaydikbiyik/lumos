"""
Clerk Backend API — the identity details Lumos never asked for.

The users table has had an `email` column since the first migration and
nothing ever wrote to it. Clerk owns identity, so the app only ever learned
the `sub` claim from the session token; the admin list therefore showed
nineteen rows of "(no email)" next to opaque ids, which is useless for
answering "who reported this?".

Emails are read from Clerk on demand and cached in our own row, so the hot
path never calls Clerk: a signed-in request is still one JWT verification and
no outbound HTTP. Failure is non-fatal by design — an admin screen that shows
ids is worse than one that shows names, but far better than one that 500s
because a third party is slow.

Verified live against api.clerk.com (2026-09-18): `GET /v1/users` accepts
repeated `user_id` parameters and returns a JSON array; unknown ids are simply
absent from the result rather than an error.
"""

import logging
from typing import Iterable, Optional

from backend.config import settings

logger = logging.getLogger("lumos.clerk")

_BASE = "https://api.clerk.com/v1/users"
_TIMEOUT = 15
# Clerk pages its list endpoints; one request per 100 ids keeps us inside any
# reasonable URL length and matches the default page size.
_BATCH = 100


def is_configured() -> bool:
    return bool(settings.CLERK_SECRET_KEY)


def _primary_email(user: dict) -> Optional[str]:
    """The address Clerk treats as primary, falling back to the first one."""
    addresses = user.get("email_addresses") or []
    if not addresses:
        return None
    primary_id = user.get("primary_email_address_id")
    for address in addresses:
        if address.get("id") == primary_id and address.get("email_address"):
            return address["email_address"]
    return addresses[0].get("email_address")


def _display_name(user: dict) -> Optional[str]:
    parts = [user.get("first_name"), user.get("last_name")]
    name = " ".join(p for p in parts if p)
    return name or None


def fetch_profiles(clerk_ids: Iterable[str]) -> dict[str, dict]:
    """
    {clerk_id: {"email": ..., "name": ...}} for the ids Clerk knows about.

    Ids Clerk has never heard of are omitted rather than raising: a row left
    over from a deleted account should not break the list it appears in.
    """
    ids = [i for i in dict.fromkeys(clerk_ids) if i]
    if not ids or not is_configured():
        return {}

    out: dict[str, dict] = {}
    try:
        import httpx

        headers = {"Authorization": f"Bearer {settings.CLERK_SECRET_KEY}"}
        for start in range(0, len(ids), _BATCH):
            chunk = ids[start:start + _BATCH]
            res = httpx.get(
                _BASE,
                params=[("user_id", i) for i in chunk] + [("limit", len(chunk))],
                headers=headers,
                timeout=_TIMEOUT,
            )
            res.raise_for_status()
            for user in res.json() or []:
                if user.get("id"):
                    out[user["id"]] = {
                        "email": _primary_email(user),
                        "name": _display_name(user),
                    }
    except Exception as exc:
        # Non-fatal: the caller falls back to whatever it already has.
        logger.warning("Clerk profile lookup failed (%s)", type(exc).__name__)
        return out

    return out
