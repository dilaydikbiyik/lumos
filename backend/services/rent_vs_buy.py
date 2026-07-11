"""
Rent or buy? — Turkey's most common first financial
question, answered honestly: two side-by-side scenarios, not a verdict.

Scenario A (buy): down payment is locked into the property; it grows
with the housing index but pays no rent.
Scenario B (rent): down payment stays invested (portfolio growth rate);
rent is paid out of pocket every month.

Deliberately conservative: no mortgage amortization schedule (too many
bank-specific variables), no tax modeling — a comparison tool, not a
calculator that pretends to be exact.
"""


def compare_rent_vs_buy(
    down_payment: float,
    monthly_rent: float,
    years: int,
    housing_annual_growth_pct: float = 20.0,
    portfolio_annual_growth_pct: float = 15.0,
) -> dict:
    """
    Args:
        down_payment: cash available now (buy scenario locks it into property)
        monthly_rent: current rent if the user stays a tenant
        years: projection horizon
        housing_annual_growth_pct: assumed nominal housing appreciation
        portfolio_annual_growth_pct: assumed nominal invested-portfolio growth

    Returns dict with both scenarios' projected net worth at year `years`.
    """
    months = years * 12

    # Scenario A: buy — down payment becomes property equity, no rent paid
    buy_value = down_payment * (1 + housing_annual_growth_pct / 100) ** years
    buy_rent_paid = 0.0

    # Scenario B: rent — down payment stays invested, rent paid monthly
    rent_portfolio_value = down_payment * (1 + portfolio_annual_growth_pct / 100) ** years
    # Rent assumed to rise with housing growth (proxy for local inflation)
    total_rent_paid = 0.0
    rent = monthly_rent
    for m in range(months):
        total_rent_paid += rent
        if (m + 1) % 12 == 0:
            rent *= 1 + housing_annual_growth_pct / 100

    return {
        "years": years,
        "buy": {
            "property_value": round(buy_value, 2),
            "total_rent_paid": buy_rent_paid,
            "net_position": round(buy_value, 2),
        },
        "rent": {
            "portfolio_value": round(rent_portfolio_value, 2),
            "total_rent_paid": round(total_rent_paid, 2),
            "net_position": round(rent_portfolio_value - total_rent_paid, 2),
        },
        "assumptions": {
            "housing_annual_growth_pct": housing_annual_growth_pct,
            "portfolio_annual_growth_pct": portfolio_annual_growth_pct,
        },
    }
