"""
The backend catalogue, held to the same standard as the frontend's.

`frontend/src/locales/locales.test.js` has enforced tr/en/de parity on the
client copy for a while. The backend catalogue had nothing equivalent, and it
is the half of the screen the engines write: risk summaries, drift notes,
honesty caveats, refusal reasons. A key added in Turkish only degrades
through the fallback chain rather than crashing, which is the right runtime
behaviour and exactly why the gap is invisible — a German reader simply meets
Turkish in the middle of an otherwise German page. That was the original
reason this catalogue exists.

These tests are about COMPLETENESS and SHAPE, not about translation quality,
which no test can judge.
"""

import re

import pytest

from backend.i18n import FALLBACK, _C, t

LANGS = ("tr", "en", "de")

# Values that are deliberately identical across languages: symbols, numerals
# and short initialisms. "ETF" is ETF in all three, and demanding otherwise
# would be demanding somebody invent a German word for "TCMB".
_SAME_BY_DESIGN = re.compile(r"^[\W\d_]*$|^[A-ZÇĞİÖŞÜ]{2,6}$")


@pytest.mark.parametrize("lang", LANGS)
def test_every_key_exists_in_every_language(lang):
    missing = sorted(k for k, v in _C.items() if lang not in v)
    assert not missing, f"{len(missing)} key(s) missing in {lang}: {missing[:15]}"


@pytest.mark.parametrize("lang", LANGS)
def test_no_key_is_blank(lang):
    blank = sorted(k for k, v in _C.items() if not (v.get(lang) or "").strip())
    assert not blank, f"blank in {lang}: {blank[:15]}"


def test_no_language_has_keys_the_others_lack():
    """A stray language on one key means a typo, not a translation."""
    for key, value in _C.items():
        extra = set(value) - set(LANGS)
        assert not extra, f"{key} carries unknown language(s): {sorted(extra)}"


def test_placeholders_match_across_languages():
    """
    The regression this guards: a translated sentence that drops `{years}`
    renders the literal text, and one that INVENTS a placeholder raises at
    format time — in a router, on a screen a reader is already looking at.
    """
    placeholder = re.compile(r"\{(\w+)\}")
    for key, value in _C.items():
        names = {lang: set(placeholder.findall(value[lang]))
                 for lang in LANGS if lang in value}
        reference = names.get("tr", set())
        for lang, found in names.items():
            assert found == reference, (
                f"{key}: {lang} has {sorted(found)}, tr has {sorted(reference)}"
            )


def test_translations_are_not_copies_of_the_turkish():
    """
    Catches the half-finished entry — a key added with the Turkish string
    pasted into all three slots, which parity alone would call complete.
    Symbols and numerals are legitimately identical and are skipped.
    """
    copied = [
        key for key, v in _C.items()
        if not _SAME_BY_DESIGN.match(v.get("tr", ""))
        and v.get("en") == v.get("tr") and v.get("de") == v.get("tr")
    ]
    assert not copied, f"untranslated: {copied[:15]}"


@pytest.mark.parametrize("lang", LANGS)
def test_t_returns_the_requested_language_for_every_key(lang):
    for key in _C:
        assert t(key, lang) == _C[key][lang], key


def test_fallback_chain_never_leaves_a_key_unresolved():
    """Every language's chain has to terminate somewhere that always has a
    value, or a missing key surfaces as the raw key to the reader."""
    for lang, chain in FALLBACK.items():
        assert "tr" in (lang, *chain), f"{lang} cannot fall back to a complete language"


def test_unknown_key_does_not_raise():
    """A missing key must degrade, not 500 — it is usually reached from a
    router that is already mid-response."""
    assert t("no.such.key.exists", "en") is not None


def test_no_copy_outlives_the_code_that_used_it():
    """
    Dead copy is not harmless. It is translated, reviewed and carried
    forward as if it still described the app, and the next person reading
    the catalogue cannot tell which sentences are live.

    Seven keys were left behind when `/projection/region` and
    `rank_regions` were removed — the Turkish ones still named TCMB as the
    source for a feature that no longer existed.

    A key counts as used if it appears ANYWHERE in the source, or if any
    prefix of it is built as an f-string stem (`f"role.{category}"`), which
    is how most of this catalogue is reached.
    """
    import pathlib
    import re

    root = pathlib.Path(__file__).resolve().parents[2]
    catalogue = (root / "backend" / "i18n.py").read_text()
    keys = sorted(set(re.findall(r'^    "([\w.]+)":\s*\{', catalogue, re.M)))
    assert keys, "no keys found — has the catalogue's shape changed?"

    sources = [p.read_text() for p in (root / "backend").rglob("*.py")
               if p.name != "i18n.py"]
    sources += [p.read_text() for p in (root / "frontend" / "src").rglob("*.js")]
    sources += [p.read_text() for p in (root / "frontend" / "src").rglob("*.jsx")]
    blob = "\n".join(sources)

    dead = []
    for key in keys:
        if key in blob:
            continue
        parts = key.split(".")
        if any(f'{".".join(parts[:i])}.{{' in blob for i in range(1, len(parts))):
            continue
        dead.append(key)

    assert not dead, f"copy with no code behind it: {dead}"
