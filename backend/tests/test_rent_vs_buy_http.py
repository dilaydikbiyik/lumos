"""
Rent-vs-buy over HTTP: user-supplied loan terms and the cost breakdown
both have to survive the router, not just the service.
"""


def test_rent_vs_buy_http_carries_costs(client):
    res = client.post("/planning/rent-vs-buy", json={
        "down_payment": 2000000, "monthly_rent": 30000,
        "years": 10, "home_price": 5000000,
    })
    assert res.status_code == 200, res.text
    b = res.json()["buy"]
    a = res.json()["assumptions"]
    assert b["purchase_costs"] > 0
    assert b["total_upkeep_paid"] > 0
    assert b["loan"]["interest_over_full_term"] > 0 if "loan" in b else True
    assert a["title_deed_fee_pct"] > 0 and a["annual_upkeep_pct"] > 0

def test_user_supplied_loan_terms_are_used(client):
    res = client.post("/planning/rent-vs-buy", json={
        "down_payment": 1000000, "monthly_rent": 25000, "years": 10,
        "home_price": 5000000, "mortgage_annual_rate_pct": 3.0,
        "mortgage_term_years": 10,
    })
    assert res.status_code == 200
    body = res.json()
    assert body["assumptions"]["mortgage_annual_rate_pct"] == 3.0
    assert body["loan"]["interest_over_full_term"] > 0
