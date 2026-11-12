"""
What the models are told, and what the checker lets through — per market.

Found by the sixth sweep: the profile extractor was told every amount is in
TRY, the REIT prompt named two US funds and a US return to every reader,
and the checker deleted correct Turkish/German explanations for words like
"ABD" and "EZB".
"""
import pytest

from backend.services.path_portfolio import build_for_path


@pytest.mark.parametrize("sentence", [
    "Portföyünün %{w}'i ABD'nin en büyük şirketlerine (S&P 500) gidiyor.",
    "FED faiz artırdığında hisseler sallanabilir; portföyünün %{w}'i bu fonda.",
    "TCMB faiz indirirse TL değer kaybedebilir; %{w} bu yüzden dolar fonunda.",
])
def test_ordinary_capitalised_words_are_not_tickers(sentence):
    from backend.services import explanation_check

    portfolio, _ = build_for_path("stocks", 6.6, 400_000, "TR", "tr")
    spy = next(a for a in portfolio.allocations if a.ticker == "SPY")
    text = sentence.format(w=round(spy.weight * 100, 1))
    assert explanation_check.contradictions(text, portfolio) == []


def test_a_made_up_ticker_is_still_caught():
    from backend.services import explanation_check

    portfolio, _ = build_for_path("stocks", 6.6, 400_000, "TR", "tr")
    assert explanation_check.contradictions("TSLA alırsan iyi olur.", portfolio)


@pytest.mark.parametrize("currency", ["TRY", "USD", "EUR"])
def test_the_extractor_is_told_the_readers_currency(currency):
    from unittest.mock import patch

    from backend.services import ai_service

    seen = {}

    def fake_dispatch(messages, system, **kw):
        seen["system"] = system
        return '{"budget": 1000, "time_horizon": "long", "loss_tolerance": "medium", ' \
               '"goal": "growth", "experience": "beginner"}'

    with patch.object(ai_service, "_dispatch", side_effect=fake_dispatch):
        ai_service.extract_profile([{"role": "user", "content": "x"}], "en", currency)
    assert f"in {currency}" in seen["system"]
    assert "{currency}" not in seen["system"]
    if currency != "TRY":
        assert "in TRY" not in seen["system"]


def test_the_reit_prompt_names_only_the_readers_own_funds():
    from unittest.mock import patch

    from backend.services import explainer

    portfolio, _ = build_for_path("real_estate", 6.0, 20_000, "DE", "de")
    seen = {}
    with patch.object(explainer, "generate_text", side_effect=lambda p, **k: seen.setdefault("p", p) or ""):
        explainer.explain_reit_inclusion(portfolio, {}, "de", "DE")
    assert "IQQP.DE" in seen["p"] and "VNQ" not in seen["p"] and "SCHH" not in seen["p"]
    assert "EUR" in seen["p"]
