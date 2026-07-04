"""
Region intelligence + EVDS service tests — EVDS HTTP mocked.
"""
from unittest.mock import patch

from backend.services.evds_service import fetch_series
from backend.services.region_intelligence import rank_regions

FAKE_KFE = {
    "TP.KFE.TR51": {
        "region": "Ankara",
        # 12 months: 100 -> 150 (nominal +50%)
        "index": {f"2025-{m:02d}": 100 + (m - 1) * 4.5 for m in range(1, 13)},
    },
    "TP.KFE.TR62": {
        "region": "Adana, Mersin",
        # 12 months: 100 -> 110 (nominal +10%, below inflation)
        "index": {f"2025-{m:02d}": 100 + (m - 1) * 0.9 for m in range(1, 13)},
    },
}


def _fake_indices(start="01-01-2023"):
    return FAKE_KFE


def test_rank_regions_orders_by_real_change():
    with patch("backend.services.region_intelligence.evds_service.get_regional_housing_indices",
               side_effect=_fake_indices):
        result = rank_regions(horizon_years=1)
    assert result["available"] is True
    assert result["regions"][0]["region"] == "Ankara"
    assert result["regions"][0]["rank"] == 1
    assert result["honesty_note"].startswith("Bu sıralama bölge")


def test_rank_regions_includes_real_change():
    with patch("backend.services.region_intelligence.evds_service.get_regional_housing_indices",
               side_effect=_fake_indices):
        result = rank_regions(horizon_years=1)
    for row in result["regions"]:
        assert "real_change_pct" in row
        assert row["real_change_pct"] < row["nominal_change_pct"] or row["nominal_change_pct"] == 0


def test_rank_regions_handles_no_data():
    with patch("backend.services.region_intelligence.evds_service.get_regional_housing_indices",
               return_value={}):
        result = rank_regions()
    assert result["available"] is False


def test_fetch_series_parses_evds_shape():
    class FakeResponse:
        def raise_for_status(self):
            pass
        def json(self):
            return {"items": [
                {"Tarih": "2026-5", "TP_FG_J0": "3500.5", "UNIXTIME": {}},
                {"Tarih": "2026-6", "TP_FG_J0": None},  # null values skipped
            ]}

    with patch("backend.services.evds_service.cache_service.get", return_value=None), \
         patch("backend.services.evds_service.cache_service.set"), \
         patch("backend.services.evds_service.httpx.get", return_value=FakeResponse()):
        result = fetch_series("TP.FG.J0", "01-01-2026", "01-07-2026")
    assert result == {"2026-05": 3500.5}


def test_region_endpoint(client):
    with patch("backend.services.region_intelligence.evds_service.get_regional_housing_indices",
               side_effect=_fake_indices):
        res = client.get("/planning/region-intelligence?horizon_years=1")
    assert res.status_code == 200
    assert res.json()["available"] is True
