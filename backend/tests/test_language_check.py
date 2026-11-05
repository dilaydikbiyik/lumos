"""
The short-string language check, held to the real cases it was tuned on.

Both directions come from actual live output. The wrong-language strings are
what scripts/live_smoke.py found readers being served; the right-language
ones are short, correct strings that a paragraph-style check flagged anyway.
"""
import pytest

from backend.services.language_check import wrong_language


@pytest.mark.parametrize("text,lang,reads_as", [
    # Served to real readers before the fixes.
    ("Exchange-traded assets (stock/fund/etf/gold/crypto) require a ticker.", "tr", "en"),
    ("Exchange-traded assets (stock/fund/etf/gold/crypto) require a ticker.", "de", "en"),
    ("Dies ist eine allgemeine Marktentwicklung, die keine sofortigen Handlungen "
     "von Ihnen erfordert.", "tr", "de"),
    ("Yapay zeka servisine şu an ulaşılamıyor — lütfen birkaç dakika sonra tekrar dene.",
     "de", "tr"),
])
def test_prose_in_another_language_is_caught(text, lang, reads_as):
    assert wrong_language(text, lang) == reads_as


@pytest.mark.parametrize("text,lang", [
    # Correct, short, and flagged by the paragraph check this replaced.
    ("Für diesen Markt gibt es keine regionalen Bevölkerungsdaten.", "de"),
    ("Sein schlimmster Rückgang lag bei 6 %.", "de"),
    ("Hedefin, kabul etmen gereken risk seviyesini belirler", "tr"),
    ("Under 30: a long runway to recover raises risk capacity", "en"),
    ("Dein Ziel bestimmt, welches Risiko du eingehen musst", "de"),
    # Nothing to judge: no signal either way must not be a failure.
    ("SPY", "de"),
    ("", "tr"),
])
def test_correct_or_unjudgeable_prose_passes(text, lang):
    assert wrong_language(text, lang) is None
