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
            "status": status, "variant_id": int(variant), "ends_at": "2026-12-21T00:00:00Z",
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
                                       "expiration_at_ms": 1800000000000}})


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
