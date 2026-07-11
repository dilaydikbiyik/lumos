"""
Per-province housing intelligence tests — EVDS mocked.
"""
from unittest.mock import patch

from backend.services.evds_service import PROVINCES, _quarter_to_month
from backend.services.province_intelligence import project_province, rank_provinces


def _fake_prices():
    # 16 years quarterly: Muğla grows fast, Ankara moderately
    def series(start, quarterly_growth):
        out = {}
        val = start
        for year in range(2010, 2026):
            for q in (3, 6, 9, 12):
                out[f"{year}-{q:02d}"] = val
                val *= quarterly_growth
        return out
    return {
        "MUGLA": {"name": "Muğla", "prices": series(1000, 1.045)},
        "ANK": {"name": "Ankara", "prices": series(1500, 1.03)},
    }


def test_quarter_to_month_conversion():
    assert _quarter_to_month("2026-Q1") == "2026-03"
    assert _quarter_to_month("2010-Q4") == "2010-12"


def test_all_81_provinces_mapped():
    assert len(PROVINCES) == 81  # 3 metro special codes + 78 provinces
    assert PROVINCES["MARAS"] == "Kahramanmaraş"
    assert PROVINCES["URFA"] == "Şanlıurfa"
    assert PROVINCES["IST"] == "İstanbul"


def test_rank_provinces_orders_by_real_change():
    with patch("backend.services.province_intelligence.evds_service.get_province_unit_prices",
               side_effect=lambda: _fake_prices()):
        r = rank_provinces(3)
    assert r["available"] is True
    assert r["provinces"][0]["province"] == "Muğla"  # faster growth ranks first
    assert r["provinces"][0]["price_per_m2"] > 0
    assert "İl ortalaması" in r["honesty_note"]


def test_rank_provinces_invalid_horizon_defaults():
    with patch("backend.services.province_intelligence.evds_service.get_province_unit_prices",
               side_effect=lambda: _fake_prices()):
        r = rank_provinces(7)
    assert r["horizon_years"] == 3


def test_project_province_has_per_window_real_band():
    with patch("backend.services.province_intelligence.evds_service.get_province_unit_prices",
               side_effect=lambda: _fake_prices()):
        p = project_province("MUGLA", 1_000_000, 5)
    assert p["available"] is True
    assert p["pessimistic"]["value"] <= p["typical"]["value"] <= p["optimistic"]["value"]
    assert p["real_band"] is not None
    assert p["real_band"]["pessimistic_pct"] <= p["real_band"]["optimistic_pct"]
    assert "kendi enflasyonundan arındırılmıştır" in p["honesty_note"]


def test_province_endpoints(client):
    with patch("backend.services.province_intelligence.evds_service.get_province_unit_prices",
               side_effect=lambda: _fake_prices()):
        r1 = client.get("/planning/province-intelligence?horizon_years=5")
        r2 = client.post("/planning/projection/province",
                         json={"region_code": "mugla", "amount": 500000, "years": 5})
    assert r1.status_code == 200 and r1.json()["available"] is True
    assert r2.status_code == 200 and r2.json()["province"] == "Muğla"
