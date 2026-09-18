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
    assert pack.inflation_source in {"tcmb_evds", "bls", "eurostat", "none"}
    assert pack.housing_index_source in {"tcmb_evds", "fred", "eurostat", "none"}
    assert pack.rent_index_source in {"bls", "eurostat", "none"}

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
    Claiming a sub-national table without a source renders an empty list
    instead of the honest "not published here" card.
    """
    from backend.services.province_intelligence import _SOURCES

    for market, pack in MARKET_PACKS.items():
        if pack.regional_housing_breakdown:
            assert pack.housing_index_source in _SOURCES, (
                f"{market} claims a breakdown but nothing can read "
                f"{pack.housing_index_source!r}")


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
        regional_housing_breakdown=True,        # claims a table nothing can read
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
        if pack.regional_housing_breakdown and pack.housing_index_source not in _SOURCES:
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
