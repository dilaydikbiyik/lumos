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
from backend.services.explanation_check import contradictions, verified_or_dropped


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
    assert "QQQ" not in (body.get("metadata", {}).get("reit_explanation") or "")


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
