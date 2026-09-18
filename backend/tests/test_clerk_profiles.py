"""
Reading identity back from Clerk.

The users table has carried an `email` column since the first migration and
nothing ever wrote to it — Clerk owns identity and the app only ever learned
the `sub` claim. The admin list therefore showed rows of "(no email)" beside
opaque ids, which cannot answer "who reported this?".

The shape asserted here was verified live against api.clerk.com rather than
recalled: GET /v1/users takes repeated `user_id` parameters, returns a JSON
array, and simply omits ids it does not know.
"""

from unittest.mock import patch

from backend.services import clerk_service


class _Response:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


def _user(uid, addresses, primary=None, first=None, last=None):
    return {
        "id": uid,
        "first_name": first,
        "last_name": last,
        "primary_email_address_id": primary,
        "email_addresses": [
            {"id": aid, "email_address": email} for aid, email in addresses
        ],
    }


def test_without_a_key_nothing_is_requested():
    with patch.object(clerk_service.settings, "CLERK_SECRET_KEY", ""):
        assert clerk_service.is_configured() is False
        assert clerk_service.fetch_profiles(["user_1"]) == {}


def test_the_primary_address_wins_over_the_first_one():
    payload = [_user("user_1",
                     [("idn_a", "old@example.com"), ("idn_b", "current@example.com")],
                     primary="idn_b")]
    with patch.object(clerk_service.settings, "CLERK_SECRET_KEY", "sk"), \
         patch("httpx.get", return_value=_Response(payload)):
        profiles = clerk_service.fetch_profiles(["user_1"])

    assert profiles["user_1"]["email"] == "current@example.com"


def test_a_missing_primary_pointer_falls_back_to_the_first_address():
    payload = [_user("user_1", [("idn_a", "only@example.com")], primary="idn_gone")]
    with patch.object(clerk_service.settings, "CLERK_SECRET_KEY", "sk"), \
         patch("httpx.get", return_value=_Response(payload)):
        assert clerk_service.fetch_profiles(["user_1"])["user_1"]["email"] == "only@example.com"


def test_a_user_with_no_address_yields_none_rather_than_an_empty_string():
    payload = [_user("user_1", [])]
    with patch.object(clerk_service.settings, "CLERK_SECRET_KEY", "sk"), \
         patch("httpx.get", return_value=_Response(payload)):
        assert clerk_service.fetch_profiles(["user_1"])["user_1"]["email"] is None


def test_unknown_ids_are_simply_absent():
    """A row left over from a deleted account must not break the list."""
    payload = [_user("user_known", [("idn_a", "known@example.com")], primary="idn_a")]
    with patch.object(clerk_service.settings, "CLERK_SECRET_KEY", "sk"), \
         patch("httpx.get", return_value=_Response(payload)):
        profiles = clerk_service.fetch_profiles(["user_known", "user_deleted"])

    assert set(profiles) == {"user_known"}


def test_ids_are_deduplicated_and_sent_as_repeated_parameters():
    captured = {}

    def _capture(url, params=None, headers=None, timeout=None):
        captured["params"] = params
        captured["headers"] = headers
        return _Response([])

    with patch.object(clerk_service.settings, "CLERK_SECRET_KEY", "sk"), \
         patch("httpx.get", _capture):
        clerk_service.fetch_profiles(["user_1", "user_2", "user_1", "", None])

    user_ids = [value for key, value in captured["params"] if key == "user_id"]
    assert user_ids == ["user_1", "user_2"]
    assert captured["headers"]["Authorization"] == "Bearer sk"


def test_a_clerk_outage_is_not_fatal():
    """An admin screen showing ids beats one that 500s because Clerk is slow."""
    def _boom(*args, **kwargs):
        raise RuntimeError("connection reset")

    with patch.object(clerk_service.settings, "CLERK_SECRET_KEY", "sk"), \
         patch("httpx.get", _boom):
        assert clerk_service.fetch_profiles(["user_1"]) == {}


def test_names_are_joined_but_never_blank():
    payload = [
        _user("user_1", [("a", "a@example.com")], primary="a", first="Ada", last="Lovelace"),
        _user("user_2", [("b", "b@example.com")], primary="b"),
    ]
    with patch.object(clerk_service.settings, "CLERK_SECRET_KEY", "sk"), \
         patch("httpx.get", return_value=_Response(payload)):
        profiles = clerk_service.fetch_profiles(["user_1", "user_2"])

    assert profiles["user_1"]["name"] == "Ada Lovelace"
    assert profiles["user_2"]["name"] is None


def test_the_admin_list_backfills_and_persists_the_email(client):
    """One outbound call the first time a row is listed, none afterwards."""
    import asyncio

    from backend.main import app
    from backend.middleware.verify_clerk import get_current_user
    from backend.repositories import user_repository
    from backend.tests.conftest import _TestSession

    app.dependency_overrides[get_current_user] = lambda: "clerk_backfill_admin"

    async def _promote():
        async with _TestSession() as db:
            user = await user_repository.get_or_create(db, "clerk_backfill_admin")
            user.role = "admin"
            await db.commit()

    asyncio.run(_promote())

    calls = {"n": 0}

    def _fetch(ids):
        calls["n"] += 1
        return {i: {"email": f"{i}@example.com", "name": None} for i in ids}

    with patch.object(clerk_service, "fetch_profiles", _fetch):
        first = client.get("/admin/users").json()
        assert calls["n"] == 1
        assert all(row["email"] for row in first)

        # Persisted, so the second listing asks Clerk for nothing.
        second = client.get("/admin/users").json()
        assert calls["n"] == 1
        assert {r["clerk_user_id"]: r["email"] for r in second} == \
               {r["clerk_user_id"]: r["email"] for r in first}
