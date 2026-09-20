"""
The contract a market pack must satisfy — and the contract a language must.

Every bug found in the US and German markets was the same shape: something
true of Türkiye leaking into an answer given to someone else. A Texas
scenario priced in lira. "e.g. Keşan" offered as a Texan district. A German
buyer sent to ImmoScout24 searching for "daire". A footnote asserting Turkish
transfer-tax law to American readers. Each was found by a person opening the
app and noticing, which does not scale to a fourth market.

So this file is the contract instead. It is parametrised over every market
and every language that exists, which means adding either one runs the whole
suite against it: an incomplete pack fails here rather than in production.

What it deliberately does NOT do is assert specific numbers — a mortgage rate
is a fact about a country and belongs in the pack, not in a test. It asserts
SHAPE: that every field is present, in every language, in the right language,
naming only its own country's facts.
"""

import re

from unittest import mock

import pytest

from backend.auth import permissions as perms  # noqa: F401  (import-time sanity)
from backend.i18n import _C, t
from backend.markets import MARKET_PACKS, get_market_pack, public_markets
from backend.middleware.language import SUPPORTED as BACKEND_LANGUAGES
from backend.schemas.user_profile import RiskProfileAnswers
from backend.services import assumptions, inflation_service
from backend.services.drift import compute_drift
from backend.services.health_score import compute_health
from backend.services.listing_bridge import build_listing_links
from backend.services.portfolio_engine import build_portfolio
from backend.services.rent_vs_buy import compare_rent_vs_buy
from backend.services.risk_engine import compute_risk_score

MARKETS = sorted(MARKET_PACKS)
LANGUAGES = sorted(BACKEND_LANGUAGES)
COMBINATIONS = [(m, lang) for m in MARKETS for lang in LANGUAGES]

# Copy every pack must resolve in every language. `disclaimer` is included
# because it must always RESOLVE, but it is excluded from the "must differ"
# check below: it is the same promise everywhere and lives in the catalogue,
# so a new pack inherits it rather than restating boilerplate.
LOCALIZED_FIELDS = ("broker_note", "tax_note", "disclaimer", "transfer_cost_note")
COUNTRY_SPECIFIC_FIELDS = ("broker_note", "tax_note", "transfer_cost_note")

# Function words that only appear in running prose, never in a proper noun.
# "Keşan" and "Grunderwerbsteuer" are place and thing names and belong in any
# language; "için" and "werden" do not.
PROSE_MARKERS = {
    "tr": re.compile(r"\b(ve|bir|için|değil|olarak|kadar|daha|gibi|ama|yok|var|"
                     r"ile|senin|bu|şu|çok|her|tüm|sonra|önce|hangi|neden)\b", re.I),
    "de": re.compile(r"\b(und|oder|nicht|eine|einen|dein|deine|wird|werden|kann|"
                     r"sind|auch|mehr|sehr|aber|noch|schon|dass|weil)\b", re.I),
    "en": re.compile(r"\b(and|the|your|with|that|this|from|have|been|will|would|"
                     r"which|are|between|about|than|into)\b", re.I),
}


def reads_as(text: str, expected: str) -> str | None:
    """The other language this text reads as, or None."""
    if not isinstance(text, str) or len(text) < 40:
        return None
    own = len(PROSE_MARKERS[expected].findall(text))
    for lang, pattern in PROSE_MARKERS.items():
        if lang == expected:
            continue
        if len(pattern.findall(text)) >= 2 and own < 2:
            return lang
    return None


def assert_language(texts, lang, where):
    for text in texts:
        wrong = reads_as(text, lang)
        assert wrong is None, f"{where} is {wrong}, expected {lang}: {text[:120]}"


# ── The pack itself ───────────────────────────────────────────────────────────

@pytest.mark.parametrize("market", MARKETS)
def test_a_pack_declares_everything_the_app_asks_it_for(market):
    pack = get_market_pack(market)

    assert pack.code == market
    assert pack.name and pack.regulator
    assert len(pack.currency) == 3, "ISO 4217"
    assert pack.currency_symbol
    assert re.fullmatch(r"[a-z]{2}-[A-Z]{2}", pack.locale), pack.locale
    assert pack.default_index_ticker

    # Enumerations the code branches on, so a typo cannot pass silently.
    assert pack.inflation_source in {"tcmb_evds", "bls", "eurostat", "bundesbank", "none"}
    assert pack.housing_index_source in {"tcmb_evds", "fred", "eurostat", "none"}
    assert pack.rent_index_source in {"bls", "eurostat", "bundesbank", "none"}
    assert pack.regional_housing_source in {"tcmb_evds", "fred", "bundesbank", "none"}

    assert pack.listing_sites, "no way to reach a listing in this market"
    assert pack.example_district and pack.example_locality
    assert pack.news_feeds, "the digest silently does nothing without feeds"


@pytest.mark.parametrize("market,lang", COMBINATIONS)
def test_every_pack_speaks_every_language(market, lang):
    """
    Language and market are independent, so a pack must answer in whichever
    language the reader picked — not in its own country's.
    """
    pack = get_market_pack(market)
    for field in LOCALIZED_FIELDS:
        text = pack.say(field, lang)
        assert len(text) > 40, f"{market}.{field} missing in {lang}"
        assert reads_as(text, lang) is None, f"{market}.{field} is not {lang}: {text[:120]}"

    fears = pack.fears(lang)
    assert len(fears) >= 3, f"{market} fear options missing in {lang}"
    assert all(label.strip() for label in fears.values())


def test_no_pack_repeats_another_pack_s_country_facts():
    """
    Copied content is how "e.g. Keşan" ended up on the Texas card. Anything
    country-specific must differ between packs.
    """
    for field in ("example_district", "example_locality", "regulator"):
        values = [getattr(p, field) for p in MARKET_PACKS.values()]
        assert len(set(values)) == len(values), f"{field} is shared: {values}"

    for field in COUNTRY_SPECIFIC_FIELDS:
        english = [p.say(field, "en") for p in MARKET_PACKS.values()]
        assert len(set(english)) == len(english), f"{field} is copied between packs"


def test_boilerplate_is_inherited_rather_than_restated_by_every_pack():
    """
    Three copies of one sentence is three chances for it to drift. The
    disclaimer lives in the catalogue; a pack overrides it only if it has a
    reason to, and a new pack gets it for free.
    """
    for market, pack in MARKET_PACKS.items():
        for lang in LANGUAGES:
            assert pack.say("disclaimer", lang), market
    assert all(not pack.disclaimer for pack in MARKET_PACKS.values()), \
        "a pack overrides the shared disclaimer — intentional, or a copy?"


def test_a_pack_cannot_claim_a_breakdown_it_cannot_read():
    """
    Claiming a sub-national table without a reader renders an empty list
    instead of the honest "not published here" card.

    The regional source is named separately from the national one because
    they need not be the same provider: Germany's national index is
    Eurostat's, its only free regional figures are the Bundesbank's.
    """
    from backend.services.province_intelligence import _SOURCES

    for market, pack in MARKET_PACKS.items():
        if pack.regional_housing_breakdown:
            assert pack.regional_housing_source in _SOURCES, (
                f"{market} claims a breakdown but nothing can read "
                f"{pack.regional_housing_source!r}")


def test_the_investable_universe_is_reachable_and_self_consistent():
    for market, pack in MARKET_PACKS.items():
        universe = list(pack.asset_universe) + list(pack.reit_assets)
        for asset in universe:
            assert asset.get("ticker") and asset.get("category"), (market, asset)
        tickers = [a["ticker"] for a in universe]
        assert len(tickers) == len(set(tickers)), f"{market} lists a ticker twice"

        for sleeve in (pack.cash_asset, pack.bond_asset):
            if sleeve:
                assert sleeve.get("ticker") and sleeve.get("category"), (market, sleeve)


# ── What the engines produce, per market x language ──────────────────────────

ANSWERS = RiskProfileAnswers(budget=100_000, time_horizon="medium",
                             loss_tolerance="medium", goal="growth",
                             experience="beginner")


@pytest.mark.parametrize("market,lang", COMBINATIONS)
def test_the_portfolio_answers_in_the_readers_language(market, lang):
    portfolio = build_portfolio(risk_score=5.0, budget=100_000,
                                market=market, lang=lang)
    assert portfolio.allocations

    assert_language([a.explanation for a in portfolio.allocations], lang,
                    f"{market} allocation rationale")
    assert_language([portfolio.metadata["allocation_logic"]["formula"]], lang,
                    f"{market} formula")
    assert_language([d["reason"] for d in
                     portfolio.metadata["allocation_logic"]["dropped"]], lang,
                    f"{market} drop reason")

    # No asset name may leak an untranslated catalogue key.
    for allocation in portfolio.allocations:
        assert not allocation.name.startswith("asset."), allocation.name


@pytest.mark.parametrize("market,lang", COMBINATIONS)
def test_no_engine_prints_another_market_s_currency(market, lang):
    """
    A module-level formatter pinned to tr-TR priced a Texas scenario in lira.
    Nothing the backend emits may name a currency that is not this market's.
    """
    pack = get_market_pack(market)
    foreign = {"TRY": r"\bTL\b|₺", "USD": r"\$", "EUR": r"€"}
    foreign.pop(pack.currency, None)

    portfolio = build_portfolio(risk_score=5.0, budget=100_000,
                                market=market, lang=lang)
    rvb = compare_rent_vs_buy(down_payment=50_000, monthly_rent=1_000,
                              years=10, market=market, lang=lang)

    texts = (
        [a.explanation for a in portfolio.allocations]
        + [d["reason"] for d in portfolio.metadata["allocation_logic"]["dropped"]]
        + [rvb["assumptions"].get("transfer_cost_note", "")]
    )
    for text in texts:
        for code, pattern in foreign.items():
            assert not re.search(pattern, text), \
                f"{market}/{lang} mentions {code}: {text[:120]}"


@pytest.mark.parametrize("market,lang", COMBINATIONS)
def test_the_rest_of_the_engines_answer_in_the_readers_language(market, lang):
    profile = compute_risk_score(ANSWERS, lang)
    assert_language([profile.summary], lang, "risk summary")
    assert_language([f.explanation for f in profile.factors], lang, "risk factor")

    assert_language(compute_health({"stock": 90.0, "land": 10.0}, lang)["notes"],
                    lang, "health note")
    assert_language([compute_drift([], {}, [], lang)["reason"]], lang, "drift")

    rvb = compare_rent_vs_buy(down_payment=50_000, monthly_rent=1_000,
                              years=10, market=market, lang=lang)
    assert_language([rvb["assumptions"]["transfer_cost_note"]], lang,
                    f"{market} transfer-cost note")


@pytest.mark.parametrize("market", MARKETS)
def test_listing_links_speak_the_market_s_own_language(market):
    """
    The asset_type ids are Turkish because Türkiye came first. Passing them
    into a foreign portal's search box returns nothing, with no way for the
    reader to tell why.
    """
    pack = get_market_pack(market)
    for asset in ("arsa", "daire"):
        links = build_listing_links("Springfield", "Shelbyville", asset, market=market)
        assert links, market
        assert {link["site"] for link in links} <= {s.name for s in pack.listing_sites} \
            | {"Sahibinden", "Emlakjet"}
        for link in links:
            assert link["url"].startswith("https://")
            if market != "TR":
                lowered = link["url"].lower()
                for turkish in ("arsa", "daire", "konut", "satilik"):
                    assert turkish not in lowered, (market, link["url"])


# ── The data a market declares must actually arrive ──────────────────────────

@pytest.mark.parametrize("market", MARKETS)
def test_a_declared_source_produces_a_plausible_number(market):
    value = assumptions.annual_inflation_pct(market)
    assert 0 < value < 200, (market, value)

    for reader in (assumptions.housing_growth_pct, assumptions.rent_growth_pct,
                   assumptions.portfolio_growth_pct):
        assert -50 < reader(market) < 200, (market, reader.__name__)

    pack = get_market_pack(market)
    assert 0 < pack.mortgage_rate_pct < 100
    assert 0 < pack.mortgage_term_years <= 40
    assert 0 <= pack.transfer_tax_pct < 30
    assert 0 <= pack.vat_pct < 50
    assert 0 < pack.gross_rental_yield < 0.5

    # agency_commission_pct is stored NET; the engine adds VAT. Germany held
    # the gross 3.57% here, so VAT was billed twice and every German buy-side
    # total carried a cost no buyer is charged. The invariant that catches it:
    # the gross must be exactly net + VAT, and must stay inside the band a
    # real buyer's agent charges anywhere we operate.
    gross = assumptions.agency_commission_with_vat_pct(market)
    expected = pack.agency_commission_pct * (1 + pack.vat_pct / 100)
    assert gross == pytest.approx(expected, abs=0.01), (market, gross, expected)
    assert 0 <= gross <= 6, (market, gross)


@pytest.mark.parametrize("market", MARKETS)
def test_the_mortgage_rate_is_read_live_or_falls_back_to_its_own_market(market):
    """
    The rate is the single input that decides a rent-vs-buy verdict, so a
    pack must declare a source we can actually dispatch on, and a source that
    goes quiet must fall back to THIS market's documented constant — never to
    another country's rate and never to None, which would crash the engine.
    """
    pack = get_market_pack(market)
    assert pack.mortgage_rate_source in {"fred", "bundesbank", "none"}, \
        (market, pack.mortgage_rate_source)

    rate = assumptions.mortgage_rate_pct(market)
    assert isinstance(rate, float) and 0 < rate < 100, (market, rate)

    # A market with no source can only ever be its constant, and must not
    # claim to be live.
    if pack.mortgage_rate_source == "none":
        assert rate == pack.mortgage_rate_pct
        assert assumptions.mortgage_rate_is_live(market) is False

    # With the source stubbed silent, every market lands on its own constant.
    with mock.patch.dict(assumptions._MORTGAGE_READERS,
                         {key: (lambda: None) for key in assumptions._MORTGAGE_READERS}):
        assert assumptions.mortgage_rate_pct(market) == pack.mortgage_rate_pct
        assert assumptions.mortgage_rate_is_live(market) is False

    # A source that raises is the same story: fall back, don't propagate.
    def boom():
        raise RuntimeError("source down")

    with mock.patch.dict(assumptions._MORTGAGE_READERS,
                         {key: boom for key in assumptions._MORTGAGE_READERS}):
        assert assumptions.mortgage_rate_pct(market) == pack.mortgage_rate_pct


@pytest.mark.parametrize("market", MARKETS)
def test_the_freshness_of_every_source_is_reported_not_hidden(market):
    """
    Eurostat's German HICP stopped nine months short while the other two
    sources were current. Whatever the answer, the app must be able to say
    how old its number is.
    """
    as_of = assumptions.inflation_as_of(market)
    assert as_of is None or re.fullmatch(r"\d{4}-\d{2}", as_of), (market, as_of)
    behind = assumptions.inflation_months_behind(market)
    assert behind is None or behind >= 0
    assert isinstance(assumptions.inflation_is_stale(market), bool)


@pytest.mark.parametrize("market", MARKETS)
def test_a_market_never_borrows_another_market_s_inflation(market):
    """The core claim of the app is the real return. It was only ever true
    for Türkiye until inflation was routed through the pack."""
    index = inflation_service._get_index(market)
    pack = get_market_pack(market)
    if pack.inflation_source == "none":
        assert index == {}
    else:
        assert index, f"{market} declares {pack.inflation_source} but reads nothing"


# ── Registries must agree ────────────────────────────────────────────────────

def test_the_client_is_told_everything_it_needs_about_each_market():
    rows = {row["code"]: row for row in public_markets()}
    assert set(rows) == set(MARKETS)
    for code, row in rows.items():
        for field in ("currency", "currency_symbol", "locale",
                      "example_district", "example_locality"):
            assert row.get(field), (code, field)
        for field in ("live_inflation", "live_housing_index",
                      "regional_housing_breakdown"):
            assert isinstance(row[field], bool), (code, field)


def test_adding_a_language_means_adding_it_everywhere():
    """
    A language half-added is worse than one not added: i18next falls back
    silently, so the app renders in the wrong language rather than failing.
    """
    import pathlib

    root = pathlib.Path(__file__).resolve().parents[2]

    frontend = set(re.findall(r"code:\s*'(\w{2})'",
                              (root / "frontend/src/i18n.js").read_text()))
    locales = {p.stem for p in (root / "frontend/src/locales").glob("*.json")}
    prompts = {"tr"} | set(re.findall(r"system_prompt\.(\w{2})\.txt",
                                      " ".join(p.name for p in
                                               (root / "backend/prompts").iterdir())))
    advisors = {"tr"} | set(re.findall(r"advisor_prompt\.(\w{2})\.txt",
                                       " ".join(p.name for p in
                                                (root / "backend/prompts").iterdir())))
    packs = set.intersection(*(set(p.tax_note) for p in MARKET_PACKS.values()))

    registries = {
        "frontend LANGUAGES": frontend,
        "backend SUPPORTED": set(BACKEND_LANGUAGES),
        "locale files": locales,
        "system prompts": prompts,
        "advisor prompts": advisors,
        "market packs": packs,
    }
    assert len(set(map(frozenset, registries.values()))) == 1, registries


def test_the_backend_catalogue_is_complete_and_in_the_right_language():
    for key, entry in _C.items():
        for lang in LANGUAGES:
            assert lang in entry, f"{key} missing {lang}"
            wrong = reads_as(entry[lang], lang)
            assert wrong is None, f"{key}[{lang}] reads as {wrong}"


def test_every_source_a_pack_can_declare_can_describe_itself():
    """The honesty note names its source, so every source needs a name."""
    for pack in MARKET_PACKS.values():
        if pack.housing_index_source == "none":
            continue
        key = f"source.{pack.housing_index_source}"
        for lang in LANGUAGES:
            assert t(key, lang) != key, f"{key} has no {lang} description"


# ── Does the contract actually have teeth? ───────────────────────────────────

def test_an_incomplete_pack_is_rejected_by_this_very_file():
    """
    A conformance suite that quietly stops catching things is worse than none,
    because it reads as proof. So: register a deliberately sloppy fourth
    market and assert that this file refuses it.

    Every mistake below is one that actually shipped in the US or German
    market at some point.
    """
    from unittest.mock import patch

    from backend.markets.base import ListingSite, MarketPack

    sloppy = MarketPack(
        code="ZZ", name="Testland", currency="EUR", currency_symbol="€",
        locale="zz-ZZ", languages=["zz"],
        inflation_source="eurostat",
        housing_index_source="eurostat",
        regional_housing_source="unreadable",   # claims a table nothing can read
        default_index_ticker="^TEST",
        news_feeds=[],                          # digest would silently do nothing
        listing_sites=[ListingSite("Portal", "https://example.com/{query}")],
        example_district=MARKET_PACKS["TR"].example_district,   # copied
        example_locality=MARKET_PACKS["TR"].example_locality,
        regulator="Test Authority",
        broker_note={"tr": "Kısa."},            # one language, and too short
        tax_note={"en": "Short."},
        transfer_cost_note={},                  # missing entirely
    )

    caught = []
    with patch.dict(MARKET_PACKS, {"ZZ": sloppy}):
        pack = get_market_pack("ZZ")

        # 1. A pack must declare everything the app asks it for.
        if not pack.news_feeds:
            caught.append("news_feeds")

        # 2. Every pack speaks every language.
        for lang in LANGUAGES:
            for field in LOCALIZED_FIELDS:
                if len(pack.say(field, lang)) <= 40 and field != "disclaimer":
                    caught.append(f"{field}/{lang}")
                    break

        # 3. Country facts may not be copied from another pack.
        districts = [p.example_district for p in MARKET_PACKS.values()]
        if len(set(districts)) != len(districts):
            caught.append("copied example")

        # 4. A breakdown needs a source something can read.
        from backend.services.province_intelligence import _SOURCES
        if pack.regional_housing_breakdown and pack.regional_housing_source not in _SOURCES:
            caught.append("unreadable breakdown")

        # 5. Listing searches must not carry Turkish asset words.
        for link in build_listing_links("A", "B", "daire", market="ZZ"):
            if "daire" in link["url"].lower():
                caught.append("turkish listing term")
                break

    assert set(caught) >= {
        "news_feeds", "copied example", "unreadable breakdown",
        "turkish listing term",
    }, caught
    assert any(c.startswith("broker_note/") for c in caught), caught


# ── Language picks the STARTING market, and never touches it again ───────────

def test_a_new_account_starts_in_the_market_its_language_suggests():
    from backend.markets import DEFAULT_MARKET_BY_LANGUAGE, default_market_for_language

    assert default_market_for_language("tr") == "TR"
    assert default_market_for_language("en") == "US"
    assert default_market_for_language("de") == "DE"

    # A language with no obvious home market, or none at all, falls back.
    assert default_market_for_language("fr") == "TR"
    assert default_market_for_language(None) == "TR"

    # The table may only name markets that exist.
    for language, market in DEFAULT_MARKET_BY_LANGUAGE.items():
        assert language in LANGUAGES, language
        assert market in MARKETS, (language, market)


def test_the_starting_market_is_a_default_and_not_a_coupling(client):
    """
    The distinction that matters: a brand-new account gets a sensible guess,
    but from then on the two settings are independent. Switching language must
    never move someone's money to another market.
    """
    import asyncio

    from backend.main import app
    from backend.middleware.verify_clerk import get_current_user
    from backend.repositories import user_repository
    from backend.tests.conftest import _TestSession

    app.dependency_overrides[get_current_user] = lambda: "market_default_en"
    created = client.get("/users/me", headers={"X-Lumos-Lang": "en"}).json()
    assert created["market"] == "US"

    # Reading in German afterwards must not move them to Germany.
    again = client.get("/users/me", headers={"X-Lumos-Lang": "de"}).json()
    assert again["market"] == "US"

    # And an explicit choice survives any later language.
    client.patch("/users/me/market", json={"market": "TR"},
                 headers={"X-Lumos-Lang": "de"})
    after = client.get("/users/me", headers={"X-Lumos-Lang": "en"}).json()
    assert after["market"] == "TR"

    async def _cleanup():
        async with _TestSession() as db:
            user = await user_repository.get_by_clerk_id(db, "market_default_en")
            assert user is not None
    asyncio.run(_cleanup())


def test_a_turkish_reader_still_starts_in_turkiye(client):
    from backend.main import app
    from backend.middleware.verify_clerk import get_current_user

    app.dependency_overrides[get_current_user] = lambda: "market_default_tr"
    assert client.get("/users/me", headers={"X-Lumos-Lang": "tr"}).json()["market"] == "TR"

    app.dependency_overrides[get_current_user] = lambda: "market_default_de"
    assert client.get("/users/me", headers={"X-Lumos-Lang": "de"}).json()["market"] == "DE"


# ── Sub-national data: shape, frequency and honesty ──────────────────────────

def test_every_regional_source_declares_its_shape_and_frequency():
    """
    Two things the app cannot guess and must not assume.

    FREQUENCY: the Turkish and US series are quarterly, the Bundesbank's is
    annual. Reading a 3-year horizon as "12 observations back" turned it into
    a 12-year one, and the number looked entirely plausible.

    SHAPE: Germany's aggregates are NESTED — the seven largest cities sit
    inside the 127 — so they can be compared but not ranked. A rank badge
    invites "pick number one", which is nonsense for a segment of a market
    you are already in.
    """
    import inspect
    from unittest.mock import patch

    from backend.services import province_intelligence as pi
    from backend.services.province_intelligence import _SOURCES

    for name, reader in _SOURCES.items():
        assert "lang" in inspect.signature(reader).parameters, name

    fake = {f"20{y:02d}-12": 100 + y for y in range(10, 26)}
    # Every reader must return the four keys the caller relies on.
    expected = {"areas", "price_level", "frequency", "shape"}
    with patch.object(pi.evds_service, "get_province_unit_prices",
                      lambda: {"X": {"name": "X", "prices": fake}}), \
         patch.object(pi.fred_service, "get_all_state_hpi",
                      lambda: {"X": {"name": "X", "index": fake}}), \
         patch.object(pi.bundesbank_service, "get_segments",
                      lambda lang="tr": {"X": {"name": "X", "index": fake}}):
        for name, reader in _SOURCES.items():
            read = reader("en")
            assert set(read) == expected, (name, set(read))
            assert read["frequency"] in ("quarterly", "annual"), name
            assert read["shape"] in ("ranking", "comparison"), name


def test_nested_segments_are_compared_and_never_ranked():
    from unittest.mock import patch

    from backend.services import province_intelligence as pi

    fake = {f"20{y:02d}-12": 100 * (1.03 ** y) for y in range(4, 26)}
    with patch.object(pi.bundesbank_service, "get_segments",
                      lambda lang="tr": {
                          "A": {"name": "Seven largest cities", "index": fake},
                          "B": {"name": "All districts", "index": fake},
                      }):
        result = pi.rank_provinces(3, "DE", "en")

    assert result["available"] is True
    assert result["shape"] == "comparison"
    assert result["frequency"] == "annual"
    assert all(row.get("rank") is None for row in result["provinces"])


def test_alternatives_are_ranked():
    from unittest.mock import patch

    from backend.services import province_intelligence as pi

    fake = {f"20{y:02d}-{m:02d}": 100 + y * 4 + m
            for y in range(10, 26) for m in (3, 6, 9, 12)}
    with patch.object(pi.evds_service, "get_province_unit_prices",
                      lambda: {"A": {"name": "A", "prices": fake},
                               "B": {"name": "B", "prices": fake}}):
        result = pi.rank_provinces(3, "TR", "tr")

    assert result["shape"] == "ranking"
    assert result["frequency"] == "quarterly"
    assert [row["rank"] for row in result["provinces"]] == [1, 2]


def test_a_horizon_means_the_same_number_of_YEARS_whatever_the_frequency():
    """The bug this pins: 3 years read as 12 on an annual series."""
    from unittest.mock import patch

    from backend.services import province_intelligence as pi

    # 3% a year, for long enough that 3 years and 12 years differ obviously.
    annual = {f"{2004 + i}-12": 100 * (1.03 ** i) for i in range(22)}
    with patch.object(pi.bundesbank_service, "get_segments",
                      lambda lang="tr": {"A": {"name": "A", "index": annual}}):
        three = pi.rank_provinces(3, "DE", "en")["provinces"][0]["nominal_change_pct"]

    # (1.03 ** 3 - 1) * 100 = 9.3, not the 42.6 that twelve years would give.
    assert three == pytest.approx(9.3, abs=0.2), three


# ── Education coverage ──────────────────────────────────────────────────────
# Every asset the app can RECOMMEND must be explainable, in every language.
# This lives here rather than in the frontend suite because the question spans
# both halves: the packs are Python, the copy is JSON, and neither side can
# answer it alone. It is the same contract as the rest of this file — adding a
# market is a checklist, not a memory test.

_LOCALES = ("tr", "en", "de")
_EXPLAINER_TABS = ("type", "what", "why", "risk")


def _locale(lang: str) -> dict:
    import json
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    return json.loads((root / "frontend" / "src" / "locales" / f"{lang}.json").read_text())


def _explainer(lang: str) -> dict:
    return _locale(lang).get("explainer", {})


def _pack_assets(pack):
    assets = list(pack.asset_universe) + list(pack.reit_assets)
    for extra in (pack.cash_asset, pack.bond_asset):
        if extra:
            assets.append(extra)
    return assets


@pytest.mark.parametrize("market", MARKETS)
def test_every_recommendable_asset_can_be_explained(market):
    """
    A user can tap any allocation to ask "what is this?". If neither the
    ticker nor its category has copy, the card falls back to `stocks` — and a
    German BOND ETF was being explained as a stock. The right shape of card
    with the wrong content in it is worse than no card.
    """
    pack = get_market_pack(market)
    assets = _pack_assets(pack)
    if not assets:
        pytest.skip(f"{market} uses the shared default universe")

    for lang in _LOCALES:
        explainer = _explainer(lang)
        by_ticker = explainer.get("byTicker", {})
        by_category = explainer.get("byCategory", {})

        for asset in assets:
            ticker = asset.get("ticker") or ""
            key = ticker.replace(".", "_")
            category = asset.get("category", "stocks")
            covered = key in by_ticker or category in by_category
            assert covered, (
                f"{market}/{lang}: {ticker} ({category}) has neither its own "
                f"explainer nor a '{category}' category fallback"
            )


@pytest.mark.parametrize("lang", _LOCALES)
def test_every_explainer_entry_is_complete(lang):
    """
    A card renders four fields. A missing one leaves a blank tab, which reads
    as a broken app rather than as missing copy.
    """
    explainer = _explainer(lang)
    for group in ("byTicker", "byCategory"):
        for name, entry in explainer.get(group, {}).items():
            for tab in _EXPLAINER_TABS:
                value = entry.get(tab)
                assert isinstance(value, str) and value.strip(), (
                    f"{lang}: explainer.{group}.{name}.{tab} is missing or empty"
                )


def test_the_three_locales_carry_the_same_explainer_entries():
    """
    Copy added in one language only means a reader of another silently gets
    the generic category card instead of the specific one.
    """
    entries = {
        lang: {
            group: set(_explainer(lang).get(group, {}))
            for group in ("byTicker", "byCategory")
        }
        for lang in _LOCALES
    }
    for group in ("byTicker", "byCategory"):
        reference = entries["en"][group]
        for lang in _LOCALES:
            missing = reference - entries[lang][group]
            extra = entries[lang][group] - reference
            assert not missing, f"{lang} is missing explainer.{group}: {sorted(missing)}"
            assert not extra, f"{lang} has explainer.{group} nobody else has: {sorted(extra)}"
