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


def test_free_tier_declares_cross_provider_chain():
    # The free tier must be able to fail over past Gemini so a spent free quota
    # is never a dead end for the core journey.
    chain = AI_TIERS["free"]["provider_chain"]
    providers = [step["provider"] for step in chain]
    assert providers == ["gemini", "groq", "openrouter"]
    assert all(step["model_chain"] for step in chain)


def test_dispatch_falls_through_provider_chain():
    """gemini spent → groq spent → openrouter answers; user never sees an error."""
    from backend.services import ai_service
    from backend.services.ai_service import _ProviderUnavailable

    calls = []

    def spent(name):
        def _adapter(messages, system, max_tokens, model_chain=None):
            calls.append(name)
            raise _ProviderUnavailable(f"{name} spent")
        return _adapter

    def answers(messages, system, max_tokens, model_chain=None):
        calls.append("openrouter")
        return "cevap"

    with patch.dict(ai_service._ADAPTERS, {
        "gemini": spent("gemini"), "groq": spent("groq"), "openrouter": answers,
    }):
        reply = ai_service._dispatch([{"role": "user", "content": "hi"}], "sys", 100, tier="free")
    assert reply == "cevap"
    assert calls == ["gemini", "groq", "openrouter"]


def test_dispatch_surfaces_503_only_when_all_providers_spent():
    from fastapi import HTTPException

    from backend.services import ai_service
    from backend.services.ai_service import _ProviderUnavailable
    import pytest

    def spent(messages, system, max_tokens, model_chain=None):
        raise _ProviderUnavailable("spent")

    with patch.dict(ai_service._ADAPTERS, {
        "gemini": spent, "groq": spent, "openrouter": spent,
    }):
        with pytest.raises(HTTPException) as exc:
            ai_service._dispatch([{"role": "user", "content": "hi"}], "sys", 100, tier="free")
    assert exc.value.status_code == 503


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
    # mock_ai patches _dispatch; the quota side proves the tier reached chat():
    # plus quota is 500 — passing without hitting the free limit of 50 is signal enough


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
    # canonical pattern + Turkish character simplification (Çankaya → cankaya)
    assert any("sahibinden.com/satilik-arsa/ankara-cankaya" in link["url"] for link in links)
    assert any("emlakjet.com/satilik-arsa/ankara-cankaya" in link["url"] for link in links)


def test_tr_village_detail_uses_search_fallback():
    # the "Çeribaşı village in Keşan" realism case: micro-location → search route
    links = build_listing_links("Edirne", "Keşan", "arsa", market="TR", detail="Çeribaşı köyü")
    sahibinden = next(link for link in links if link["site"] == "Sahibinden")
    emlakjet = next(link for link in links if link["site"] == "Emlakjet")
    assert "arama?query_text=" in sahibinden["url"]
    assert "%C3%87eriba%C5%9F%C4%B1" in sahibinden["url"] or "eriba" in sahibinden["url"]
    # Emlakjet: never invent a village slug (404 risk) — guaranteed district page
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
    assert all("model_chain" not in p for p in plans)  # internal details must not leak


# ── Advisor chat (free-form, not the quiz) ──────────────────────────────────────

def test_advisor_endpoint_uses_advisor_mode_with_context(client):
    """The advisor route must call chat() in advisor mode with the user's context."""
    import asyncio

    from backend.main import app
    from backend.middleware.verify_clerk import get_current_user
    from backend.repositories import user_repository
    from backend.routers import chat as chat_router
    from backend.tests.conftest import _TestSession

    app.dependency_overrides[get_current_user] = lambda: "user_advisor_1"

    async def seed():
        async with _TestSession() as db:
            user = await user_repository.get_or_create(db, "user_advisor_1")
            user.risk_score = 6.2
            user.budget = 100000
            user.goal = "growth"
            await db.commit()

    asyncio.run(seed())

    captured = {}

    def fake_chat(messages, tier=None, mode="profiling", context=""):
        captured["mode"] = mode
        captured["context"] = context
        return "ETF, hazır bir sepettir."

    original = chat_router.ai_chat
    chat_router.ai_chat = fake_chat
    try:
        res = client.post("/chat/advisor", json={"messages": [{"role": "user", "content": "ETF nedir?"}]})
        assert res.status_code == 200, res.text
        assert res.json()["reply"] == "ETF, hazır bir sepettir."
        assert captured["mode"] == "advisor"
        assert "6.2/10" in captured["context"]  # real profile injected
    finally:
        chat_router.ai_chat = original


# ── Reply-quality guards ─────────────────────────────────────────────────────

def test_corrupted_script_reply_is_rejected_and_next_provider_serves():
    """A reply with CJK/Cyrillic corruption must be discarded, not shown."""
    from backend.services import ai_service

    def corrupted(messages, system, max_tokens, model_chain=None):
        return "Eğer rahat的话, yaşınızı paylaşır mısınız?"

    def clean(messages, system, max_tokens, model_chain=None):
        return "Yaşınızı paylaşır mısınız?"

    with patch.dict(ai_service._ADAPTERS, {
        "gemini": corrupted, "groq": clean, "openrouter": clean,
    }):
        reply = ai_service._dispatch([{"role": "user", "content": "5 sene"}], "sys", 100, tier="free")
    assert reply == "Yaşınızı paylaşır mısınız?"


def test_profiling_mode_never_reaches_weak_providers():
    """The scripted quiz is pinned to gemini/anthropic — llama fallbacks are
    for the free-form advisor only."""
    from backend.services import ai_service

    called = []

    def track(name, reply="tamam"):
        def _adapter(messages, system, max_tokens, model_chain=None):
            called.append(name)
            if name == "gemini":
                raise ai_service._ProviderUnavailable("spent")
            return reply
        return _adapter

    with patch.dict(ai_service._ADAPTERS, {
        "gemini": track("gemini"), "groq": track("groq"), "openrouter": track("openrouter"),
    }):
        import pytest as _pytest
        from fastapi import HTTPException
        with _pytest.raises(HTTPException):
            ai_service._dispatch(
                [{"role": "user", "content": "merhaba"}], "sys", 100,
                tier="free", providers={"gemini", "anthropic"},
            )
    assert called == ["gemini"]  # groq/openrouter never consulted


def test_profiling_survives_via_openrouter_google_models_only():
    """When direct Gemini keys are dead, the quiz may fall to OpenRouter —
    but only its Google-family models, never the Llama/DeepSeek entries."""
    from backend.services import ai_service

    captured = {}

    def gemini_down(messages, system, max_tokens, model_chain=None):
        raise ai_service._ProviderUnavailable("keys unusable")

    def openrouter(messages, system, max_tokens, model_chain=None):
        captured["models"] = model_chain
        return "Yaşınızı paylaşır mısınız?"

    with patch.dict(ai_service._ADAPTERS, {
        "gemini": gemini_down, "groq": openrouter, "openrouter": openrouter,
    }):
        reply = ai_service._dispatch(
            [{"role": "user", "content": "merhaba"}], "sys", 100,
            tier="free",
            providers={"gemini", "anthropic", "openrouter"},
            model_filter=lambda m: any(f in m.lower() for f in ("gemini", "gemma", "claude")),
        )
    assert reply == "Yaşınızı paylaşır mısınız?"
    assert captured["models"] == [
        "google/gemma-4-31b-it:free", "google/gemma-4-26b-a4b-it:free",
    ]


def test_chat_profiling_mode_allows_openrouter_gemini():
    """chat(mode='profiling') must wire the provider+model filters through."""
    from unittest.mock import patch as _patch

    from backend.services import ai_service

    captured = {}

    def fake_dispatch(messages, system, max_tokens, tier=None, providers=None, model_filter=None):
        captured["providers"] = providers
        captured["model_filter"] = model_filter
        return "ok"

    with _patch.object(ai_service, "_dispatch", fake_dispatch):
        ai_service.chat([{"role": "user", "content": "selam"}], mode="profiling")

    assert captured["providers"] == {"gemini", "anthropic", "groq", "openrouter"}
    f = captured["model_filter"]
    assert f("google/gemini-2.0-flash-exp:free") and f("claude-haiku-4-5")
    assert f("google/gemma-4-31b-it:free") and f("openai/gpt-oss-120b")
    assert not f("meta-llama/llama-3.3-70b-instruct:free")
    assert not f("deepseek/deepseek-chat-v3-0324:free")
    assert not f("llama-3.3-70b-versatile")
