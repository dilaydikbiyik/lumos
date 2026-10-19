"""
The sentence beside the scenario band must not predict.

The card's own text says "Bu bir tahmin DEĞİL" / "This is NOT a forecast",
and the guard above it refuses to draw a band at all when the record holds
too few independent periods. A news sentence next to that saying "analysts
expect further declines" contradicts the claim — not numerically, IN KIND.
The figures stay a measurement while the prose beside them predicts, and
the reader cannot tell the two halves are different sorts of statement.

The portfolio consistency rule does NOT apply here and must not be reused:
this sentence makes no claim about the reader's allocation, so there is
nothing to compare it against. Reusing a rule across prompts that promise
different things is how the REIT guard started deleting correct work.

What applies instead is structural isolation — already tested in
test_projection.py, which asserts every other field is byte-identical with
and without the sentence — plus the forecast check here.
"""
import pytest

from backend.services.forecast_language import is_forecast, markers_in


# ── forecasts, which must be caught ─────────────────────────────────────────

@pytest.mark.parametrize("text", [
    # Turkish analyst copy, both voices. The first draft of the marker list
    # had only the passive "bekleniyor", so this exact sentence — the most
    # common forecast shape in Turkish financial news — walked through.
    "Analistler düşüşün süreceğini bekliyor.",
    "Ekonomistler toparlanma bekliyorlar.",
    "Fed'in faizi indirmesi bekleniyor.",
    "Düşüşün devam edeceği öngörülüyor.",
    "Hedef fiyat yukarı yönlü revize edildi.",
    "Endeksin yükselecek olması bekleniyor.",
    # English
    "Analysts expect further declines in the coming weeks.",
    "The Fed is likely to cut rates.",
    "Rates are expected to fall.",
    "The price target was raised.",
    # German
    "Die EZB dürfte die Zinsen senken.",
    "Eine Erholung wird erwartet.",
    "Die Prognose wurde angehoben.",
    "Der Index wird steigen.",
])
def test_a_forecast_is_recognised(text):
    assert is_forecast(text), f"forecast not caught: {text!r}"
    assert markers_in(text), "a catch with no marker cannot be explained in a log"


# ── reports, which must pass ────────────────────────────────────────────────

@pytest.mark.parametrize("text", [
    # The past, which is what a digest is supposed to describe.
    "Piyasalar bu hafta dalgalandı.",
    "Enflasyon verisi açıklandı.",
    "Enflasyon verisi beklentinin altında kaldı.",
    "Markets fell sharply yesterday.",
    "The central bank raised rates at its last meeting.",
    "Der Index gab gestern nach.",
    # A fact about VOLATILITY, not a claim about what happens next. This is
    # the distinction the rule has to hold: "markets can fall" is true of
    # markets, "markets will fall" is a prediction.
    "Borsa düşebilir, bu normaldir.",
    "Portföyün değeri kısa vadede düşebilir.",
    "Stock prices can fall as well as rise.",
    "Kurse können fallen.",
    # The app's own calming language must survive, or the coach loses its voice.
    "Şu an yapman gereken bir şey yok.",
    "There is nothing you need to do right now.",
])
def test_a_report_is_not_mistaken_for_a_forecast(text):
    assert not is_forecast(text), f"false positive: {text!r} -> {markers_in(text)}"


def test_empty_text_is_not_a_forecast():
    assert is_forecast("") is False
    assert markers_in("") == []


# ── the wiring, which is the part a pure test cannot prove ──────────────────

def _digest(**fields):
    base = {"headline": "Manşet", "why_it_matters": "Bu seni şöyle etkiler.",
            "calmness_note": "Şu an yapman gereken bir şey yok."}
    base.update(fields)
    return [base]


def test_the_sentence_comes_from_why_it_matters_not_the_headline():
    """
    The latent bug this replaced: the function read "takeaway" then
    "summary", and the digest emits NEITHER — they appear nowhere in this
    repository — so the chain always landed on the headline. Of the three
    fields, the headline is the one most likely to carry a forecast, while
    the two written to be calm and non-predictive went unused.
    """
    from unittest.mock import patch

    from backend.services import news_service

    with patch.object(news_service, "get_daily_digest", return_value=_digest()):
        assert news_service.context_sentence() == "Bu seni şöyle etkiler."


def test_a_forecast_in_the_digest_yields_no_sentence_at_all():
    """
    Dropped, not shown. The card is designed to render without a sentence —
    this function already returns None by design — so the cost of dropping
    one is close to zero, while printing a forecast costs the card the only
    promise it makes.
    """
    from unittest.mock import patch

    from backend.services import news_service

    forecast = _digest(why_it_matters="Analistler düşüşün süreceğini bekliyor.")
    with patch.object(news_service, "get_daily_digest", return_value=forecast):
        assert news_service.context_sentence() is None


def test_a_digest_without_the_field_yields_nothing_rather_than_the_headline():
    """
    Falling back to the headline is exactly the behaviour that was removed.
    An empty slot is the honest answer.
    """
    from unittest.mock import patch

    from backend.services import news_service

    with patch.object(news_service, "get_daily_digest",
                      return_value=[{"headline": "Fed faizi indirebilir"}]):
        assert news_service.context_sentence() is None


def test_the_digest_prompt_forbids_prediction_not_only_alarm():
    """
    A rule over the prompt itself. "Never use alarmist words" was the only
    instruction, and alarm is not prediction: "the Fed may cut rates" is
    perfectly calm and still a forecast.
    """
    from backend.services.news_service import _DIGEST_SYSTEM

    assert "NEVER PREDICT" in _DIGEST_SYSTEM
    assert "alarmist" in _DIGEST_SYSTEM, "the original instruction was dropped"


# ── the digest itself, not only the sentence pulled from it ─────────────────

def test_a_predictive_item_is_dropped_from_the_digest(monkeypatch):
    """
    The prompt forbids prediction for every item; the check was enforcing it
    on one of two consumers. /news renders these cards straight to the
    dashboard, so a predictive item reached the reader there while the
    identical text would have been dropped beside a projection.
    """
    from backend.services import cache as cache_service
    from backend.services import news_service

    items = [
        {"headline": "Enflasyon açıklandı", "why_it_matters": "Bu seni şöyle etkiler.",
         "calmness_note": "Yapman gereken bir şey yok."},
        {"headline": "Faiz kararı", "why_it_matters": "Analistler indirim bekliyor.",
         "calmness_note": "Sakin ol."},
    ]
    monkeypatch.setattr(news_service, "fetch_headlines", lambda market="TR": [{"title": "x"}])
    monkeypatch.setattr(news_service, "generate_text", lambda *a, **k: "[]")
    monkeypatch.setattr("backend.services.json_extract.extract_json_array", lambda raw: items)
    monkeypatch.setattr(cache_service, "get", lambda key: None)
    monkeypatch.setattr(cache_service, "set", lambda key, value, ttl=None: None)

    kept = news_service.get_daily_digest()
    assert len(kept) == 1, f"the forecast item survived: {kept}"
    assert kept[0]["headline"] == "Enflasyon açıklandı"


# ── negation: the fix for a shipped bug ─────────────────────────────────────
#
# The first version of this rule flagged any marker anywhere, so it dropped
# exactly the sentences this app exists to produce. Measured against the
# app's 239 translated strings it fired on 12, and SEVEN of those were the
# honesty notes asserting that a figure is not a forecast — a rule that
# deletes the sentence "this is not a forecast" for containing the word
# "forecast" is worse than no rule.
#
# The digest filter was live with that bug: an item whose calmness note said
# "nobody can predict the market" would have been dropped.

@pytest.mark.parametrize("text", [
    # Turkish negates with a SUFFIX, which no word-list catches:
    # öngör|eme|z. This is the case that needed its own pattern.
    "Kimse borsanın ne yapacağını öngöremez.",
    "Hiç kimse faizin ne olacağını tahmin edemez.",
    "Bu bir tahmin değil, geçmişin dağılımı.",
    # English
    "Nobody can forecast the market.",
    "This is NOT a forecast.",
    "No one is expected to time this correctly.",
    # German
    "Das ist keine Prognose.",
    "Niemand kann eine Prognose stellen.",
])
def test_a_negated_marker_is_not_a_forecast(text):
    """Saying nobody can predict is the opposite of predicting."""
    assert not is_forecast(text), f"negation missed: {text!r} -> {markers_in(text)}"


def test_the_apps_own_honesty_note_survives_the_rule():
    """
    The specific sentence the first version deleted, in all three languages,
    read from the live catalogue rather than retyped here — so a reword of
    the disclaimer is still covered.
    """
    from backend.i18n import _C

    note = _C["projection.note_asset"]
    for lang, text in note.items():
        rendered = text.replace("{ticker}", "SPY").replace("{years}", "5")
        assert not is_forecast(rendered), (
            f"the app's own 'this is not a forecast' note [{lang}] trips the "
            f"forecast rule: {markers_in(rendered)}"
        )


def test_negation_does_not_excuse_a_forecast_elsewhere_in_the_sentence():
    """
    The window is one clause. A negation at the start must not license a
    prediction at the end, or "nobody knows, but rates will fall" passes.
    """
    text = ("Kimse kesin bir şey bilemez. Yine de analistler düşüşün "
            "süreceğini bekliyor ve hedef fiyat yükseltildi.")
    assert is_forecast(text), f"a forecast slipped through: {markers_in(text)}"


def test_a_calm_digest_item_is_not_dropped_as_a_forecast(monkeypatch):
    """
    End to end, on the bug as shipped: this item's calmness note is the most
    valuable sentence the digest can carry, and the live filter removed it.
    """
    from backend.services import cache as cache_service
    from backend.services import news_service

    items = [{
        "headline": "Faiz kararı açıklandı",
        "why_it_matters": "Bu, kredi maliyetini etkiler.",
        "calmness_note": "Kimse bundan sonrasını öngöremez; yapman gereken bir şey yok.",
    }]
    monkeypatch.setattr(news_service, "fetch_headlines", lambda market="TR": [{"title": "x"}])
    monkeypatch.setattr(news_service, "generate_text", lambda *a, **k: "[]")
    monkeypatch.setattr("backend.services.json_extract.extract_json_array", lambda raw: items)
    monkeypatch.setattr(cache_service, "get", lambda key: None)
    monkeypatch.setattr(cache_service, "set", lambda key, value, ttl=None: None)

    assert news_service.get_daily_digest() == items, "a calm item was dropped"
