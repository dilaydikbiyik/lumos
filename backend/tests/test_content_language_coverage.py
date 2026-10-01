"""
Every piece of market content, in every language the app ships.

THE BUG THIS EXISTS FOR. A Turkish reader in the German market opened "what
to check before you buy" and got German. The content was market-keyed, which
was right — a purchase checklist for Germany has to be about the Grundbuch —
but each market carried exactly ONE language, and a silent fallback served
whichever existed. The app's own rule is that language and market are
INDEPENDENT axes: the market decides what the content is about, the language
decides what it is written in, and neither may stand in for the other.

There was already a test. It asked `for_market(market, "en")` and checked the
answer was non-empty, which the fallback satisfied by handing back German —
the same vacuous shape the AI-failure-mode audit flagged elsewhere, a test
that passes for a reason unrelated to the thing it names.

So these tests assert three separate things, because the first two can both
hold while the reader still sees the wrong language:

  1. The entry EXISTS for that exact language, with no fallback involved.
  2. The entries DIFFER between languages — otherwise one was pasted into all
     three and coverage is a lie.
  3. The text is actually IN that language, by script and function words.
     This is the one that catches German text filed under "tr".

The market-pack sweep is by REFLECTION rather than a hardcoded field list, so
a per-language field added to the pack tomorrow is covered by this test today.
"""

import dataclasses

import pytest

from backend.content import purchase_checks
from backend.markets import get_market_pack

MARKETS = ("TR", "US", "DE")
LANGS = ("tr", "en", "de")

# Letters that exist in exactly one of the three languages. These are the
# cheap, reliable half of the signal.
_ONLY_TURKISH = set("şŞğĞıİ")
_ONLY_GERMAN = set("ß")

# Function words. Chosen to be common enough to appear in any paragraph of
# running prose and to belong to one language only.
_MARKERS = {
    "tr": (" ve ", " bir ", " için ", " bu ", " ile ", " değil"),
    "en": (" the ", " and ", " you ", " is ", " of ", " that "),
    "de": (" der ", " die ", " das ", " und ", " nicht ", " dir ", " ist "),
}


def _looks_like(text: str, lang: str) -> bool:
    """Heuristic, deliberately loose — it only has to catch a WHOLE block
    of prose filed under the wrong language, not judge translation quality."""
    lowered = f" {text.lower()} "
    chars = set(text)

    if lang == "tr":
        if chars & _ONLY_TURKISH:
            return True
        return any(m in lowered for m in _MARKERS["tr"])
    if lang == "de":
        if chars & _ONLY_GERMAN:
            return True
        return any(m in lowered for m in _MARKERS["de"])
    # English: function words, and none of the other two scripts.
    if chars & (_ONLY_TURKISH | _ONLY_GERMAN):
        return False
    return any(m in lowered for m in _MARKERS["en"])


def _text_of(checks: list[dict]) -> str:
    return " ".join(f"{c['title']} {c['body']}" for c in checks)


# ── purchase checklists ─────────────────────────────────────────────────────

@pytest.mark.parametrize("market", MARKETS)
@pytest.mark.parametrize("lang", LANGS)
def test_every_market_has_checks_in_every_language(market, lang):
    """Checked against the raw table, so a fallback cannot satisfy it."""
    by_lang = purchase_checks.CHECKS[market]
    assert lang in by_lang, f"{market} has no {lang} checklist (fallback would hide this)"
    assert by_lang[lang], f"{market}/{lang} checklist is empty"


@pytest.mark.parametrize("market", MARKETS)
@pytest.mark.parametrize("lang", LANGS)
def test_checks_are_written_in_the_language_they_are_filed_under(market, lang):
    """The actual reported bug: German prose served to a Turkish reader."""
    text = _text_of(purchase_checks.CHECKS[market][lang])
    assert _looks_like(text, lang), (
        f"{market}/{lang} does not read as {lang}: {text[:120]!r}"
    )


@pytest.mark.parametrize("market", MARKETS)
def test_the_languages_are_not_copies_of_each_other(market):
    """Pasting one language into all three is coverage on paper only."""
    rendered = {lang: _text_of(purchase_checks.CHECKS[market][lang]) for lang in LANGS}
    assert len(set(rendered.values())) == len(LANGS), f"{market} has duplicate languages"


@pytest.mark.parametrize("market", MARKETS)
def test_every_language_covers_the_same_checks(market):
    """A translation that quietly drops two checks is worse than none: the
    reader believes they have seen the whole list."""
    counts = {lang: len(purchase_checks.CHECKS[market][lang]) for lang in LANGS}
    assert len(set(counts.values())) == 1, f"{market} check counts differ: {counts}"


@pytest.mark.parametrize("market", MARKETS)
@pytest.mark.parametrize("lang", LANGS)
def test_for_market_returns_the_requested_language_without_falling_back(market, lang):
    """The public accessor, not just the table behind it."""
    assert purchase_checks.for_market(market, lang) is purchase_checks.CHECKS[market][lang]


# ── market packs: same rule, discovered by reflection ───────────────────────

def _per_language_fields(pack) -> dict[str, dict]:
    """Every pack field that is a {language: text} mapping."""
    found = {}
    for field in dataclasses.fields(pack):
        value = getattr(pack, field.name)
        if isinstance(value, dict) and value and all(
            isinstance(k, str) and len(k) == 2 for k in value
        ):
            found[field.name] = value
    return found


@pytest.mark.parametrize("market", MARKETS)
def test_every_per_language_pack_field_covers_every_language(market):
    """
    By reflection, so a field added to the pack tomorrow is covered today —
    the purchase checklist was missed precisely because nothing swept for
    this shape and each new piece of content had to remember on its own.
    """
    pack = get_market_pack(market)
    fields = _per_language_fields(pack)
    assert fields, f"{market}: found no per-language fields — has the shape changed?"

    for name, value in fields.items():
        missing = set(LANGS) - set(value)
        assert not missing, f"{market}.{name} is missing {sorted(missing)}"


@pytest.mark.parametrize("market", MARKETS)
def test_pack_text_is_written_in_the_language_it_is_filed_under(market):
    pack = get_market_pack(market)
    for name, value in _per_language_fields(pack).items():
        for lang in LANGS:
            assert _looks_like(value[lang], lang), (
                f"{market}.{name}[{lang}] does not read as {lang}: {value[lang][:120]!r}"
            )


# ── system prompts: the same class, one layer further in ────────────────────

def test_every_prompt_variant_exists_in_every_language():
    """
    The prompts are loaded from files by glob — the Turkish one is the bare
    name and the others are suffixed — so a language is missing exactly when
    somebody forgot to add a file, with nothing failing to say so. The
    `_language_directive` appended last would still force the reply's
    language, which is what makes the gap invisible: the reader gets their
    own language wrapped around instructions written for someone else.
    """
    from backend.services.ai_service import _ADVISOR_PROMPTS, _SYSTEM_PROMPTS

    for name, variants in (("system", _SYSTEM_PROMPTS), ("advisor", _ADVISOR_PROMPTS)):
        missing = set(LANGS) - set(variants)
        assert not missing, f"{name} prompt is missing {sorted(missing)}"
        for lang in LANGS:
            assert variants[lang].strip(), f"{name} prompt for {lang} is empty"


def test_prompt_variants_are_not_copies_of_one_another():
    from backend.services.ai_service import _ADVISOR_PROMPTS, _SYSTEM_PROMPTS

    for name, variants in (("system", _SYSTEM_PROMPTS), ("advisor", _ADVISOR_PROMPTS)):
        texts = {variants[lang] for lang in LANGS}
        assert len(texts) == len(LANGS), f"{name} prompt has duplicate languages"


# ── currency exposure belongs to the market, not the copy ───────────────────

@pytest.mark.parametrize("market", MARKETS)
def test_every_allocation_declares_what_it_is_priced_in(market):
    """
    The client decides whether to warn about currency risk by comparing the
    holding's currency with the reader's market. A missing value would make
    that comparison silently skip the warning.
    """
    from backend.services.portfolio_engine import build_portfolio

    portfolio = build_portfolio(risk_score=7, budget=1_000_000, market=market)
    for allocation in portfolio.allocations:
        assert allocation.currency, (market, allocation.ticker)


def test_the_same_holding_is_foreign_in_one_market_and_local_in_another():
    """
    The bug this pins. SPY is a dollar ETF in both the Turkish and the US
    universe. For a Turkish reader it carries currency risk; for an American
    it does not — and the old copy decided that by LANGUAGE, telling a
    Turkish reader in the US market that dollars shield them from lira
    erosion they do not have, while never warning an English reader in the
    Turkish market who carries the exposure in full.
    """
    from backend.markets import get_market_pack
    from backend.services.portfolio_engine import build_portfolio

    for market, expect_foreign in (("TR", True), ("US", False), ("DE", False)):
        portfolio = build_portfolio(risk_score=7, budget=1_000_000, market=market)
        pack = get_market_pack(market)
        foreign = [a for a in portfolio.allocations if a.currency != pack.currency]
        assert bool(foreign) is expect_foreign, (market, [a.ticker for a in foreign])


def test_the_fx_note_names_no_currency_of_its_own():
    """It is interpolated from both sides, so it must work for any pair."""
    import json
    import pathlib

    for lang in LANGS:
        bundle = json.loads(
            pathlib.Path(f"frontend/src/locales/{lang}.json").read_text()
        )
        text = bundle["explainer"]["fxExposure"]["text"]
        assert "{{assetCurrency}}" in text and "{{marketCurrency}}" in text, lang
