"""
The prose must not contradict the figures beside it.

The app's one real consistency risk. The allocation is a deterministic
formula — the same input gives the same portfolio every time — but the
sentence explaining it is written by a model, and nothing checked that the
two agree. Every existing test touching `plain_explanation` either passes
an empty string or asserts a mocked value came back unchanged.

A reader shown "weighted toward gold" beside a chart weighted toward
equities cannot tell which half to believe, and will believe the sentence,
because it is the half written in their language.

Both directions are tested, and the false-positive half matters more:
dropping a CORRECT explanation costs the reader the one part of the page
written for them, so the rule has to be conservative enough to live in
production.
"""
import pytest

from backend.schemas.portfolio import AssetAllocation, PortfolioRecommendResponse
from backend.services.explanation_check import (
    contradictions,
    reit_verified_or_dropped,
    verified_or_dropped,
)


def _portfolio() -> PortfolioRecommendResponse:
    """The shape the engine really produces, weights and all."""
    return PortfolioRecommendResponse(
        risk_score=6.0,
        budget=250_000.0,
        allocations=[
            AssetAllocation(ticker="SPY", name="S&P 500 ETF", weight=0.303, category="stocks"),
            AssetAllocation(ticker="VNQ", name="Vanguard Real Estate ETF", weight=0.282, category="reit"),
            AssetAllocation(ticker="BND", name="Tahvil Fonu", weight=0.148, category="bond"),
            AssetAllocation(ticker="GLD", name="Gold ETF", weight=0.144, category="gold"),
            AssetAllocation(ticker="BIL", name="Nakit / Kısa Vade", weight=0.122, category="cash"),
        ],
        plain_explanation="",
    )


# ── what it must catch ──────────────────────────────────────────────────────

def test_an_instrument_that_is_not_in_the_portfolio_is_caught():
    """
    The worst thing this app could print, because a reader may act on a
    symbol. The prompt is given these holdings and no others, so naming a
    different one is the model supplying an instrument from nowhere.
    """
    text = ("Portföyünün büyük kısmı SPY ve VNQ'da. Ayrıca QQQ ile "
            "teknolojiye de pay ayırdık.")
    problems = contradictions(text, _portfolio())
    assert any("QQQ" in p for p in problems), problems


def test_a_percentage_that_matches_nothing_is_caught():
    text = "Hisselerin payı %55, bu da risk profiline uygun bir denge."
    problems = contradictions(text, _portfolio())
    assert any("55" in p for p in problems), problems


def test_a_wrong_risk_score_is_caught():
    """A fact about the PERSON, altered. 6/10 is theirs; 8/10 is not."""
    text = "Risk puanın 8/10 olduğu için daha agresif bir dağılım seçtik."
    problems = contradictions(text, _portfolio())
    assert any("8" in p and "risk" in p for p in problems), problems


def test_a_contradicting_explanation_is_dropped_not_corrected():
    """
    Editing the model's sentence to match the numbers would produce prose
    nobody wrote and nobody checked. The page is complete without it.
    """
    text = "Portföyün %55'i QQQ'da."
    assert verified_or_dropped(text, _portfolio()) == ""


# ── what it must NOT flag ───────────────────────────────────────────────────

def test_the_real_figures_pass():
    text = ("Portföyünün %30,3'ü S&P 500 ETF'inde (SPY), %28,2'si gayrimenkul "
            "fonunda (VNQ), %14,8'i tahvilde (BND), %14,4'ü altında (GLD) ve "
            "%12,2'si nakitte (BIL). Risk puanın 6/10.")
    assert contradictions(text, _portfolio()) == []


def test_rounded_figures_pass():
    """Prose rounds, and a reader is not harmed by 30 instead of 30.3."""
    text = "Yaklaşık %30'u hisse senedinde, %28'i gayrimenkulde, %14'ü altında."
    assert contradictions(text, _portfolio()) == []


def test_a_category_total_passes():
    """
    Aggregating is the natural way to describe a mix in words. Here each
    category happens to be one holding, so the totals equal the weights —
    the point is that the rule allows totals at all rather than only
    per-holding figures.
    """
    text = "Toplamın %100'ü beş varlığa yayılmış durumda."
    assert contradictions(text, _portfolio()) == []


def test_prose_with_no_figures_at_all_passes():
    """Most explanations are mostly words. None of that is checkable."""
    text = ("Bu karma, paranı tek bir yere bağlamamak için kurulmuş. Düşüş "
            "olduğunda hepsi aynı anda düşmediği için toplam dalgalanma azalır.")
    assert contradictions(text, _portfolio()) == []


@pytest.mark.parametrize("text", [
    # German capitalises every noun. Without the vocabulary guard the ticker
    # rule would fire on ordinary prose and silently delete every German
    # explanation the app ever wrote.
    "Dein Portfolio ist breit gestreut. Der Anteil von GLD liegt bei etwa 14%.",
    # English sentences start with a capital.
    "The mix holds SPY and VNQ. Gold is about 14% of it.",
    # Turkish, with an acronym the app itself uses.
    "Bu bir ETF karması; SPK düzenlemesine tabi fonlar da içeriyor.",
])
def test_ordinary_prose_in_each_language_is_not_mistaken_for_a_ticker(text):
    assert contradictions(text, _portfolio()) == [], text


def test_a_holdings_own_name_is_not_read_as_a_stray_ticker():
    """"Gold ETF" is this portfolio's own name for GLD, not a symbol."""
    text = "Altın tarafı Gold ETF üzerinden, %14,4 ağırlıkla."
    assert contradictions(text, _portfolio()) == []


def test_an_empty_explanation_is_not_a_contradiction():
    """The engine returns one, and the explainer fills it afterwards."""
    assert contradictions("", _portfolio()) == []
    assert verified_or_dropped("", _portfolio()) == ""


def test_a_consistent_explanation_survives_untouched():
    text = "Portföyünün %30,3'ü SPY'de. Risk puanın 6/10."
    assert verified_or_dropped(text, _portfolio()) == text


# ── end to end, through the endpoint ────────────────────────────────────────
#
# The rule above is pure and tested, which proves it works — not that it is
# WIRED. Every existing test of this endpoint mocks the explainer and
# asserts the mocked value came back unchanged, which is exactly the shape
# that would keep passing if the guard were deleted tomorrow.

def test_a_contradicting_explanation_never_reaches_the_client(client):
    """The model invents an instrument; the reader must not receive it."""
    from unittest.mock import patch

    with patch("backend.routers.recommend.explain_portfolio",
               return_value="Portföyünün %55'i QQQ'da."):
        res = client.post("/recommend", json={"risk_score": 6.0, "budget": 250000})

    assert res.status_code == 200
    body = res.json()
    assert body["plain_explanation"] == "", "contradicting prose was served"
    # The numbers are untouched: dropping the paragraph must not cost the
    # reader the answer itself.
    assert body["allocations"], "the allocation disappeared with the prose"

    # Scoped to the EXPLANATION, not the whole response. QQQ legitimately
    # appears in `metadata`: the engine publishes its volatility table and
    # the candidates it REJECTED with the reason for each ("an asset from
    # this category was already chosen"). That is a transparency feature,
    # and a blunt assertion over the whole body mistook it for a leak —
    # which would have made this test fail for the right reason by accident
    # and then been "fixed" by weakening the guard.
    assert "QQQ" not in body["plain_explanation"]


def test_a_consistent_explanation_is_served_normally(client):
    """
    The other half, and the one that matters for false positives: a guard
    that drops everything would also make the test above pass.
    """
    from unittest.mock import patch

    res = client.post("/recommend", json={"risk_score": 6.0, "budget": 250000})
    tickers = [a["ticker"] for a in res.json()["allocations"]]
    honest = f"Portföyün {tickers[0]} ve {tickers[1]} içeriyor. Risk puanın 6/10."

    with patch("backend.routers.recommend.explain_portfolio", return_value=honest):
        res = client.post("/recommend", json={"risk_score": 6.0, "budget": 250000})

    assert res.json()["plain_explanation"] == honest, "consistent prose was dropped"


# ── the REIT explanation, which needed a DIFFERENT rule ─────────────────────
#
# The portfolio checker was applied here first and that was a real bug: it
# silently deleted essentially every REIT explanation the app produced,
# because reit_explain_prompt.txt instructs the model to state figures that
# are deliberately not portfolio weights.
#
# The assertion that was supposed to cover this was vacuous. It checked that
# "QQQ" was absent from an explanation that the test fixture had set to
# "Mocked AI reply" — true whether or not any guard ran at all.

def _reit_prose() -> str:
    """
    The explanation the prompt actually asks for, figures and all. Every
    number here is instructed by reit_explain_prompt.txt:
      "required by law to distribute at least 90% of taxable income"
      "VNQ has delivered ~8-10% annualized returns over 20 years"
    """
    return ("GYO'lar gelir getiren gayrimenkul işleten şirketlerdir ve yasa gereği "
            "vergilendirilebilir gelirlerinin en az %90'ını temettü olarak dağıtmak "
            "zorundadır. VNQ ve SCHH gibi fonlar 20 yılda yıllık ~%8–10 getiri "
            "sağladı; bu gelecek için garanti değildir. Risk puanın 6/10 olduğu "
            "için faiz duyarlılığı senin için kabul edilebilir bir risk.")


def test_the_portfolio_rule_would_delete_a_correct_reit_explanation():
    """
    The bug, pinned so it cannot come back by someone "simplifying" the two
    checkers into one. Three independent reasons, each guaranteed by the
    prompt: the 90% distribution rule, the 8-10% historical range, and GYO
    read as a stray symbol.
    """
    problems = contradictions(_reit_prose(), _portfolio())
    assert len(problems) >= 2, (
        "the portfolio rule no longer objects to correct REIT prose — if that "
        "is because the rule got smarter, good; check reit_verified_or_dropped "
        f"is still needed. problems={problems}"
    )


def test_the_reit_rule_keeps_a_correct_reit_explanation():
    text = _reit_prose()
    assert reit_verified_or_dropped(text, _portfolio()) == text


def test_the_reit_rule_still_catches_a_wrong_risk_score():
    """
    Turning the percentage rule off must not turn the whole check off. The
    risk score IS checkable here: the prompt hands the model the real one.
    """
    text = _reit_prose().replace("6/10", "9/10")
    assert reit_verified_or_dropped(text, _portfolio()) == ""


def test_the_reit_rule_still_catches_an_invented_instrument():
    """The worst case stays guarded: a reader may act on a symbol."""
    text = _reit_prose() + " Ayrıca ARKK da ekledik."
    assert reit_verified_or_dropped(text, _portfolio()) == ""


def test_the_reit_rule_allows_the_engines_own_reit_universe():
    """
    The prompt says "VNQ and/or SCHH" without knowing which was selected, so
    naming the one that was not allocated is the prompt's doing rather than
    an invention. This portfolio holds VNQ; SCHH must still pass.
    """
    text = "SCHH ve VNQ, GYO fonlarının iki örneğidir. Risk puanın 6/10."
    assert reit_verified_or_dropped(text, _portfolio()) == text


def test_a_contradicting_reit_explanation_never_reaches_the_client(client):
    """
    End to end, and NOT vacuous this time: the prose is a real contradiction
    and the assertion is that it was dropped.
    """
    from unittest.mock import patch

    with patch("backend.routers.recommend.explain_reit_inclusion",
               return_value="GYO tarafını ARKK ile kurduk."):
        res = client.post("/recommend", json={"risk_score": 6.0, "budget": 250000})

    assert res.status_code == 200
    body = res.json()
    assert body["includes_reits"] is True, "the fixture must actually include REITs"
    assert body["metadata"].get("reit_explanation") == "", "ARKK reached the reader"


def test_a_correct_reit_explanation_is_served_end_to_end(client):
    """
    The half that would also pass if the guard dropped everything — which is
    exactly how the REIT bug survived its first test.
    """
    from unittest.mock import patch

    with patch("backend.routers.recommend.explain_reit_inclusion",
               return_value=_reit_prose()):
        res = client.post("/recommend", json={"risk_score": 6.0, "budget": 250000})

    assert res.json()["metadata"]["reit_explanation"] == _reit_prose(), (
        "a correct REIT explanation was dropped"
    )
