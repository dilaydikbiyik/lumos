"""
Billing: who has paid for which plan, and the two stores that tell us.

The plan table (ai_tiers.py) already decides what a plan buys — models,
daily quota. This module only decides WHICH plan a reader is on, from:

  * Lemon Squeezy (web) — a merchant of record: it sells, charges and pays
    the VAT in Türkiye, the US and Germany, and accepts an individual
    seller in Türkiye, which Stripe does not;
  * RevenueCat (iOS) — over Apple's in-app purchase, which the App Store
    requires for a digital subscription.

Each store's events are verified (an HMAC signature for Lemon Squeezy, a
shared Authorization value for RevenueCat) and only ever move a plan that
store granted: cancelling on the web never downgrades a plan bought in the
App Store, and the reverse.

A cancelled subscription keeps its plan until the paid period ends; the
store sends a separate "expired" event then, which returns the reader to
free.
"""
import hashlib
import hmac
import logging
from datetime import datetime, timezone
from typing import Optional

from backend.config import settings

logger = logging.getLogger("lumos.billing")

LEMONSQUEEZY = "lemonsqueezy"
REVENUECAT = "revenuecat"
_LS_API = "https://api.lemonsqueezy.com/v1"

# Lemon Squeezy subscription statuses that still grant the plan. past_due is
# the store's retry window: the reader keeps access while their card is
# retried, which is what the store's own dunning emails promise them.
_LS_ACTIVE = {"active", "on_trial", "past_due", "cancelled"}
_LS_ENDED = {"expired", "unpaid", "paused"}

_RC_GRANT = {"INITIAL_PURCHASE", "RENEWAL", "PRODUCT_CHANGE", "UNCANCELLATION",
             "NON_RENEWING_PURCHASE", "SUBSCRIPTION_EXTENDED"}
_RC_END = {"EXPIRATION"}
_RC_CANCEL = {"CANCELLATION"}


def web_checkout_enabled() -> bool:
    return bool(settings.LEMONSQUEEZY_API_KEY and settings.LEMONSQUEEZY_STORE_ID
                and _variant_for("plus") and _variant_for("pro"))


def _variant_for(plan: str) -> str:
    return {"plus": settings.LEMONSQUEEZY_VARIANT_PLUS,
            "pro": settings.LEMONSQUEEZY_VARIANT_PRO}.get(plan, "")


def plan_for_variant(variant_id) -> Optional[str]:
    variant = str(variant_id or "")
    for plan in ("plus", "pro"):
        if variant and variant == _variant_for(plan):
            return plan
    return None


def create_checkout(clerk_user_id: str, email: Optional[str], plan: str,
                    return_url: str) -> str:
    """A hosted checkout URL for this reader and plan. The user id travels as
    custom data and comes back in every webhook, which is how a payment is
    tied to an account without trusting anything the browser says."""
    import httpx

    variant = _variant_for(plan)
    if not variant or not web_checkout_enabled():
        raise ValueError("web checkout is not configured")
    body = {"data": {
        "type": "checkouts",
        "attributes": {
            "checkout_data": {"custom": {"user_id": clerk_user_id},
                              **({"email": email} if email else {})},
            "product_options": {"redirect_url": return_url},
        },
        "relationships": {
            "store": {"data": {"type": "stores", "id": str(settings.LEMONSQUEEZY_STORE_ID)}},
            "variant": {"data": {"type": "variants", "id": str(variant)}},
        },
    }}
    res = httpx.post(f"{_LS_API}/checkouts", json=body, timeout=20, headers={
        "Accept": "application/vnd.api+json",
        "Content-Type": "application/vnd.api+json",
        "Authorization": f"Bearer {settings.LEMONSQUEEZY_API_KEY}",
    })
    res.raise_for_status()
    return res.json()["data"]["attributes"]["url"]


def lemonsqueezy_signature_ok(raw_body: bytes, signature: str) -> bool:
    secret = settings.LEMONSQUEEZY_WEBHOOK_SECRET
    if not secret or not signature:
        return False
    expected = hmac.new(secret.encode(), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


def revenuecat_auth_ok(header: str) -> bool:
    """RevenueCat sends the configured value as the Authorization header,
    with or without a "Bearer " prefix depending on how it was entered."""
    secret = settings.REVENUECAT_WEBHOOK_AUTH
    if not secret:
        return False
    value = header or ""
    return hmac.compare_digest(value, secret) or hmac.compare_digest(value, f"Bearer {secret}")


def lemonsqueezy_change(payload: dict) -> Optional[dict]:
    """What a Lemon Squeezy event means for the plan, or None to ignore it."""
    meta = payload.get("meta") or {}
    data = payload.get("data") or {}
    if data.get("type") != "subscriptions":
        return None
    user_id = (meta.get("custom_data") or {}).get("user_id")
    attrs = data.get("attributes") or {}
    status = attrs.get("status")
    if not user_id or not status:
        return None
    change = {"user_id": user_id, "source": LEMONSQUEEZY,
              "subscription_id": str(data.get("id") or ""),
              "portal_url": (attrs.get("urls") or {}).get("customer_portal"),
              "ends_at": attrs.get("ends_at") if status == "cancelled" else None}
    if status in _LS_ENDED:
        return {**change, "plan": "free"}
    if status in _LS_ACTIVE:
        plan = plan_for_variant(attrs.get("variant_id"))
        return {**change, "plan": plan} if plan else None
    return None


def revenuecat_change(payload: dict) -> Optional[dict]:
    """What a RevenueCat event means for the plan, or None to ignore it."""
    event = payload.get("event") or {}
    kind = event.get("type")
    user_id = event.get("app_user_id")
    if not kind or not user_id:
        return None
    entitlements = set(event.get("entitlement_ids") or [])
    plan = "pro" if "pro" in entitlements else "plus" if "plus" in entitlements else None
    change = {"user_id": user_id, "source": REVENUECAT,
              "subscription_id": event.get("original_transaction_id") or event.get("id"),
              "portal_url": None, "ends_at": None}
    if kind in _RC_END:
        return {**change, "plan": "free"}
    if kind in _RC_CANCEL and plan:
        ms = event.get("expiration_at_ms")
        ends = (datetime.fromtimestamp(ms / 1000, tz=timezone.utc).isoformat()
                if isinstance(ms, (int, float)) else None)
        return {**change, "plan": plan, "ends_at": ends}
    if kind in _RC_GRANT and plan:
        return {**change, "plan": plan}
    return None


def apply_change(user, change: dict) -> bool:
    """Set the plan on `user`. False when the event belongs to a plan this
    store did not grant (a web cancellation never touches an App Store plan)."""
    if change["plan"] == "free":
        if user.plan_source not in (None, change["source"]):
            return False
        user.plan = "free"
        user.plan_source = None
        user.plan_ends_at = None
        user.subscription_id = None
        user.billing_portal_url = None
        return True
    if user.plan_source not in (None, change["source"], "admin") and user.plan != "free":
        # Already paying in the other store: keep the better of the two.
        order = {"free": 0, "plus": 1, "pro": 2}
        if order.get(change["plan"], 0) <= order.get(user.plan, 0):
            return False
    user.plan = change["plan"]
    user.plan_source = change["source"]
    user.plan_ends_at = change.get("ends_at")
    user.subscription_id = change.get("subscription_id") or user.subscription_id
    if change.get("portal_url"):
        user.billing_portal_url = change["portal_url"]
    return True
