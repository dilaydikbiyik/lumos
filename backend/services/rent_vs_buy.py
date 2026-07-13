"""
Rent or buy? — Turkey's most common first financial question, answered
honestly with a CONSISTENT, apples-to-apples comparison.

The old model was misleading: it treated the down payment as if it were the
whole property, so "100.000 TL peşinat" looked like you bought a 100k house —
even when your rent was 50.000 TL/month (a house that rents for that is worth
millions, not 100k). Buy and rent described two different homes.

This version compares the SAME home under two strategies, with an EQUAL
monthly housing budget (the only fair basis):

  • home_price is the real property value. If the user doesn't know it, we
    estimate it from the rent using a realistic gross rental yield (annual
    rent / yield) and surface that assumption openly.
  • BUY: pay the down payment now, finance the rest with a mortgage. Each
    month pay the mortgage installment; the home appreciates with the housing
    index; equity = home value − remaining loan.
  • RENT: keep the down payment invested (portfolio growth); pay rent monthly.
  • EQUAL OUTFLOW: both sides spend the same amount on housing each month
    (max of mortgage vs rent). Whoever pays less that month invests the
    difference. This is what makes the two net-worth figures comparable.

Still deliberately simple: fixed nominal rates, no taxes, no maintenance/
aidat, no transaction costs. A comparison tool, not a promise of precision.
"""

from backend.services import assumptions

# Gross rental yield used to back out a home price when the user doesn't give
# one: annual_rent / yield. ~5% is realistic for large Turkish cities.
DEFAULT_GROSS_RENTAL_YIELD = 0.05


def _mortgage_payment(loan: float, monthly_rate: float, term_months: int) -> float:
    """Fixed monthly installment for an amortizing loan (annuity formula)."""
    if loan <= 0:
        return 0.0
    if monthly_rate == 0:
        return loan / term_months
    return loan * monthly_rate / (1 - (1 + monthly_rate) ** -term_months)


def compare_rent_vs_buy(
    down_payment: float,
    monthly_rent: float,
    years: int,
    home_price: float | None = None,
    housing_annual_growth_pct: float | None = None,
    portfolio_annual_growth_pct: float | None = None,
    rent_annual_growth_pct: float | None = None,
    mortgage_annual_rate_pct: float | None = None,
    mortgage_term_years: int | None = None,
) -> dict:
    """
    Compare buying vs renting the SAME home over `years`, with an equal
    monthly housing budget. Returns both strategies' projected net worth plus
    the assumptions used (so nothing is hidden).

    Rate arguments default to the LIVE, market-linked planning assumptions
    (inflation from TCMB, housing/portfolio as real spreads over it); pass an
    explicit value to override any of them.
    """
    # 0) Resolve live market-linked assumptions (overridable) ------------------
    if housing_annual_growth_pct is None:
        housing_annual_growth_pct = assumptions.housing_growth_pct()
    if portfolio_annual_growth_pct is None:
        portfolio_annual_growth_pct = assumptions.portfolio_growth_pct()
    if rent_annual_growth_pct is None:
        rent_annual_growth_pct = assumptions.rent_growth_pct()
    if mortgage_annual_rate_pct is None:
        mortgage_annual_rate_pct = assumptions.mortgage_rate_pct()
    if mortgage_term_years is None:
        mortgage_term_years = assumptions.mortgage_term_years()

    # 1) Establish a consistent home price -------------------------------------
    estimated = False
    if not home_price or home_price <= 0:
        # Back out from rent so the two scenarios describe the same property
        home_price = (monthly_rent * 12) / DEFAULT_GROSS_RENTAL_YIELD
        estimated = True
    # A down payment can't exceed the home's value
    down_payment = min(down_payment, home_price)

    months = years * 12
    term_months = mortgage_term_years * 12
    portfolio_m = (1 + portfolio_annual_growth_pct / 100) ** (1 / 12) - 1
    mortgage_m = mortgage_annual_rate_pct / 100 / 12

    loan = max(home_price - down_payment, 0.0)
    installment = _mortgage_payment(loan, mortgage_m, term_months)

    # 2) Month-by-month simulation ---------------------------------------------
    loan_balance = loan
    buy_side_portfolio = 0.0     # what the buyer invests when rent > mortgage
    rent_portfolio = down_payment  # renter keeps the down payment invested
    rent = monthly_rent
    total_rent_paid = 0.0
    total_mortgage_paid = 0.0

    for m in range(months):
        # Equal housing budget this month — both sides "spend" the same
        mortgage_due = installment if loan_balance > 1e-6 else 0.0
        budget = max(mortgage_due, rent)

        # BUY: pay the mortgage, invest whatever is left of the shared budget
        if loan_balance > 1e-6:
            interest = loan_balance * mortgage_m
            principal = min(installment - interest, loan_balance)
            loan_balance = max(loan_balance - principal, 0.0)
            total_mortgage_paid += installment
        buy_side_portfolio = buy_side_portfolio * (1 + portfolio_m) + (budget - mortgage_due)

        # RENT: pay the rent, invest the rest; the down payment keeps compounding
        rent_portfolio = rent_portfolio * (1 + portfolio_m) + (budget - rent)
        total_rent_paid += rent

        # Rent resets once a year
        if (m + 1) % 12 == 0:
            rent *= 1 + rent_annual_growth_pct / 100

    # 3) Net worth at the horizon ----------------------------------------------
    home_value = home_price * (1 + housing_annual_growth_pct / 100) ** years
    buy_equity = home_value - loan_balance
    buy_net = buy_equity + buy_side_portfolio
    rent_net = rent_portfolio

    # Real (inflation-adjusted) net worth — the nominal figures above are big
    # mostly because of inflation; these say what they're worth in today's money.
    inflation_pct = assumptions.annual_inflation_pct()
    buy_net_real = assumptions.real_value(buy_net, years, inflation_pct)
    rent_net_real = assumptions.real_value(rent_net, years, inflation_pct)

    return {
        "years": years,
        "home_price": round(home_price, 2),
        "home_price_estimated": estimated,
        "monthly_mortgage": round(installment, 2),
        "buy": {
            "home_value": round(home_value, 2),
            "remaining_loan": round(loan_balance, 2),
            "equity": round(buy_equity, 2),
            "side_investments": round(buy_side_portfolio, 2),
            "total_mortgage_paid": round(total_mortgage_paid, 2),
            "net_worth": round(buy_net, 2),
            "net_worth_real": round(buy_net_real, 2),
        },
        "rent": {
            "portfolio_value": round(rent_portfolio, 2),
            "total_rent_paid": round(total_rent_paid, 2),
            "net_worth": round(rent_net, 2),
            "net_worth_real": round(rent_net_real, 2),
        },
        "verdict": "buy" if buy_net >= rent_net else "rent",
        "difference": round(abs(buy_net - rent_net), 2),
        "difference_real": round(abs(buy_net_real - rent_net_real), 2),
        "assumptions": {
            "housing_annual_growth_pct": housing_annual_growth_pct,
            "portfolio_annual_growth_pct": portfolio_annual_growth_pct,
            "rent_annual_growth_pct": rent_annual_growth_pct,
            "mortgage_annual_rate_pct": mortgage_annual_rate_pct,
            "mortgage_term_years": mortgage_term_years,
            "gross_rental_yield_pct": round(DEFAULT_GROSS_RENTAL_YIELD * 100, 1),
            "annual_inflation_pct": inflation_pct,
        },
    }
