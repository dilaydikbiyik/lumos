"""
Alternatives for each role: offered while teaching, never as advice.

Suggested so the reader is shown CHOICES rather than a single answer: beside
each fund the portfolio can hold, the funds that could have stood in its
place and what measurably differs. These tests hold it to being complete in
every language, buyable where it is shown, consistent with the engine's own
rule, and impersonal.
"""
import numpy as np
import pandas as pd
import pytest

from backend.markets import MARKET_PACKS, get_market_pack
from backend.services.language_check import wrong_language


def _series(seed, years=20):
    n = int(252 * years)
    rng = np.random.default_rng(seed)
    return pd.Series(100 * np.cumprod(1 + rng.normal(0.0002, 0.008, n)),
                     index=pd.date_range("2006-01-02", periods=n, freq="B"))


@pytest.fixture
def svc(monkeypatch):
    from backend.services import cache as cache_service
    from backend.services import role_alternatives

    calls = []

    def history(tickers, period="1y", adjusted=True):
        calls.append((tuple(tickers), period, adjusted))
        return {tk: _series(abs(hash(tk)) % 9999) for tk in tickers}

    monkeypatch.setattr(role_alternatives, "fetch_price_history", history)
    monkeypatch.setattr(cache_service, "get", lambda k: None)
    monkeypatch.setattr(cache_service, "set", lambda k, v, ttl=None: None)
    role_alternatives.calls = calls
    return role_alternatives


@pytest.mark.parametrize("market", sorted(MARKET_PACKS))
@pytest.mark.parametrize("lang", ["tr", "en", "de"])
def test_every_fund_shown_says_what_it_holds_in_the_reader_s_language(svc, market, lang):
    body = svc.alternatives(market, lang)
    assert body["roles"], f"{market} has no alternatives at all"
    for chosen, entry in body["roles"].items():
        assert entry["note"] and not entry["note"].startswith("alternatives."), entry["note"]
        assert wrong_language(entry["note"], lang) is None, entry["note"]
        for row in entry["rows"]:
            assert row["holds"] and not row["holds"].startswith("holds."), (
                f"{row['ticker']} has no 'holds' line in {lang}")
            assert wrong_language(row["holds"], lang) is None, (row["ticker"], lang, row["holds"])


def test_german_alternatives_are_funds_a_german_retail_investor_can_buy():
    """
    EU retail investors cannot buy US-domiciled ETFs, which is why the German
    universe is all UCITS on Xetra. An alternative shown there must be too —
    offering a choice the reader is not allowed to take teaches the wrong
    thing.
    """
    pack = get_market_pack("DE")
    for chosen, alts in pack.role_alternatives.items():
        for alt in alts:
            assert alt["ticker"].endswith(".DE"), (chosen, alt["ticker"])


@pytest.mark.parametrize("market", sorted(MARKET_PACKS))
def test_same_holdings_alternatives_follow_the_engine_s_own_overlap_rule(svc, market):
    """A table that disagreed with the engine would teach a rule it does not apply."""
    from backend.services.portfolio_engine import _overlap_group

    pack = get_market_pack(market)
    group_of = {a["ticker"]: _overlap_group(a) for a in [*pack.asset_universe, *pack.reit_assets]}
    for chosen, entry in svc.alternatives(market, "en")["roles"].items():
        if entry["kind"] != "same_holdings":
            continue
        for row in entry["rows"]:
            assert group_of[row["ticker"]] == group_of[chosen], (market, chosen, row["ticker"])


def test_the_role_fund_comes_first_and_nothing_is_ranked(svc):
    for chosen, entry in svc.alternatives("US", "en")["roles"].items():
        rows = entry["rows"]
        assert rows[0]["ticker"] == chosen
        names = [r["name"] for r in rows[1:]]
        assert names == sorted(names, key=str.casefold), "alternatives must be in name order"
        for r in rows:
            assert not {"score", "rank", "rating", "better", "best"} & {k.lower() for k in r}


def test_every_fund_is_measured_in_one_fetch_on_one_basis(svc):
    svc.alternatives("TR", "tr")
    assert len(svc.calls) == 1, "every fund compared must come from one fetch"
    _, period, adjusted = svc.calls[0]
    assert period == "max" and adjusted is True


def test_the_answer_does_not_depend_on_who_asks(client, svc):
    from backend.main import app
    from backend.middleware.verify_clerk import get_current_user

    answers = []
    for uid, tol in (("calm", "low"), ("bold", "high")):
        app.dependency_overrides[get_current_user] = lambda uid=uid: uid
        client.post("/profile", json={"budget": 100_000, "time_horizon": "long",
                                      "loss_tolerance": tol, "goal": "growth",
                                      "experience": "beginner"})
        answers.append(client.get("/planning/alternatives").json())
    assert answers[0] == answers[1]
