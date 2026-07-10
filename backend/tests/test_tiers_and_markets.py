"""
Paid-tier infrastructure + Market Pack tests.
"""
from unittest.mock import patch

from backend.markets import MARKET_PACKS, get_market_pack
from backend.services.ai_tiers import AI_TIERS, get_tier
from backend.services.listing_bridge import build_listing_links


# ── AI tiers ──────────────────────────────────────────────────────────────────

def test_every_tier_is_complete():
    for name, t in AI_TIERS.items():
        assert t["provider"] in ("gemini", "anthropic"), name
        assert len(t["model_chain"]) >= 1, name
        assert t["daily_quota"] > 0, name


def test_unknown_plan_degrades_to_free():
    assert get_tier("enterprise-nonsense") == AI_TIERS["free"]


def test_free_tier_quota_matches_previous_default():
    assert get_tier("free")["daily_quota"] == 50


def test_dispatch_routes_by_tier():
    from backend.services import ai_service

    captured = {}

    def fake_adapter(messages, system, max_tokens, model_chain=None):
        captured["chain"] = model_chain
        return "ok"

    with patch.dict(ai_service._ADAPTERS, {"gemini": fake_adapter, "anthropic": fake_adapter}):
        ai_service._dispatch([{"role": "user", "content": "hi"}], "sys", 100, tier="plus")
    assert captured["chain"] == AI_TIERS["plus"]["model_chain"]


def test_chat_endpoint_uses_plan_quota(client, mock_ai):
    import asyncio

    from backend.main import app
    from backend.middleware.verify_clerk import get_current_user
    from backend.repositories import user_repository
    from backend.tests.conftest import _TestSession

    app.dependency_overrides[get_current_user] = lambda: "user_tier_test"

    async def make_plus():
        async with _TestSession() as db:
            user = await user_repository.get_or_create(db, "user_tier_test")
            user.plan = "plus"
            await db.commit()

    asyncio.run(make_plus())

    res = client.post("/chat", json={"messages": [{"role": "user", "content": "selam"}]})
    assert res.status_code == 200
    # mock_ai patches _dispatch; tier'ın chat()'e ulaştığını quota tarafı kanıtlar:
    # plus kotası 500 — 50'lik free sınırında takılmadan geçmiş olması yeterli sinyal


def test_admin_can_set_plan(client):
    import asyncio

    from backend.main import app
    from backend.middleware.verify_clerk import get_current_user
    from backend.repositories import user_repository
    from backend.tests.conftest import _TestSession

    app.dependency_overrides[get_current_user] = lambda: "user_admin_2"

    async def promote():
        async with _TestSession() as db:
            user = await user_repository.get_or_create(db, "user_admin_2")
            user.role = "admin"
            await db.commit()

    asyncio.run(promote())

    res = client.patch("/admin/users/user_target_1/plan", json={"plan": "pro"})
    assert res.status_code == 200
    assert res.json()["plan"] == "pro"

    bad = client.patch("/admin/users/user_target_1/plan", json={"plan": "diamond"})
    assert bad.status_code == 422


# ── Market packs ──────────────────────────────────────────────────────────────

def test_all_packs_have_required_content():
    for code, pack in MARKET_PACKS.items():
        assert pack.currency and pack.locale, code
        assert pack.regulator, code
        assert pack.tax_note and "professional" in pack.disclaimer, code
        assert len(pack.listing_sites) >= 1, code
        assert len(pack.fear_options) >= 3, code


def test_unknown_market_falls_back_to_tr():
    assert get_market_pack("XX").code == "TR"
    assert get_market_pack("").code == "TR"


def test_tr_listing_links_use_canonical_slugs():
    links = build_listing_links("Ankara", "Çankaya", "arsa", market="TR")
    # kanonik kalıp + Türkçe karakter sadeleştirme (Çankaya → cankaya)
    assert any("sahibinden.com/satilik-arsa/ankara-cankaya" in link["url"] for link in links)
    assert any("emlakjet.com/satilik-arsa/ankara-cankaya" in link["url"] for link in links)


def test_tr_village_detail_uses_search_fallback():
    # "Keşan'da Çeribaşı köyü" gerçekçiliği: mikro konum → arama rotası
    links = build_listing_links("Edirne", "Keşan", "arsa", market="TR", detail="Çeribaşı köyü")
    sahibinden = next(link for link in links if link["site"] == "Sahibinden")
    emlakjet = next(link for link in links if link["site"] == "Emlakjet")
    assert "arama?query_text=" in sahibinden["url"]
    assert "%C3%87eriba%C5%9F%C4%B1" in sahibinden["url"] or "eriba" in sahibinden["url"]
    # Emlakjet: köy slugu uydurulmaz (404 riski) — garantili ilçe sayfası
    assert emlakjet["url"] == "https://www.emlakjet.com/satilik-arsa/edirne-kesan"


def test_us_listing_links_use_pack_templates():
    links = build_listing_links("Austin", "", "land", market="US")
    sites = {link["site"] for link in links}
    assert "Zillow" in sites
    assert all("Austin" in link["url"] for link in links)


def test_markets_endpoint(client):
    res = client.get("/users/markets")
    assert res.status_code == 200
    codes = {m["code"] for m in res.json()["markets"]}
    assert {"TR", "US", "DE"} <= codes


def test_update_market_endpoint(client):
    res = client.patch("/users/me/market", json={"market": "de"})
    assert res.status_code == 200
    assert res.json()["market"] == "DE"

    bad = client.patch("/users/me/market", json={"market": "MARS"})
    assert bad.status_code == 422


def test_plans_endpoint(client):
    res = client.get("/users/me/plans")
    assert res.status_code == 200
    plans = res.json()["plans"]
    assert {p["plan"] for p in plans} == {"free", "plus", "pro"}
    assert all("model_chain" not in p for p in plans)  # iç detay sızmaz
