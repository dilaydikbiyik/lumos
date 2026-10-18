"""
Push: the subscription lifecycle and the refusals.

The failure modes here are all silent — a dead subscription retried
forever, a notification encrypted for nobody, a reader's permission spent
on a deployment that cannot send. None of them raise, so each one gets a
test rather than a comment.
"""
from unittest.mock import patch

import pytest

from backend.config import settings


_SUB = {
    "endpoint": "https://push.example.com/abc123",
    "keys": {"p256dh": "BPublicKeyMaterial", "auth": "AuthSecret"},
}


@pytest.fixture
def keys_configured():
    """A deployment that CAN send, without touching a real push service."""
    with patch.object(settings, "VAPID_PRIVATE_KEY", "test-private"), \
         patch.object(settings, "VAPID_PUBLIC_KEY", "test-public"), \
         patch.object(settings, "VAPID_SUBJECT", "mailto:test@example.com"):
        yield


def test_a_deployment_without_keys_says_so_instead_of_failing_later(client):
    """
    The honest refusal. Without this the frontend would ask the reader for
    notification permission and only then discover nothing can send — and
    a denied prompt is not a soft no, it is a setting they must go and undo.
    """
    with patch.object(settings, "VAPID_PRIVATE_KEY", ""), \
         patch.object(settings, "VAPID_SUBJECT", ""):
        res = client.get("/push/public-key")
    assert res.status_code == 200
    assert res.json()["available"] is False


def test_the_public_key_is_served_when_configured(client, keys_configured):
    res = client.get("/push/public-key")
    assert res.status_code == 200
    body = res.json()
    assert body["available"] is True
    assert body["public_key"] == "test-public"


def test_the_private_key_is_never_in_any_response(client, keys_configured):
    """The one thing in this feature that must not travel."""
    for path in ("/push/public-key", "/health"):
        res = client.get(path)
        assert "test-private" not in res.text, f"{path} leaked the private key"


def test_subscribing_records_the_browser(client):
    res = client.post("/push/subscribe", json=_SUB)
    assert res.status_code == 200
    assert res.json()["subscribed"] is True


def test_resubscribing_updates_in_place_rather_than_duplicating(client):
    """
    Browsers reissue endpoints. Without the upsert a reader who reinstalls
    accumulates dead rows, and every one of them is retried on every market
    move — which on a free tier is what gets a service suspended for
    outbound traffic.
    """
    client.post("/push/subscribe", json=_SUB)
    client.post("/push/subscribe", json={**_SUB, "keys": {"p256dh": "NEW", "auth": "NEWAUTH"}})

    import asyncio

    from sqlalchemy import select

    from backend.models.push_subscription import PushSubscription
    from backend.tests.conftest import _TestSession

    async def read():
        async with _TestSession() as s:
            return (await s.execute(select(PushSubscription))).scalars().all()

    rows = asyncio.run(read())
    assert len(rows) == 1, f"{len(rows)} rows for one browser"
    assert rows[0].p256dh == "NEW"


def test_unsubscribing_deletes_rather_than_flagging(client):
    """
    `failed_at` means the push service says the browser is gone. A reader
    switching notifications OFF is a different fact, and conflating them
    would let a later re-subscribe silently revive something they turned
    off on purpose.
    """
    client.post("/push/subscribe", json=_SUB)
    res = client.request("DELETE", "/push/subscribe", params={"endpoint": _SUB["endpoint"]})
    assert res.status_code == 200
    assert res.json()["subscribed"] is False

    import asyncio

    from sqlalchemy import select

    from backend.models.push_subscription import PushSubscription
    from backend.tests.conftest import _TestSession

    async def read():
        async with _TestSession() as s:
            return (await s.execute(select(PushSubscription))).scalars().all()

    assert asyncio.run(read()) == []


def test_a_subscription_the_service_calls_gone_is_retired_not_retried(keys_configured):
    """
    404 and 410 mean the browser is gone for good — uninstalled, cleared,
    expired. Retrying those on every market move is how a notification
    feature turns into a bandwidth bill.
    """
    import asyncio

    from backend.models.push_subscription import PushSubscription
    from backend.services import push_service

    class _Gone(Exception):
        def __init__(self):
            self.response = type("R", (), {"status_code": 410})()

    sub = PushSubscription(
        id=1, user_id=1, endpoint="https://push.example.com/dead",
        p256dh="k", auth="a", lang="tr",
    )

    with patch("pywebpush.webpush", side_effect=_Gone()), \
         patch("pywebpush.WebPushException", _Gone):
        status = asyncio.run(asyncio.to_thread(push_service._send_one, sub, {"title": "x"}))

    assert status == 410, "a gone subscription must be reported for retirement"


def test_one_browsers_failure_never_costs_another_its_message(keys_configured):
    """
    A reader whose laptop subscription expired must still be told on their
    phone. Each send is independent, and an unexpected exception is
    swallowed per-subscription rather than reaching the market-event
    handler that is serving everybody at once.
    """
    import asyncio

    from backend.models.push_subscription import PushSubscription
    from backend.services import push_service

    sub = PushSubscription(
        id=1, user_id=1, endpoint="https://push.example.com/x",
        p256dh="k", auth="a", lang="tr",
    )
    with patch("pywebpush.webpush", side_effect=RuntimeError("network down")):
        status = asyncio.run(asyncio.to_thread(push_service._send_one, sub, {"title": "x"}))

    # Not reported as gone: a transient failure must not retire a live browser.
    assert status is None


def test_nothing_is_sent_when_push_is_not_configured():
    import asyncio
    from unittest.mock import AsyncMock

    from backend.services import push_service

    with patch.object(settings, "VAPID_PRIVATE_KEY", ""), \
         patch.object(settings, "VAPID_SUBJECT", ""):
        sent = asyncio.run(push_service.send_to_user(
            AsyncMock(), 1, title="t", body="b"))
    assert sent == 0


# ── the market sweep ────────────────────────────────────────────────────────

def test_the_sweep_is_closed_without_a_secret(client, keys_configured):
    """
    An unauthenticated sweep would let anyone make the app notify every
    reader at will. An empty CRON_SECRET disables the endpoint rather than
    leaving it open, and the refusal is a 404 rather than a 401 so a
    scanner cannot tell the endpoint exists.
    """
    with patch.object(settings, "CRON_SECRET", ""):
        res = client.post("/push/market-sweep")
    assert res.status_code == 404


def test_the_sweep_refuses_a_wrong_secret(client, keys_configured):
    with patch.object(settings, "CRON_SECRET", "right"):
        res = client.post("/push/market-sweep", headers={"X-Lumos-Cron": "wrong"})
    assert res.status_code == 404


def test_the_sweep_accepts_the_right_secret(client, keys_configured):
    with patch.object(settings, "CRON_SECRET", "right"):
        res = client.post("/push/market-sweep", headers={"X-Lumos-Cron": "right"})
    assert res.status_code == 200
    assert res.json() == {"checked": 0, "notified": 0}


def test_the_sweep_says_so_when_push_is_unconfigured(client):
    """Authenticated, but nothing to send with. Reported, not pretended."""
    with patch.object(settings, "CRON_SECRET", "right"), \
         patch.object(settings, "VAPID_PRIVATE_KEY", ""), \
         patch.object(settings, "VAPID_SUBJECT", ""):
        res = client.post("/push/market-sweep", headers={"X-Lumos-Cron": "right"})
    assert res.status_code == 200
    assert res.json()["notified"] == 0


def test_a_quiet_move_notifies_nobody(client, keys_configured):
    """
    Below the threshold the honest response is silence. An app that pings
    about a 0.4% wobble teaches the reader to turn notifications off, which
    costs the coach its only carrier permanently.
    """
    from backend.routers import push as push_router

    client.post("/push/subscribe", json=_SUB)
    with patch.object(settings, "CRON_SECRET", "right"), \
         patch.object(push_router, "_portfolio_move_pct", return_value=0.4), \
         patch("backend.services.push_service.send_to_user") as send:
        res = client.post("/push/market-sweep", headers={"X-Lumos-Cron": "right"})

    assert res.status_code == 200
    assert res.json()["checked"] == 1, "the reader was checked"
    assert res.json()["notified"] == 0, "and deliberately not told"
    send.assert_not_called()


def test_a_real_drop_notifies_once_and_then_respects_the_cooldown(client, keys_configured):
    """
    The sweep runs on whatever schedule the external cron uses. Without the
    cooldown a cron set to five minutes would send the same drop twelve
    times an hour.
    """
    from unittest.mock import AsyncMock

    from backend.routers import push as push_router

    client.post("/push/subscribe", json=_SUB)
    with patch.object(settings, "CRON_SECRET", "right"), \
         patch.object(push_router, "_portfolio_move_pct", return_value=-12.0), \
         patch("backend.services.push_service.send_to_user",
               new=AsyncMock(return_value=1)) as send:
        first = client.post("/push/market-sweep", headers={"X-Lumos-Cron": "right"})
        second = client.post("/push/market-sweep", headers={"X-Lumos-Cron": "right"})

    assert first.json()["notified"] == 1
    assert second.json() == {"checked": 0, "notified": 0}, "cooldown must hold"
    assert send.await_count == 1


def test_the_notification_body_is_the_coach_not_a_figure(client, keys_configured):
    """
    The reader is told what to DO, in the words keyed to the loss tolerance
    they stated — never "you are down 12%", which is the alarm this is
    meant to answer rather than amplify.
    """
    from unittest.mock import AsyncMock

    from backend.routers import push as push_router

    client.post("/push/subscribe", json=_SUB)
    with patch.object(settings, "CRON_SECRET", "right"), \
         patch.object(push_router, "_portfolio_move_pct", return_value=-12.0), \
         patch("backend.services.push_service.send_to_user",
               new=AsyncMock(return_value=1)) as send:
        client.post("/push/market-sweep", headers={"X-Lumos-Cron": "right"})

    kwargs = send.await_args.kwargs
    assert "12" not in kwargs["body"], f"a figure reached the body: {kwargs['body']!r}"
    assert "%" not in kwargs["body"]
    assert kwargs["url"] == "/holdings"
    assert len(kwargs["body"]) > 40, "the body should be the coach's sentence"
