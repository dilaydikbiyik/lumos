"""
Rent-vs-buy and listing bridge tests.
"""
import pytest

from backend.services.goal_planner import required_monthly_contribution
from backend.services.listing_bridge import build_listing_links
from backend.services.rent_vs_buy import compare_rent_vs_buy


def test_rent_vs_buy_returns_both_scenarios():
    result = compare_rent_vs_buy(down_payment=500000, monthly_rent=8000, years=5)
    # Both strategies produce a comparable net worth for the SAME home
    assert result["buy"]["net_worth"] != 0
    assert result["rent"]["net_worth"] != 0
    assert result["rent"]["total_rent_paid"] > 0
    assert result["verdict"] in ("buy", "rent")


def test_rent_vs_buy_estimates_home_price_from_rent():
    # No home_price given → estimated from rent, and the two scenarios describe
    # the same (realistically-priced) home, not a house worth the down payment.
    result = compare_rent_vs_buy(down_payment=100000, monthly_rent=50000, years=5)
    assert result["home_price_estimated"] is True
    assert result["home_price"] > 1_000_000  # a 50k/month rental is a multi-million home
    assert result["monthly_mortgage"] > result["rent"]["total_rent_paid"] / (5 * 12)


def test_rent_vs_buy_respects_explicit_home_price():
    result = compare_rent_vs_buy(
        down_payment=3_000_000, monthly_rent=50000, years=5, home_price=8_000_000,
    )
    assert result["home_price"] == 8_000_000
    assert result["home_price_estimated"] is False
    assert result["buy"]["remaining_loan"] >= 0


def test_rent_vs_buy_higher_portfolio_growth_favors_renting():
    result = compare_rent_vs_buy(
        down_payment=500000, monthly_rent=1000, years=10, home_price=1_000_000,
        housing_annual_growth_pct=10, portfolio_annual_growth_pct=30,
    )
    assert result["rent"]["net_worth"] > result["buy"]["net_worth"]


def test_rent_vs_buy_reports_real_terms():
    # Inflation erodes big nominal figures; the real value must be lower and shown.
    r = compare_rent_vs_buy(down_payment=100000, monthly_rent=50000, years=5)
    assert r["buy"]["net_worth_real"] < r["buy"]["net_worth"]
    assert r["rent"]["net_worth_real"] < r["rent"]["net_worth"]
    assert r["assumptions"]["annual_inflation_pct"] > 0


def test_planning_tools_use_live_market_linked_assumptions():
    # Coherence: both tools resolve rates from the single, live-market-linked
    # source (inflation from CPI; growth as a real spread over it).
    from backend.services import assumptions
    r = compare_rent_vs_buy(down_payment=500000, monthly_rent=8000, years=5)
    assert r["assumptions"]["portfolio_annual_growth_pct"] == assumptions.portfolio_growth_pct()
    assert r["assumptions"]["annual_inflation_pct"] == assumptions.annual_inflation_pct()
    # Portfolio growth must beat inflation by exactly the documented real spread
    assert assumptions.real_rate_pct(assumptions.portfolio_growth_pct()) == pytest.approx(
        assumptions.PORTFOLIO_REAL_SPREAD_PCT, abs=0.2
    )


def test_inflation_is_measured_not_hardcoded():
    # The live inflation figure comes from the CPI index (static file here),
    # so it reflects real data rather than a frozen constant.
    from backend.services import assumptions
    from backend.services.inflation_service import trailing_annual_inflation_pct
    assert trailing_annual_inflation_pct() > 0
    assert assumptions.annual_inflation_pct() > 0


def test_goal_plan_reports_target_real_value():
    plan = required_monthly_contribution(target_amount=800000, years=3, current_savings=0)
    assert plan["target_real_value"] < 800000  # eroded by inflation
    assert plan["annual_inflation_pct"] > 0


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


# ── Purchase and ownership costs ────────────────────────────────────────────

def test_purchase_costs_are_charged_on_the_price():
    from backend.services import assumptions
    from backend.services.rent_vs_buy import compare_rent_vs_buy

    r = compare_rent_vs_buy(2_000_000, 30_000, 10, home_price=5_000_000)
    expected = 5_000_000 * (
        assumptions.TITLE_DEED_FEE_PCT + assumptions.agency_commission_with_vat_pct()
    ) / 100
    assert r["buy"]["purchase_costs"] == expected


def test_upkeep_accumulates_over_the_horizon():
    from backend.services.rent_vs_buy import compare_rent_vs_buy

    short = compare_rent_vs_buy(2_000_000, 30_000, 5, home_price=5_000_000)
    long = compare_rent_vs_buy(2_000_000, 30_000, 10, home_price=5_000_000)
    assert long["buy"]["total_upkeep_paid"] > short["buy"]["total_upkeep_paid"] > 0


def test_costs_make_buying_less_attractive():
    """The whole point: ignoring these silently favours buying."""
    from backend.services import assumptions
    from backend.services.rent_vs_buy import compare_rent_vs_buy

    with_costs = compare_rent_vs_buy(2_000_000, 30_000, 10, home_price=5_000_000)

    deed, agency, upkeep = (
        assumptions.TITLE_DEED_FEE_PCT,
        assumptions.AGENCY_COMMISSION_PCT,
        assumptions.ANNUAL_UPKEEP_PCT,
    )
    assumptions.TITLE_DEED_FEE_PCT = 0.0
    assumptions.AGENCY_COMMISSION_PCT = 0.0
    assumptions.ANNUAL_UPKEEP_PCT = 0.0
    try:
        without = compare_rent_vs_buy(2_000_000, 30_000, 10, home_price=5_000_000)
    finally:
        assumptions.TITLE_DEED_FEE_PCT = deed
        assumptions.AGENCY_COMMISSION_PCT = agency
        assumptions.ANNUAL_UPKEEP_PCT = upkeep

    buy_edge_with = with_costs["buy"]["net_worth"] - with_costs["rent"]["net_worth"]
    buy_edge_without = without["buy"]["net_worth"] - without["rent"]["net_worth"]
    assert buy_edge_with < buy_edge_without


def test_renter_keeps_the_money_the_buyer_spent_on_costs():
    """The costs the buyer pays at closing stay invested on the renting side."""
    from backend.services.rent_vs_buy import compare_rent_vs_buy

    r = compare_rent_vs_buy(2_000_000, 30_000, 1, home_price=5_000_000)
    assert r["rent"]["portfolio_value"] > 2_000_000 + r["buy"]["purchase_costs"] * 0.9


def test_agency_commission_carries_vat():
    """The cap is 2%; the agent invoices VAT on top of it."""
    from backend.services import assumptions

    assert assumptions.agency_commission_with_vat_pct() > assumptions.AGENCY_COMMISSION_PCT
    assert assumptions.agency_commission_with_vat_pct() == round(
        assumptions.AGENCY_COMMISSION_PCT * (1 + assumptions.VAT_PCT / 100), 2
    )


def test_cash_flag_takes_costs_out_of_the_down_payment():
    """"This is all my money" must not silently gain the fees on top."""
    from backend.services.rent_vs_buy import compare_rent_vs_buy

    on_top = compare_rent_vs_buy(2_000_000, 30_000, 10, home_price=5_000_000)
    inclusive = compare_rent_vs_buy(
        2_000_000, 30_000, 10, home_price=5_000_000, down_payment_includes_costs=True,
    )

    assert on_top["buy"]["down_payment_applied"] == 2_000_000
    assert inclusive["buy"]["down_payment_applied"] == (
        2_000_000 - inclusive["buy"]["purchase_costs"]
    )
    # Both report the cash the user actually said they had
    assert inclusive["buy"]["cash_available"] == 2_000_000
    # Less money reaching the property means a bigger loan
    assert inclusive["buy"]["remaining_loan"] >= on_top["buy"]["remaining_loan"]


def test_cash_flag_never_makes_the_down_payment_negative():
    from backend.services.rent_vs_buy import compare_rent_vs_buy

    r = compare_rent_vs_buy(
        10_000, 30_000, 10, home_price=5_000_000, down_payment_includes_costs=True,
    )
    assert r["buy"]["down_payment_applied"] == 0
