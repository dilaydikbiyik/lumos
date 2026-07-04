"""
Rent-vs-buy and listing bridge tests.
"""
from backend.services.listing_bridge import build_listing_links
from backend.services.rent_vs_buy import compare_rent_vs_buy


def test_rent_vs_buy_returns_both_scenarios():
    result = compare_rent_vs_buy(down_payment=500000, monthly_rent=8000, years=5)
    assert result["buy"]["property_value"] > 500000
    assert result["rent"]["portfolio_value"] > 500000
    assert result["rent"]["total_rent_paid"] > 0
    assert result["buy"]["total_rent_paid"] == 0


def test_rent_vs_buy_higher_portfolio_growth_favors_renting():
    result = compare_rent_vs_buy(
        down_payment=500000, monthly_rent=1000, years=10,
        housing_annual_growth_pct=10, portfolio_annual_growth_pct=30,
    )
    assert result["rent"]["net_position"] > result["buy"]["net_position"]


def test_listing_links_include_major_portals():
    links = build_listing_links("Ankara", "Gölbaşı", "arsa")
    sites = [link["site"] for link in links]
    assert "Sahibinden" in sites
    assert "Emlakjet" in sites
    assert all("ankara" in link["url"] for link in links)


def test_listing_links_without_district():
    links = build_listing_links("İzmir", "", "daire")
    assert all(link["url"] for link in links)


def test_rent_vs_buy_endpoint(client):
    res = client.post("/planning/rent-vs-buy", json={
        "down_payment": 500000, "monthly_rent": 8000, "years": 5,
    })
    assert res.status_code == 200
    assert res.json()["years"] == 5


def test_listing_links_endpoint(client):
    res = client.post("/planning/listing-links", json={
        "il": "Ankara", "ilce": "Gölbaşı", "asset_type": "arsa",
    })
    assert res.status_code == 200
    assert len(res.json()["links"]) == 2
