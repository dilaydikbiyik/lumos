"""
Browser subscriptions: handing out the public key, and taking a grant back.

The subscription flow is three steps and only the middle one is ours. The
browser asks the OS for permission, the browser talks to its own push
service and gets an endpoint, and then it tells us. We never see the
permission dialog and cannot trigger it from here.
"""
import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy import delete, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import settings
from backend.i18n import t
from backend.services.behavior_coach import drop_message, rise_message

from backend.db.database import get_db
from backend.middleware.language import language
from backend.middleware.verify_clerk import get_current_user
from backend.models.push_subscription import PushSubscription
from backend.models.user import User
from backend.repositories import user_repository
from backend.services import push_service

router = APIRouter()
logger = logging.getLogger("lumos.push")


class SubscriptionKeys(BaseModel):
    p256dh: str = Field(min_length=1, max_length=255)
    auth: str = Field(min_length=1, max_length=255)


class SubscribeRequest(BaseModel):
    endpoint: str = Field(min_length=1, max_length=2000)
    keys: SubscriptionKeys


@router.get("/public-key")
async def get_public_key():
    """
    The applicationServerKey, and whether this deployment can send at all.

    `available: false` is the honest answer for a deployment with no VAPID
    keys, and the frontend uses it to not offer notifications rather than
    offering them and failing at the last step — which would spend the
    reader's permission on nothing.
    """
    return {"available": push_service.is_configured(), "public_key": push_service.public_key()}


@router.post("/subscribe")
async def subscribe(
    body: SubscribeRequest,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    lang: str = Depends(language),
):
    """
    Record one browser's grant, or update it in place.

    Keyed on the ENDPOINT, not the user: browsers reissue endpoints, and a
    reader who reinstalls would otherwise accumulate dead rows that get
    retried on every market move. The endpoint is also how a device moving
    between two accounts on a shared phone lands on the right user rather
    than notifying the previous one.
    """
    user = await user_repository.get_or_create(db, user_id)

    existing = (await db.execute(
        select(PushSubscription).where(PushSubscription.endpoint == body.endpoint)
    )).scalar_one_or_none()

    if existing:
        existing.user_id = user.id
        existing.p256dh = body.keys.p256dh
        existing.auth = body.keys.auth
        existing.lang = lang
        # A re-subscribe is the browser saying it is alive again, so an
        # earlier retirement is lifted rather than leaving the reader
        # permanently silent after one lapsed grant.
        existing.failed_at = None
    else:
        db.add(PushSubscription(
            user_id=user.id, endpoint=body.endpoint,
            p256dh=body.keys.p256dh, auth=body.keys.auth, lang=lang,
        ))

    await db.commit()
    return {"subscribed": True}


@router.delete("/subscribe")
async def unsubscribe(
    endpoint: str,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Withdraw a grant, for real.

    DELETED rather than flagged. `failed_at` means "the push service says
    this browser is gone"; a reader turning notifications off is a
    different fact, and conflating them would let a re-subscribe silently
    revive something they switched off on purpose.
    """
    user = await user_repository.get_or_create(db, user_id)
    await db.execute(
        delete(PushSubscription).where(
            PushSubscription.endpoint == endpoint,
            PushSubscription.user_id == user.id,
        )
    )
    await db.commit()
    return {"subscribed": False}


# The minimum move worth waking somebody for. Same threshold the chart uses
# to decide whether to show a grounding note at all: below this the honest
# response is silence, and an app that pings about a 0.4% wobble teaches the
# reader to turn notifications off — which costs the coach its only carrier.
MARKET_SWEEP_MIN_PCT = 5.0

# A browser told something within this window is left alone. The sweep runs
# on whatever schedule the external cron happens to use, and without this a
# cron set to five minutes would send the same drop twelve times an hour.
NOTIFY_COOLDOWN_HOURS = 20


@router.post("/market-sweep")
async def market_sweep(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Check every subscribed reader's own portfolio and notify the ones whose
    money actually moved.

    Triggered by an EXTERNAL cron, because a free Render instance has no
    scheduler — and because the same request keeps the instance awake, which
    it needs anyway. One free uptime pinger does both jobs.

    Authenticated by a shared secret rather than a user token: there is no
    user making this request. An empty CRON_SECRET disables the endpoint
    outright instead of leaving it open, since an unauthenticated sweep
    would let anyone make the app notify every reader at will.

    Per-reader, never broadcast. "The market dropped" is not a fact about
    somebody who holds nothing, and the message itself is keyed to the loss
    tolerance THEY stated.
    """
    secret = settings.CRON_SECRET
    if not secret or request.headers.get("X-Lumos-Cron") != secret:
        raise HTTPException(status_code=404)

    if not push_service.is_configured():
        return {"checked": 0, "notified": 0, "reason": "push not configured"}

    cutoff = datetime.now(timezone.utc) - timedelta(hours=NOTIFY_COOLDOWN_HOURS)
    subs = (await db.execute(
        select(PushSubscription).where(
            PushSubscription.failed_at.is_(None),
            or_(PushSubscription.last_notified_at.is_(None),
                PushSubscription.last_notified_at < cutoff),
        )
    )).scalars().all()

    checked = 0
    notified = 0
    # Grouped by user so a reader with a phone and a laptop costs one price
    # lookup rather than two.
    by_user: dict[int, list[PushSubscription]] = {}
    for sub in subs:
        by_user.setdefault(sub.user_id, []).append(sub)

    for uid, rows in by_user.items():
        checked += 1
        try:
            move = await _portfolio_move_pct(db, uid)
        except Exception:
            # One reader's missing price data must not end the sweep for
            # everybody after them.
            logger.warning("sweep: move unavailable for user %s", uid)
            continue

        if move is None or abs(move) < MARKET_SWEEP_MIN_PCT:
            continue

        # By internal id, which is what a subscription row carries. Every
        # user_repository helper is keyed on the Clerk id instead, and the
        # sweep has no Clerk id because there is no user making the request.
        user = (await db.execute(select(User).where(User.id == uid))).scalar_one_or_none()
        if user is None:
            continue

        for sub in rows:
            message = (drop_message if move < 0 else rise_message)(
                user.loss_tolerance, lang=sub.lang,
            )
            sent = await push_service.send_to_user(
                db, uid,
                title=t("push.move_title", sub.lang),
                body=message,
                url="/holdings",
                # One tag per reader per sweep: the service worker replaces
                # rather than stacks, so a second notification about the same
                # move cannot pile up on their lock screen.
                tag="lumos-market-move",
            )
            if sent:
                notified += 1
            break   # send_to_user already covers every browser this user has

        await db.execute(
            update(PushSubscription)
            .where(PushSubscription.id.in_([r.id for r in rows]))
            .values(last_notified_at=datetime.now(timezone.utc))
        )
        await db.commit()

    return {"checked": checked, "notified": notified}


async def _portfolio_move_pct(db: AsyncSession, user_id: int) -> Optional[float]:
    """The reader's OWN portfolio move over the last month, or None."""
    from backend.repositories import holding_repository
    from backend.services.portfolio_history import portfolio_value_history

    holdings = await holding_repository.list_for_user(db, user_id)
    if not holdings:
        return None
    history = await asyncio.to_thread(portfolio_value_history, holdings, 30)
    return history.get("change_pct")
