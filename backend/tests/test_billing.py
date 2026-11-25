"""
Billing: a verified store event moves the plan, and nothing else does.

What must never happen: an unsigned or forged event changing a plan; a
cancellation in one store downgrading a plan bought in the other; a
cancelled subscription losing access before the paid period ends.
"""
import hashlib
import hmac
import json
from unittest.mock import patch

import pytest

from backend.config import settings


@pytest.fixture
def stores(monkeypatch):
    for key, value in {
        "LEMONSQUEEZY_API_KEY": "k", "LEMONSQUEEZY_STORE_ID": "1",
        "LEMONSQUEEZY_WEBHOOK_SECRET": "ls-secret",
        "LEMONSQUEEZY_VARIANT_PLUS": "111", "LEMONSQUEEZY_VARIANT_PRO": "222",
        "REVENUECAT_WEBHOOK_AUTH": "rc-secret",
    }.items():
        monkeypatch.setattr(settings, key, value)


def _ls(client, status, variant="111", user=None, sign=True):
    from backend.tests.conftest import FAKE_USER_ID

    body = json.dumps({
        "meta": {"event_name": "subscription_updated", "custom_data": {"user_id": user or FAKE_USER_ID}},
        "data": {"type": "subscriptions", "id": "sub_1", "attributes": {
            "status": status, "variant_id": int(variant), "ends_at": "2099-12-21T00:00:00Z",
            "urls": {"customer_portal": "https://lumos.lemonsqueezy.com/billing"}}},
    }).encode()
    sig = hmac.new(b"ls-secret", body, hashlib.sha256).hexdigest() if sign else "forged"
    return client.post("/billing/webhook/lemonsqueezy", content=body,
                       headers={"X-Signature": sig, "Content-Type": "application/json"})


def _rc(client, kind, entitlement="plus", user=None, auth="rc-secret"):
    from backend.tests.conftest import FAKE_USER_ID

    return client.post("/billing/webhook/revenuecat", headers={"Authorization": auth},
                       json={"event": {"type": kind, "app_user_id": user or FAKE_USER_ID,
                                       "entitlement_ids": [entitlement],
                                       "expiration_at_ms": 4100000000000}})


def _plan(client):
    return client.get("/billing/me").json()


def test_a_signed_web_payment_grants_the_plan_and_expiry_ends_it(client, stores):
    client.get("/users/me")
    assert _ls(client, "active", "222").status_code == 200
    assert _plan(client)["plan"] == "pro"
    _ls(client, "cancelled", "222")
    me = _plan(client)
    assert me["plan"] == "pro" and me["ends_at"], "cancelled keeps the paid period"
    _ls(client, "expired", "222")
    assert _plan(client)["plan"] == "free"


def test_an_unsigned_or_forged_event_changes_nothing(client, stores):
    client.get("/users/me")
    assert _ls(client, "active", "222", sign=False).status_code == 401
    assert _rc(client, "INITIAL_PURCHASE", "pro", auth="wrong").status_code == 401
    assert _plan(client)["plan"] == "free"


def test_one_store_cannot_downgrade_the_others_plan(client, stores):
    client.get("/users/me")
    _rc(client, "INITIAL_PURCHASE", "pro")
    assert _plan(client)["source"] == "revenuecat"
    _ls(client, "expired", "111")                      # a web event for the same reader
    assert _plan(client)["plan"] == "pro"
    _rc(client, "EXPIRATION", "pro")
    assert _plan(client)["plan"] == "free"


def test_checkout_is_refused_cleanly_without_store_keys(client):
    res = client.post("/billing/checkout", json={"plan": "plus"}, headers={"X-Lumos-Lang": "de"})
    assert res.status_code == 503 and "Bezahlvorgang" in res.json()["detail"]


def test_checkout_carries_the_user_id_for_the_webhook(client, stores):
    client.get("/users/me")
    seen = {}

    def fake_post(url, json=None, **kw):
        seen["body"] = json

        class R:
            def raise_for_status(self):
                pass

            def json(self):
                return {"data": {"attributes": {"url": "https://lumos.lemonsqueezy.com/checkout/x"}}}
        return R()

    with patch("httpx.post", side_effect=fake_post):
        res = client.post("/billing/checkout", json={"plan": "pro"})
    assert res.json()["url"].startswith("https://")
    attrs = seen["body"]["data"]["attributes"]
    from backend.tests.conftest import FAKE_USER_ID

    assert attrs["checkout_data"]["custom"]["user_id"] == FAKE_USER_ID
    assert seen["body"]["data"]["relationships"]["variant"]["data"]["id"] == "222"


# ── Late, out-of-order and stale events (bug hunt round 11) ─────────────────

def _ls_event(client, status, variant, sub, updated_at, user=None, ends_at=None):
    from backend.tests.conftest import FAKE_USER_ID

    body = json.dumps({
        "meta": {"custom_data": {"user_id": user or FAKE_USER_ID}},
        "data": {"type": "subscriptions", "id": sub, "attributes": {
            "status": status, "variant_id": int(variant), "updated_at": updated_at,
            "ends_at": ends_at or "2099-01-01T00:00:00Z", "urls": {}}},
    }).encode()
    sig = hmac.new(b"ls-secret", body, hashlib.sha256).hexdigest()
    return client.post("/billing/webhook/lemonsqueezy", content=body,
                       headers={"X-Signature": sig, "Content-Type": "application/json"})


def test_an_old_subscription_expiring_does_not_cancel_the_new_one(client, stores):
    client.get("/users/me")
    _ls_event(client, "active", "111", "9", "2026-01-01T00:00:00Z")
    _ls_event(client, "cancelled", "111", "9", "2026-01-02T00:00:00Z")
    _ls_event(client, "active", "222", "10", "2026-01-03T00:00:00Z")
    assert _plan(client)["plan"] == "pro"
    _ls_event(client, "expired", "111", "9", "2026-01-04T00:00:00Z")
    assert _plan(client)["plan"] == "pro", "sub 9 ending must not touch sub 10"


def test_a_late_retry_cannot_undo_a_newer_event(client, stores):
    client.get("/users/me")
    _ls_event(client, "active", "111", "9", "2026-01-01T00:00:00Z")
    _ls_event(client, "expired", "111", "9", "2026-02-01T00:00:00Z")
    assert _plan(client)["plan"] == "free"
    # the January "active" delivered again in March
    _ls_event(client, "active", "111", "9", "2026-01-01T00:00:00Z")
    assert _plan(client)["plan"] == "free"


def test_a_late_revenuecat_purchase_cannot_undo_its_expiration(client, stores):
    from backend.tests.conftest import FAKE_USER_ID

    client.get("/users/me")

    def rc(kind, ms):
        return client.post("/billing/webhook/revenuecat", headers={"Authorization": "rc-secret"},
                           json={"event": {"type": kind, "app_user_id": FAKE_USER_ID,
                                           "entitlement_ids": ["plus"],
                                           "original_transaction_id": "t1",
                                           "event_timestamp_ms": ms}})
    rc("INITIAL_PURCHASE", 1000)
    rc("EXPIRATION", 3000)
    rc("RENEWAL", 2000)                       # older than the expiration
    assert _plan(client)["plan"] == "free"


def test_an_admin_grant_is_not_lowered_or_ended_by_a_store(client, stores):
    import asyncio

    from backend.main import app
    from backend.middleware.verify_clerk import get_current_user
    from backend.repositories import user_repository
    from backend.tests.conftest import FAKE_USER_ID, _TestSession

    client.get("/users/me")

    async def promote():
        async with _TestSession() as db:
            admin = await user_repository.get_or_create(db, "user_admin_billing")
            admin.role = "admin"
            await db.commit()
    asyncio.run(promote())

    # The real admin route — it must record where the plan came from.
    app.dependency_overrides[get_current_user] = lambda: "user_admin_billing"
    assert client.patch(f"/admin/users/{FAKE_USER_ID}/plan", json={"plan": "pro"}).status_code == 200
    app.dependency_overrides[get_current_user] = lambda: FAKE_USER_ID

    _ls_event(client, "active", "111", "9", "2026-01-01T00:00:00Z")
    assert _plan(client)["plan"] == "pro", "a plus purchase must not lower an admin pro"
    _ls_event(client, "expired", "111", "9", "2026-01-02T00:00:00Z")
    me = _plan(client)
    assert me["plan"] == "pro" and me["source"] == "admin"


def test_a_paid_period_that_is_over_lapses_without_the_expiry_event(client, stores):
    client.get("/users/me")
    _ls_event(client, "cancelled", "222", "9", "2026-01-01T00:00:00Z",
              ends_at="2026-01-31T00:00:00Z")
    # no "expired" event ever arrives (a refund, a lost delivery)
    assert _plan(client)["plan"] == "free"


def test_a_json_body_that_is_not_an_object_is_ignored_not_a_500(client, stores):
    body = b"[1]"
    sig = hmac.new(b"ls-secret", body, hashlib.sha256).hexdigest()
    res = client.post("/billing/webhook/lemonsqueezy", content=body,
                      headers={"X-Signature": sig, "Content-Type": "application/json"})
    assert res.status_code == 200 and res.json() == {"handled": False}
    res = client.post("/billing/webhook/revenuecat", content=b"[1]",
                      headers={"Authorization": "rc-secret", "Content-Type": "application/json"})
    assert res.status_code == 200 and res.json() == {"handled": False}


def test_a_web_subscriber_cannot_open_a_second_checkout(client, stores):
    client.get("/users/me")
    _ls_event(client, "active", "111", "9", "2026-01-01T00:00:00Z")
    with patch("backend.services.billing.create_checkout", return_value="https://x") as made:
        res = client.post("/billing/checkout", json={"plan": "pro"})
    assert res.status_code == 409
    made.assert_not_called()


def test_deleting_the_account_cancels_the_web_subscription_first(client, stores):
    from backend.tests.conftest import FAKE_USER_ID

    client.get("/users/me")
    _ls_event(client, "active", "111", "9", "2026-01-01T00:00:00Z")
    with patch("backend.services.billing.cancel_web_subscription", return_value=False) as cancel, \
         patch("backend.services.clerk_service.delete_user", return_value=True):
        res = client.request("DELETE", "/users/me", json={"confirm_user_id": FAKE_USER_ID})
    assert res.status_code == 502, "the store could not cancel: nothing may be deleted"
    cancel.assert_called_once_with("9")
    assert _plan(client)["plan"] == "plus"

    with patch("backend.services.billing.cancel_web_subscription", return_value=True), \
         patch("backend.services.clerk_service.delete_user", return_value=True):
        res = client.request("DELETE", "/users/me", json={"confirm_user_id": FAKE_USER_ID})
    assert res.status_code == 200 and res.json()["app_store_subscription"] is False
