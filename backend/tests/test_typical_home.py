"""
What a typical home costs, per market — and the numbers held to each other.

Written after the region explorer offered "what if you had bought for
1,000,000" in every market: 18 m² in Türkiye, a large house in Germany.
"""
import pytest

from backend.markets import MARKET_PACKS


@pytest.fixture
def svc(monkeypatch):
    from backend.services import cache as cache_service
    from backend.services import typical_home

    monkeypatch.setattr(cache_service, "get", lambda k: None)
    monkeypatch.setattr(cache_service, "set", lambda k, v, ttl=None: None)
    return typical_home


@pytest.mark.parametrize("code", sorted(MARKET_PACKS))
def test_every_market_declares_a_dated_typical_home(code):
    spec = MARKET_PACKS[code].typical_home
    assert spec["source"] in ("evds", "fred", "static")
    assert spec["fallback"] > 0 and spec["as_of"] and spec["source_name"]
    if spec["source"] in ("evds", "static"):
        assert spec["m2"] > 0
    if spec["source"] == "static":
        assert spec["price_per_m2"] * spec["m2"] == pytest.approx(spec["fallback"], rel=0.05)


@pytest.mark.parametrize("code", sorted(MARKET_PACKS))
def test_the_entry_threshold_is_a_plausible_share_of_a_typical_home(code):
    """The entry threshold is CASH — a down payment plus purchase costs — so
    it must sit between a tenth and a half of what an ordinary home costs.
    Outside that band one of the two numbers has stopped describing the
    market (Türkiye's prices rise fast enough to break this within years)."""
    pack = MARKET_PACKS[code]
    share = pack.property_entry_threshold / pack.typical_home["fallback"]
    assert 0.1 <= share <= 0.5, (code, round(share, 2))


def test_a_dead_live_source_falls_back_to_the_dated_figure(svc, monkeypatch):
    def boom(spec):
        raise RuntimeError("upstream down")
    monkeypatch.setattr(svc, "_live", boom)
    out = svc.typical_home("TR")
    spec = MARKET_PACKS["TR"].typical_home
    assert out["live"] is False
    assert out["price"] == round(spec["fallback"]) and out["as_of"] == spec["as_of"]


def test_a_live_reading_is_used_and_dated(svc, monkeypatch):
    monkeypatch.setattr(svc, "_live", lambda spec: (412_345.0, "2026-10"))
    out = svc.typical_home("US")
    assert out["live"] is True and out["price"] == 412_345 and out["as_of"] == "2026-10"
    assert out["example_amount"] == 410_000


def test_example_amounts_are_round_and_in_the_markets_currency(svc, monkeypatch):
    monkeypatch.setattr(svc, "_live", lambda spec: None)
    seen = {}
    for code in MARKET_PACKS:
        out = svc.typical_home(code)
        assert out["currency"] == MARKET_PACKS[code].currency
        digits = str(int(out["example_amount"])).rstrip("0")
        assert len(digits) <= 2, out["example_amount"]
        seen[code] = out["example_amount"]
    assert len(set(seen.values())) == len(seen), "one number for every market again"
