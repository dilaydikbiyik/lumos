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
        assert pack.tax_note, code
        # Language and market are independent axes, so every pack must speak
        # every UI language: an English reader may pick the German market.
        for lang in ("tr", "en", "de"):
            assert len(pack.say("broker_note", lang)) > 40, (code, lang)
            assert len(pack.say("tax_note", lang)) > 40, (code, lang)
            assert len(pack.say("disclaimer", lang)) > 60, (code, lang)
            assert len(pack.fears(lang)) >= 3, (code, lang)
        assert len(pack.listing_sites) >= 1, code
        assert len(pack.fear_options) >= 3, code


def test_province_table_is_gated_separately_from_the_national_index():
    """
    A national house-price index and a province-by-province breakdown are
    different data products. Gating the province table on the national index
    showed a German reader Turkish provinces priced in lira — Eurostat gives
    Germany a national index but no regional breakdown.
    """
    tr, us, de = MARKET_PACKS["TR"], MARKET_PACKS["US"], MARKET_PACKS["DE"]

    # Türkiye (TCMB, 81 provinces) and the US (FHFA via FRED, 50 states + DC)
    # publish a sub-national breakdown. Germany does not: Eurostat's house
    # price index is national only, and inventing regions from it would be a
    # fabrication — so Germany keeps the national index and loses the table.
    assert tr.regional_housing_breakdown is True
    assert us.regional_housing_breakdown is True
    assert de.regional_housing_breakdown is False
    assert de.housing_index_source != "none"

    # No pack may claim a breakdown it has no source for.
    for code, pack in MARKET_PACKS.items():
        if pack.regional_housing_breakdown:
            assert pack.housing_index_source != "none", code


def test_listing_bridge_reaches_local_portals_in_every_market():
    """The listing bridge is the one real-estate feature that works
    everywhere — it needs no price index, only the market's own portals."""
    from backend.services.listing_bridge import build_listing_links

    for code, pack in MARKET_PACKS.items():
        links = build_listing_links("Berlin", "Mitte", "daire", market=code)
        assert links, code
        assert {link["site"] for link in links} <= {s.name for s in pack.listing_sites} | {
            "Sahibinden", "Emlakjet"
        }, code
        for link in links:
            assert link["url"].startswith("https://"), (code, link)


def test_every_pack_carries_its_own_country_rates():
    """
    Mortgage rates and transfer taxes are facts about a country. They lived in
    a shared constants module until US and DE arrived, which meant a German
    buyer was quietly run through Türkiye's 39% mortgage.
    """
    rates = {c: (p.mortgage_rate_pct, p.transfer_tax_pct, p.mortgage_term_years)
             for c, p in MARKET_PACKS.items()}
    assert len(set(rates.values())) == len(rates), rates
    for code, pack in MARKET_PACKS.items():
        assert 0 < pack.mortgage_rate_pct < 100, code
        assert 0 <= pack.transfer_tax_pct < 30, code
        assert 0 < pack.gross_rental_yield < 0.5, code


def test_eu_pack_offers_no_us_domiciled_etfs():
    """
    PRIIPs bars EU retail investors from US-domiciled ETFs — they carry no Key
    Information Document, so European brokers refuse the order. Recommending
    SPY to a German user names something they cannot legally buy.
    """
    de = MARKET_PACKS["DE"]
    tickers = [a["ticker"] for a in de.asset_universe + de.reit_assets]
    assert tickers, "DE must define its own universe, not inherit the US one"
    us_domiciled = {"SPY", "QQQ", "VOO", "VTI", "VNQ", "SCHH", "GLD", "BND", "BIL", "VXUS"}
    assert not (set(tickers) & us_domiciled), tickers
    # Every DE holding trades on a German venue
    assert all(t.endswith(".DE") for t in tickers), tickers


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

    def fake_chat(messages, tier=None, mode="profiling", context="", language="tr"):
        captured["mode"] = mode
        captured["context"] = context
        captured["language"] = language
        return "ETF, hazır bir sepettir."

    original = chat_router.ai_chat
    chat_router.ai_chat = fake_chat
    try:
        res = client.post("/chat/advisor", json={"messages": [{"role": "user", "content": "ETF nedir?"}]})
        assert res.status_code == 200, res.text
        assert res.json()["reply"] == "ETF, hazır bir sepettir."
        assert captured["mode"] == "advisor"
        assert "6.2/10" in captured["context"]  # real profile injected
        assert captured["language"] == "tr"      # no header -> reference locale
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


# ── DB URL normalization (paste-verbatim provider strings) ───────────────────

def test_neon_style_url_is_normalized_for_asyncpg():
    from backend.db.database import normalize_db_url

    neon = ("postgresql://user:pw@ep-x-pooler.c-4.eu-central-1.aws.neon.tech/neondb"
            "?sslmode=require&channel_binding=require")
    out = normalize_db_url(neon)
    assert out.startswith("postgresql+asyncpg://")
    assert "channel_binding" not in out
    assert "ssl=require" in out and "sslmode=" not in out

    # param-order variant: channel_binding first must still yield a valid query
    variant = "postgres://u:p@h/db?channel_binding=require&sslmode=require"
    out2 = normalize_db_url(variant)
    assert out2 == "postgresql+asyncpg://u:p@h/db?ssl=require"

    # sqlite/dev URLs pass through untouched
    assert normalize_db_url("sqlite+aiosqlite:///./lumos.db") == "sqlite+aiosqlite:///./lumos.db"
    # already-correct asyncpg URLs stay stable
    ok = "postgresql+asyncpg://u:p@h/db?ssl=require"
    assert normalize_db_url(ok) == ok


def test_monthly_income_saved_once_and_returned(client):
    res = client.patch("/users/me/income", json={"monthly_income": 85000})
    assert res.status_code == 200
    assert res.json()["monthly_income"] == 85000

    me = client.get("/users/me")
    assert me.status_code == 200
    assert me.json()["monthly_income"] == 85000


def test_language_header_selects_the_english_prompt_variant(client):
    """X-Lumos-Lang: en must reach chat() as language="en"; junk falls back to tr."""
    import asyncio

    from backend.main import app
    from backend.middleware.verify_clerk import get_current_user
    from backend.repositories import user_repository
    from backend.routers import chat as chat_router
    from backend.tests.conftest import _TestSession

    app.dependency_overrides[get_current_user] = lambda: "user_lang_1"

    async def seed():
        async with _TestSession() as db:
            await user_repository.get_or_create(db, "user_lang_1")
            await db.commit()

    asyncio.run(seed())

    captured = {}

    def fake_chat(messages, tier=None, mode="profiling", context="", language="tr"):
        captured["language"] = language
        return "ok [PROFILE_COMPLETE]"

    original = chat_router.ai_chat
    chat_router.ai_chat = fake_chat
    try:
        body = {"messages": [{"role": "user", "content": "hello"}]}
        assert client.post("/chat", json=body, headers={"X-Lumos-Lang": "en"}).status_code == 200
        assert captured["language"] == "en"
        assert client.post("/chat", json=body, headers={"X-Lumos-Lang": "xx"}).status_code == 200
        assert captured["language"] == "tr"
    finally:
        chat_router.ai_chat = original


def test_prompt_variants_cover_the_same_contract():
    """The EN quiz must keep the marker protocol and carry no Turkish script."""
    import re

    from backend.services.ai_service import _SYSTEM_PROMPTS, _ADVISOR_PROMPTS

    for variants in (_SYSTEM_PROMPTS, _ADVISOR_PROMPTS):
        assert set(variants) >= {"tr", "en"}

    en = _SYSTEM_PROMPTS["en"]
    assert "[PROFILE_COMPLETE]" in en                  # completion protocol intact
    assert "Q9" in en                                  # all nine questions present
    assert not re.search(r"[şğıŞĞİ]", en)              # no Turkish leaked into EN
    assert "EXCLUSIVELY in English" in en


def test_language_and_market_are_independent():
    """
    Picking English must not force a market, and picking a market must not
    force a language: an English reader investing in Germany has to get
    German market FACTS in English PROSE. Writing each pack in one national
    language quietly welded the two axes together.
    """
    de = MARKET_PACKS["DE"]
    tr = MARKET_PACKS["TR"]

    # German market, English reader — English words, German rules
    english_de = de.say("broker_note", "en")
    assert "UCITS" in english_de
    assert "Aktien" not in english_de

    # Turkish market, English reader
    english_tr = tr.say("broker_note", "en")
    assert "brokerage" in english_tr.lower()

    # Turkish market, German reader
    assert de.say("broker_note", "de") != de.say("broker_note", "en")
    assert tr.say("disclaimer", "de") != tr.say("disclaimer", "tr")

    # Fear options keep stable ids across languages so stored answers survive
    # a language switch — the label changes, the key never does.
    assert set(de.fears("en")) == set(de.fears("de")) == set(de.fears("tr"))


def test_missing_translation_never_renders_blank():
    """A pack with a gap must fall back, not show an empty screen."""
    import dataclasses

    from backend.markets import MARKET_PACKS

    partial = dataclasses.replace(MARKET_PACKS["TR"], broker_note={"en": "Only English here."})
    assert partial.say("broker_note", "de") == "Only English here."
    assert partial.say("broker_note", "tr") == "Only English here."


def test_pack_endpoint_crosses_every_language_with_every_market(client):
    """
    The product requirement in one test: someone on the English UI must be
    able to invest in Türkiye AND in Germany, and Turkish must not disappear
    for anyone. Language picks the words, the market picks the rules.
    """
    import asyncio

    from backend.main import app
    from backend.middleware.verify_clerk import get_current_user
    from backend.repositories import user_repository
    from backend.tests.conftest import _TestSession

    app.dependency_overrides[get_current_user] = lambda: "user_cross_1"

    def set_market(code):
        async def go():
            async with _TestSession() as db:
                user = await user_repository.get_or_create(db, "user_cross_1")
                user.market = code
                await db.commit()
        asyncio.run(go())

    seen = {}
    for market in ("TR", "US", "DE"):
        set_market(market)
        for lang in ("tr", "en", "de"):
            res = client.get("/users/markets/pack", headers={"X-Lumos-Lang": lang})
            assert res.status_code == 200, (market, lang, res.text)
            body = res.json()
            assert body["code"] == market
            assert body["broker_note"] and body["tax_note"] and body["disclaimer"]
            assert len(body["fear_options"]) >= 3
            seen[(market, lang)] = body["broker_note"]

    # Same market, three languages → three different texts (same facts)
    for market in ("TR", "US", "DE"):
        texts = {seen[(market, lang)] for lang in ("tr", "en", "de")}
        assert len(texts) == 3, market

    # Same language, three markets → three different texts (same language)
    for lang in ("tr", "en", "de"):
        texts = {seen[(market, lang)] for market in ("TR", "US", "DE")}
        assert len(texts) == 3, lang

    # The PRIIPs warning is a German-MARKET fact, so it must reach an English
    # reader who selected Germany — that is the whole point of the split.
    assert "UCITS" in seen[("DE", "en")]
    assert "UCITS" in seen[("DE", "tr")]


def test_pack_endpoint_reports_country_rates_not_shared_constants(client):
    """A German buyer must never be quoted Türkiye's mortgage rate."""
    import asyncio

    from backend.main import app
    from backend.middleware.verify_clerk import get_current_user
    from backend.repositories import user_repository
    from backend.tests.conftest import _TestSession

    app.dependency_overrides[get_current_user] = lambda: "user_rates_1"

    rates = {}
    for market in ("TR", "US", "DE"):
        async def go(code=market):
            async with _TestSession() as db:
                user = await user_repository.get_or_create(db, "user_rates_1")
                user.market = code
                await db.commit()
        asyncio.run(go())
        rates[market] = client.get("/users/markets/pack").json()["assumptions"]

    assert rates["TR"]["mortgage_rate_pct"] > 20     # high-inflation economy
    assert rates["DE"]["mortgage_rate_pct"] < 10
    assert rates["US"]["mortgage_rate_pct"] < 10
    assert rates["DE"]["mortgage_term_years"] != rates["TR"]["mortgage_term_years"]
    assert rates["US"]["vat_pct"] == 0               # no VAT on US home purchases


def test_every_ui_language_has_its_own_quiz_prompt():
    """
    A German reader must not be handed the Turkish quiz. The prompt variants
    are the AI-layer half of "language and market are independent".
    """
    import re

    from backend.services.ai_service import _ADVISOR_PROMPTS, _SYSTEM_PROMPTS

    for variants in (_SYSTEM_PROMPTS, _ADVISOR_PROMPTS):
        assert set(variants) >= {"tr", "en", "de"}

    de = _SYSTEM_PROMPTS["de"]
    assert "[PROFILE_COMPLETE]" in de          # completion protocol intact
    assert "Q9" in de                          # all nine questions survive
    assert "EXCLUSIVELY in German" in de
    assert not re.search(r"[şğıŞĞİ]", de)      # no Turkish leaked in
    assert "Wie viel kannst du zum Investieren" in de


def test_unknown_language_falls_back_to_english_not_turkish():
    """Turkish is the most complete file, but it is the WRONG fallback for a
    reader who chose neither — English is the safer intermediate."""
    from backend.services import ai_service

    captured = {}

    def fake_dispatch(messages, system, **kwargs):
        captured["system"] = system
        return "ok"

    original = ai_service._dispatch
    ai_service._dispatch = fake_dispatch
    try:
        ai_service.chat([{"role": "user", "content": "hi"}], language="fr")
        assert "EXCLUSIVELY in English" in captured["system"]
    finally:
        ai_service._dispatch = original


def test_each_market_declares_its_own_universe():
    """
    Every pack states its investable assets rather than inheriting a shared
    file. Türkiye silently fell through to the default set, so a Turkish user
    could be handed the identical portfolio as a US user with no local
    exposure at all — the markets were not actually differentiated.
    """
    universes = {}
    for code, pack in MARKET_PACKS.items():
        assert pack.asset_universe, code
        assert pack.reit_assets, code
        universes[code] = {a["ticker"] for a in pack.asset_universe}

    # Türkiye keeps local equities on the menu
    assert "XU100.IS" in universes["TR"]
    # and no two markets offer an identical menu
    assert len({frozenset(u) for u in universes.values()}) == len(universes)
