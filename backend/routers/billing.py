"""
Plans, checkout and the two stores' webhooks.

GET  /billing/plans        what each plan buys, and whether the web can sell it
GET  /billing/me           the reader's plan, where it came from, how to manage it
POST /billing/checkout     a hosted Lemon Squeezy checkout for plus or pro
POST /billing/webhook/lemonsqueezy   signed; moves the plan
POST /billing/webhook/revenuecat     shared secret; moves the plan

The webhooks answer 200 to anything they do not act on, so a store does not
retry an event that is not ours forever; they answer 401 only to a request
that failed verification.
"""
import asyncio
import json
import logging
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import settings
from backend.db.database import get_db
from backend.i18n import t
from backend.limiter import limiter
from backend.middleware.language import language
from backend.middleware.verify_clerk import get_current_user
from backend.repositories import user_repository
from backend.services import billing
from backend.services.ai_tiers import public_tiers

logger = logging.getLogger("lumos.billing")
router = APIRouter()


@router.get("/plans")
async def plans():
    return {"plans": public_tiers(), "web_checkout": billing.web_checkout_enabled()}


@router.get("/me")
async def my_plan(user_id: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    user = await user_repository.get_or_create(db, user_id)
    return {"plan": user.plan, "source": user.plan_source, "ends_at": user.plan_ends_at,
            "portal_url": user.billing_portal_url}


class CheckoutRequest(BaseModel):
    plan: Literal["plus", "pro"]


@router.post("/checkout")
@limiter.limit("10/minute")
async def checkout(request: Request, body: CheckoutRequest,
                   user_id: str = Depends(get_current_user),
                   db: AsyncSession = Depends(get_db), lang: str = Depends(language)):
    if not billing.web_checkout_enabled():
        raise HTTPException(status_code=503, detail=t("billing.unavailable", lang))
    user = await user_repository.get_or_create(db, user_id)
    if user.plan_source == billing.REVENUECAT and user.plan != "free":
        # Already subscribed in the App Store: a second subscription on the
        # web would charge them twice for one plan.
        raise HTTPException(status_code=409, detail=t("billing.alreadyApple", lang))
    if user.plan_source == billing.LEMONSQUEEZY and user.plan != "free":
        # A second checkout is a second subscription, charged alongside the
        # first. Changing plan goes through the store's customer portal.
        raise HTTPException(status_code=409, detail=t("billing.alreadyWeb", lang))
    return_url = f"{settings.FRONTEND_URL.rstrip('/')}/plans?paid=1"
    try:
        url = await asyncio.to_thread(billing.create_checkout, user_id, user.email,
                                      body.plan, return_url)
    except Exception as exc:
        logger.warning("checkout failed (%s)", type(exc).__name__)
        raise HTTPException(status_code=503, detail=t("billing.unavailable", lang))
    return {"url": url}


async def _apply(db: AsyncSession, change: dict | None) -> dict:
    if not change:
        return {"handled": False}
    user = await user_repository.get_by_clerk_id(db, change["user_id"])
    if user is None:
        logger.warning("billing event for unknown user")
        return {"handled": False}
    changed = billing.apply_change(user, change)
    await db.flush()
    logger.info("billing %s plan=%s applied=%s", change["source"], change["plan"], changed)
    return {"handled": changed}


@router.post("/webhook/lemonsqueezy")
async def lemonsqueezy_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    raw = await request.body()
    if not billing.lemonsqueezy_signature_ok(raw, request.headers.get("X-Signature", "")):
        raise HTTPException(status_code=401)
    try:
        payload = json.loads(raw)
    except ValueError:
        return {"handled": False}
    return await _apply(db, billing.lemonsqueezy_change(payload))


@router.post("/webhook/revenuecat")
async def revenuecat_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    if not billing.revenuecat_auth_ok(request.headers.get("Authorization", "")):
        raise HTTPException(status_code=401)
    try:
        payload = await request.json()
    except ValueError:
        return {"handled": False}
    return await _apply(db, billing.revenuecat_change(payload))
