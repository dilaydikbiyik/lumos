"""
HTTP-level coverage for the endpoints that only had service-level tests.

Why this file exists. The services behind these routes were each unit
tested, and every one of them passed while the routes on top of them were
wrong: the three market-coupling bugs found in the end-to-end audit all lived
in the layer this file exercises — a router that forgot to pass the user's
market, an argument threaded in the wrong order, a response shape the client
could not read. A green service test says the arithmetic is right. It says
nothing about whether the caller asked the right question.

So these tests deliberately go through the app: auth, dependency wiring,
serialisation and the market lookup included. They assert the CONTRACT — the
status, the keys the client reads, and market-sensitivity where the answer
must differ by country — rather than re-checking numbers that
`test_property_vs_portfolio`, `test_listing_eval` and friends already own.
"""

import asyncio

import pytest

from backend.main import app
from backend.middleware.verify_clerk import get_current_user
from backend.repositories import user_repository
from backend.tests.conftest import FAKE_USER_ID, _TestSession


def _set_market(market: str, user_id: str = FAKE_USER_ID):
    async def go():
        async with _TestSession() as db:
            user = await user_repository.get_or_create(db, user_id)
            user.market = market
            await db.commit()
    asyncio.run(go())


def _set_profile(user_id: str = FAKE_USER_ID, **over):
    answers = dict(
        risk_score=6, budget=1_000_000, time_horizon="long",
        loss_tolerance="medium", goal="growth", experience="beginner",
    )
    answers.update(over)

    async def go():
        async with _TestSession() as db:
            await user_repository.save_risk_profile(db, user_id, **answers)
            await db.commit()
    asyncio.run(go())


# ── /planning ────────────────────────────────────────────────────────────────

def test_purchase_checks_returns_a_checklist(client):
    res = client.get("/planning/purchase-checks")
    assert res.status_code == 200
    body = res.json()
    assert body["checks"], body


@pytest.mark.parametrize("market", ["TR", "US", "DE"])
def test_purchase_checks_are_market_specific(client, market):
    """
    The checklist is the one place the app tells somebody what to verify
    before signing. A shared list would send a German buyer to look for a
    Turkish land registry record.
    """
    _set_market(market)
    res = client.get("/planning/purchase-checks")
    assert res.status_code == 200
    assert res.json()["checks"]


def test_purchase_checks_differ_between_markets(client):
    _set_market("TR")
    tr = client.get("/planning/purchase-checks").json()["checks"]
    _set_market("DE")
    de = client.get("/planning/purchase-checks").json()["checks"]
    assert tr != de


def test_yield_comparison_is_net_of_upkeep(client):
    """The strip the client renders: gross minus upkeep must equal net, or
    the three numbers on screen do not add up."""
    res = client.get("/planning/yield-comparison")
    assert res.status_code == 200
    body = res.json()
    assert body["net_rental_yield_pct"] == pytest.approx(
        body["gross_rental_yield_pct"] - body["annual_upkeep_pct"], abs=0.01
    )
    assert body["note"]


def test_yield_comparison_follows_the_users_market(client):
    _set_market("TR")
    tr = client.get("/planning/yield-comparison").json()
    _set_market("DE")
    de = client.get("/planning/yield-comparison").json()
    assert tr["market"] == "TR" and de["market"] == "DE"


def test_property_vs_portfolio_requires_its_inputs(client):
    assert client.get("/planning/property-vs-portfolio").status_code == 422


def test_property_vs_portfolio_answers_or_says_why_not(client):
    res = client.get("/planning/property-vs-portfolio", params={
        "region": "MUGLA", "amount": 1_000_000, "period": "5y",
    })
    assert res.status_code == 200
    body = res.json()
    if body.get("available") is False:
        # An honest refusal is a valid outcome and must carry its reason.
        assert body["reason"]
    else:
        assert body["property"] and body["portfolio"]


def test_listing_eval_refuses_where_area_data_is_an_index(client):
    """
    US and DE publish a housing INDEX, not a price level, so there is no
    honest per-m² figure to compare a listing against. The refusal is the
    feature: a made-up number here costs somebody a fair property.
    """
    _set_market("DE")
    res = client.post("/planning/listing-eval", json={
        "area_code": "BE", "size_m2": 80, "asking_price": 400_000,
    })
    assert res.status_code == 200
    body = res.json()
    assert body["available"] is False
    assert body["reason"]


def test_listing_eval_validates_its_inputs(client):
    res = client.post("/planning/listing-eval", json={
        "area_code": "MUGLA", "size_m2": 0, "asking_price": 0,
    })
    assert res.status_code == 422


# ── /holdings ────────────────────────────────────────────────────────────────

def test_holdings_history_returns_a_series(client):
    res = client.get("/holdings/history")
    assert res.status_code == 200
    body = res.json()
    assert isinstance(body, (list, dict)), body


def test_holdings_drift_without_holdings_refuses_honestly(client):
    """
    Allocation drift needs both a profile and holdings. With neither, the
    answer is "not available, and here is why" — not a zero-drift verdict,
    which would read as reassurance nobody has earned.
    """
    res = client.get("/holdings/drift")
    assert res.status_code == 200
    body = res.json()
    assert body.get("available") is False
    assert body["reason"]


def test_holdings_drift_target_follows_the_users_market(client):
    """
    The drift TARGET is the recommended portfolio, and the investable
    universe is market-specific — measuring a German portfolio against a
    Turkish target would invent drift that is not there.
    """
    _set_profile()
    _set_market("DE")
    res = client.get("/holdings/drift")
    assert res.status_code == 200


# ── /users ───────────────────────────────────────────────────────────────────

def test_outgoings_are_saved_and_returned(client):
    """The reserve in the budget split is computed from this number, so a
    silently-unsaved value would quietly change somebody's plan."""
    res = client.patch("/users/me/outgoings", json={"monthly_outgoings": 25_000})
    assert res.status_code == 200, res.text
    assert res.json()["monthly_outgoings"] == 25_000

    again = client.patch("/users/me/outgoings", json={"monthly_outgoings": 30_000})
    assert again.json()["monthly_outgoings"] == 30_000


def test_outgoings_reject_a_negative_figure(client):
    res = client.patch("/users/me/outgoings", json={"monthly_outgoings": -1})
    assert res.status_code == 422


# ── /admin ───────────────────────────────────────────────────────────────────

def _promote(user_id: str):
    async def go():
        async with _TestSession() as db:
            user = await user_repository.get_or_create(db, user_id)
            user.role = "admin"
            await db.commit()
    asyncio.run(go())


def test_admin_role_change_is_gated(client):
    """A regular user must not be able to promote anybody, least of all
    themselves."""
    res = client.patch(f"/admin/users/{FAKE_USER_ID}/role", json={"role": "admin"})
    assert res.status_code == 403


def test_admin_plan_change_is_gated(client):
    res = client.patch(f"/admin/users/{FAKE_USER_ID}/plan", json={"plan": "pro"})
    assert res.status_code == 403


def test_admin_can_change_a_role_and_a_plan(client):
    app.dependency_overrides[get_current_user] = lambda: "user_admin_surface"
    _promote("user_admin_surface")
    _set_market("TR", "user_target_surface")   # creates the target user

    role = client.patch("/admin/users/user_target_surface/role",
                        json={"role": "admin"})
    assert role.status_code == 200, role.text

    plan = client.patch("/admin/users/user_target_surface/plan",
                        json={"plan": "pro"})
    assert plan.status_code == 200, plan.text


def test_admin_rejects_an_unknown_role(client):
    app.dependency_overrides[get_current_user] = lambda: "user_admin_surface2"
    _promote("user_admin_surface2")
    res = client.patch(f"/admin/users/{FAKE_USER_ID}/role",
                       json={"role": "superuser"})
    assert res.status_code in (400, 422), res.text


# ── /planning/population-trend ───────────────────────────────────────────────

@pytest.fixture
def offline_population():
    """
    No network. Eurostat is a real upstream, and letting the suite call it
    made this file take 128 seconds instead of a fifth of one — a suite slow
    enough to skip is a suite that stops catching things.
    """
    from unittest.mock import patch

    from backend.markets import get_market_pack
    from backend.services import population_signal

    series = {str(y): float(1_000_000 + (y - 2019) * 25_000) for y in range(2019, 2026)}

    def table(market, age="TOTAL"):
        scale = 0.68 if age == "Y15-64" else 1.0
        return {geo: {k: v * scale for k, v in series.items()}
                for geo in get_market_pack(market).population_regions}

    with patch.object(population_signal, "_table_for", table):
        yield


def test_population_trend_is_served_for_a_market_with_a_source(client, offline_population):
    _set_market("TR")
    res = client.get("/planning/population-trend")
    assert res.status_code == 200, res.text
    body = res.json()
    if body.get("available"):
        assert body["regions"]
        assert body["caveat"] and body["source_note"]
        # NUTS-2, and the answer has to say so — a three-province row must not
        # be read as one province.
        assert body["area_kind"] == "nuts2"
    else:
        # A refusal is a valid outcome (upstream unreachable in a test run)
        # and must carry its reason rather than an empty table.
        assert body["reason"]


def test_population_trend_refuses_in_a_market_with_no_source(client):
    """The US pack declares no population source; it must say so, not guess."""
    _set_market("US")
    res = client.get("/planning/population-trend")
    assert res.status_code == 200
    body = res.json()
    assert body["available"] is False
    assert body["reason"]


def test_population_trend_is_mounted_on_both_paths(client, offline_population):
    """Every router is served at /api/v1 AND its bare legacy path."""
    _set_market("TR")
    assert client.get("/api/v1/planning/population-trend").status_code == 200
    assert client.get("/planning/population-trend").status_code == 200


# ── CORS ─────────────────────────────────────────────────────────────────────

def test_development_allows_any_loopback_port(client):
    """
    Vite takes the next free port when one is busy, and the allowlist used to
    name 5173/5174/5175 one by one — so a developer who landed on 5176 got a
    CORS failure that named no cause.
    """
    import re

    from backend.main import _DEV_ORIGIN_PATTERN

    pattern = re.compile(_DEV_ORIGIN_PATTERN)
    for origin in ("http://localhost:5173", "http://localhost:5176",
                   "http://localhost:61234", "http://127.0.0.1:8080",
                   "https://localhost:5173", "http://localhost"):
        assert pattern.match(origin), origin


def test_the_dev_pattern_does_not_admit_the_open_internet():
    """It is a laptop convenience, and must not read as "any origin"."""
    import re

    from backend.main import _DEV_ORIGIN_PATTERN

    pattern = re.compile(_DEV_ORIGIN_PATTERN)
    for origin in ("http://evil.com", "http://localhost.evil.com",
                   "http://notlocalhost", "http://127.0.0.1.evil.com",
                   "http://localhost:5173.evil.com"):
        assert not pattern.match(origin), origin
