"""
Sending a notification, and knowing when to stop.

This is the carrier for the one message in the app that is worthless late:
"the market dropped, here is what you said you would do". An hour later the
reader has already sold.

Three rules the code enforces rather than documents:

1. **No keys means no push, not a crash.** A deployment without VAPID keys
   serves a completely working app that simply never offers notifications.
   Push is the last thing that should be able to take the site down.

2. **A dead subscription is retired, not retried.** Push services answer
   404 or 410 when a browser is gone for good — uninstalled, cleared, or
   expired. Retrying those on every market move is how a notification
   backlog turns into an outbound-traffic bill, and on Render's free tier
   outbound traffic is what gets a service suspended.

3. **One failure never costs the others their message.** Each subscription
   is sent independently. A reader whose laptop subscription has expired
   must still get it on their phone.

What this file deliberately does NOT do is decide WHETHER to notify. That
belongs with the thing that knows the reader's own stated loss tolerance,
because a 0.4% wobble does not need a notification and an app that sends
one teaches the reader to turn notifications off.
"""
import json
import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import settings
from backend.models.push_subscription import PushSubscription

logger = logging.getLogger("lumos.push")

# The push services' way of saying "this browser is gone for good".
_GONE_STATUSES = {404, 410}


def is_configured() -> bool:
    """Whether this deployment can send at all."""
    return bool(settings.VAPID_PRIVATE_KEY and settings.VAPID_SUBJECT)


def public_key() -> Optional[str]:
    """The applicationServerKey a browser needs. Public by design."""
    return settings.VAPID_PUBLIC_KEY or None


def _send_one(subscription: PushSubscription, payload: dict) -> Optional[int]:
    """
    Push to one browser. Returns the HTTP status when the subscription is
    gone and should be retired, or None when there is nothing to do.

    Synchronous on purpose: pywebpush uses `requests`, so the caller runs
    this in a thread rather than pretending it is async and blocking the
    event loop for every subscriber in turn.
    """
    from pywebpush import WebPushException, webpush

    try:
        webpush(
            subscription_info={
                "endpoint": subscription.endpoint,
                "keys": {"p256dh": subscription.p256dh, "auth": subscription.auth},
            },
            data=json.dumps(payload),
            vapid_private_key=settings.VAPID_PRIVATE_KEY,
            vapid_claims={"sub": settings.VAPID_SUBJECT},
            # The push service may hold a message this long if the device is
            # offline. Beyond about an hour this notification is no longer
            # about anything: the number it refers to has moved on, and a
            # stale alarm is worse than a missed one.
            ttl=3600,
        )
        return None
    except WebPushException as exc:
        status = getattr(getattr(exc, "response", None), "status_code", None)
        if status in _GONE_STATUSES:
            # Not an error worth alarm: this is the normal end of a browser's
            # life. Logged at info so a cleared cache does not read as a fault.
            logger.info("subscription gone (%s) — retiring", status)
            return status
        logger.warning("push failed (%s): %s", status, exc)
        return None
    except Exception:
        # Never let one subscriber's failure reach the caller: the caller is
        # usually a market event handler serving everybody at once.
        logger.exception("push raised unexpectedly")
        return None


async def send_to_user(
    db: AsyncSession, user_id: int, *, title: str, body: str,
    url: str = "/", tag: str = "lumos",
) -> int:
    """
    Notify every live browser this user has installed. Returns how many
    were actually sent.

    Retired subscriptions are marked rather than deleted, so the row still
    says this reader once granted permission — which is the difference
    between "never asked" and "asked and it lapsed" when deciding whether
    to invite them again.
    """
    if not is_configured():
        return 0

    import asyncio

    rows = (await db.execute(
        select(PushSubscription).where(
            PushSubscription.user_id == user_id,
            PushSubscription.failed_at.is_(None),
        )
    )).scalars().all()
    if not rows:
        return 0

    sent = 0
    retire: list[int] = []
    for sub in rows:
        payload = {"title": title, "body": body, "url": url, "tag": tag}
        gone = await asyncio.to_thread(_send_one, sub, payload)
        if gone:
            retire.append(sub.id)
        else:
            sent += 1

    if retire:
        await db.execute(
            update(PushSubscription)
            .where(PushSubscription.id.in_(retire))
            .values(failed_at=datetime.now(timezone.utc))
        )
        await db.commit()

    return sent
