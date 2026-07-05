"""
Future scenario band tests — market data and EVDS mocked.
"""
import numpy as np
import pandas as pd
import pytest
from unittest.mock import patch

from backend.services.projection import project_asset, project_region

# 10 years of daily data, steady ~12%/yr growth with noise
_N = 2520
_rng = np.random.default_rng(7)
_GROWTH = pd.Series(
    100 * np.cumprod(1 + _rng.normal(0.00045, 0.01, _N)),
    index=pd.date_range("2016-01-01", periods=_N, freq="B"),
)


def _fake_history(tickers, period="10y"):
    return {t: _GROWTH for t in tickers}


def test_asset_projection_returns_ordered_band():
    with patch("backend.services.projection.fetch_price_history", side_effect=_fake_history):
        r = project_asset("SPY", amount=100000, years=5)
    assert r["available"] is True
    assert r["pessimistic"]["value"] <= r["typical"]["value"] <= r["optimistic"]["value"]
    assert r["windows_analysed"] >= 6
    assert "tahmin DEĞİL" in r["honesty_note"]


def test_asset_projection_applies_amount():
    with patch("backend.services.projection.fetch_price_history", side_effect=_fake_history):
        r = project_asset("SPY", amount=50000, years=1)
    typ = r["typical"]
    assert typ["value"] == pytest.approx(50000 * (1 + typ["return_pct"] / 100), rel=0.01)


def test_asset_projection_refuses_thin_history():
    short = {"NEW": _GROWTH.iloc[:300]}  # ~1.2 yıl veri
    with patch("backend.services.projection.fetch_price_history", return_value=short):
        r = project_asset("NEW", amount=10000, years=5)
    assert r["available"] is False
    assert "geçmiş veri yok" in r["reason"]


def _fake_regions(start="01-01-2023"):
    # 40 ay, aylık ~%2 artış
    index = {f"{2023 + m // 12}-{m % 12 + 1:02d}": 100 * (1.02 ** m) for m in range(40)}
    return {"TP.KFE.TR51": {"region": "Ankara", "index": index}}


def test_region_projection_band_and_real():
    with patch("backend.services.projection.evds_service.get_regional_housing_indices",
               side_effect=_fake_regions):
        r = project_region("TP.KFE.TR51", amount=1000000, years=2)
    assert r["available"] is True
    assert r["typical"]["return_pct"] > 0
    assert "typical_real_return_pct" in r
    assert "NUTS2" in r["honesty_note"]


def test_region_projection_honest_about_short_history():
    with patch("backend.services.projection.evds_service.get_regional_housing_indices",
               side_effect=_fake_regions):
        r = project_region("TP.KFE.TR51", amount=1000000, years=3)
    assert r["available"] is False
    assert "yeterli pencere yok" in r["reason"]


def test_asset_projection_endpoint(client):
    with patch("backend.services.projection.fetch_price_history", side_effect=_fake_history):
        res = client.post(
            "/planning/projection/asset",
            json={"ticker": "spy", "amount": 100000, "years": 5},
        )
    assert res.status_code == 200
    assert res.json()["ticker"] == "SPY"


def test_projection_endpoint_rejects_bad_years(client):
    res = client.post(
        "/planning/projection/asset",
        json={"ticker": "SPY", "amount": 100000, "years": 7},
    )
    assert res.status_code == 422
