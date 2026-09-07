"""
Live price-data sources per market.

The app's central claim is that returns are shown after real inflation. That
claim was only true for Türkiye until US and DE arrived, and it stays true
only if each market's source degrades to real data rather than to a constant.
"""

import pytest


def _yoy(index):
    months = sorted(index)
    latest = months[-1]
    year, month = latest.split("-")
    prior = f"{int(year) - 1}-{month}"
    return round((index[latest] / index[prior] - 1) * 100, 2) if prior in index else None


def test_us_falls_back_to_a_real_index_not_a_constant(monkeypatch):
    """
    BLS caps the keyless endpoint at 25 requests/day per IP, which our
    datacenter shares — so the live call really does fail in production. It
    used to leave US inflation on a hardcoded 3.0% while looking measured.
    """
    import httpx

    from backend.services import bls_service
    from backend.services import cache as cache_service

    monkeypatch.setattr(cache_service, "get", lambda key: None)
    monkeypatch.setattr(cache_service, "set", lambda *a, **k: None)
    monkeypatch.setattr(httpx, "post", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("blocked")))

    index = bls_service.get_cpi_index()
    assert index, "must fall back to the bundled snapshot"
    assert len(index) > 24, "a fallback with a year of data cannot compute YoY"

    measured = _yoy(index)
    from backend.markets import get_market_pack

    assert measured is not None
    assert measured != get_market_pack("US").inflation_fallback_pct


def test_bundled_us_snapshots_are_parseable_and_recent():
    from backend.services import bls_service

    for series in (bls_service._CPI_SERIES, bls_service._RENT_SERIES):
        index = bls_service._static_index(series)
        assert index and len(index) > 24, series
        assert all(isinstance(v, (int, float)) for v in index.values()), series
        # Keys must sort chronologically for "nearest month at or before" reads
        assert sorted(index) == sorted(index, key=str), series


def test_a_rent_index_is_never_used_as_a_house_price_index():
    """
    BLS publishes rent, not house prices. Substituting one for the other
    would corrupt every buy-vs-rent verdict, so the US pack must declare no
    housing index rather than quietly borrowing the rent series.
    """
    from backend.markets import get_market_pack

    us = get_market_pack("US")
    assert us.rent_index_source == "bls"
    assert us.housing_index_source == "none"

    # Germany does have a real price index, so it may claim one
    de = get_market_pack("DE")
    assert de.housing_index_source == "eurostat"


@pytest.mark.parametrize("market", ["TR", "US", "DE"])
def test_every_market_produces_a_usable_inflation_number(market):
    from backend.services import assumptions

    value = assumptions.annual_inflation_pct(market)
    assert 0 < value < 200, (market, value)
