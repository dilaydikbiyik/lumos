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
    down_payment_includes_costs: bool = False,
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

    # Purchase costs are paid out of pocket at closing, on top of the price.
    # Leaving them out silently flatters buying, which is the default bias we
    # are trying to correct — so the buyer's side starts this much behind.
    purchase_costs = home_price * (
        assumptions.TITLE_DEED_FEE_PCT + assumptions.agency_commission_with_vat_pct()
    ) / 100

    # People think in "the money I have", not "the down payment after fees".
    # When they say the figure is all their cash, the fees come out of it —
    # which is exactly the surprise that derails first-time buyers.
    cash_available = down_payment
    if down_payment_includes_costs:
        down_payment = max(down_payment - purchase_costs, 0.0)

    # The renter did not spend that money, so they keep it invested. Either way
    # both sides start from the same total outlay.
    rent_portfolio_start = down_payment + purchase_costs

    loan = max(home_price - down_payment, 0.0)
    installment = _mortgage_payment(loan, mortgage_m, term_months)

    # Dues, insurance and upkeep fall on the owner every month, whatever the
    # market does. Charged on the home's current (appreciating) value.
    upkeep_m = assumptions.ANNUAL_UPKEEP_PCT / 100 / 12
    housing_m = (1 + housing_annual_growth_pct / 100) ** (1 / 12) - 1

    # 2) Month-by-month simulation ---------------------------------------------
    loan_balance = loan
    buy_side_portfolio = 0.0     # what the buyer invests when rent > mortgage
    rent_portfolio = rent_portfolio_start  # down payment + the costs never paid
    rent = monthly_rent
    total_rent_paid = 0.0
    total_mortgage_paid = 0.0
    total_interest_paid = 0.0   # the true cost of borrowing, separate from principal
    total_upkeep_paid = 0.0
    running_home_value = home_price

    for m in range(months):
        # Upkeep tracks the home's value, so it grows along with it
        upkeep_due = running_home_value * upkeep_m

        # Equal housing budget this month — both sides "spend" the same. The
        # owner's outgoings include upkeep, so the shared budget must cover it;
        # otherwise the renter would be handed a smaller budget for free.
        mortgage_due = installment if loan_balance > 1e-6 else 0.0
        budget = max(mortgage_due + upkeep_due, rent)

        # BUY: pay the mortgage and the upkeep, invest what's left
        if loan_balance > 1e-6:
            interest = loan_balance * mortgage_m
            principal = min(installment - interest, loan_balance)
            loan_balance = max(loan_balance - principal, 0.0)
            total_mortgage_paid += installment
            total_interest_paid += interest
        total_upkeep_paid += upkeep_due
        buy_side_portfolio = (
            buy_side_portfolio * (1 + portfolio_m) + (budget - mortgage_due - upkeep_due)
        )

        # RENT: pay the rent, invest the rest; the down payment keeps compounding
        rent_portfolio = rent_portfolio * (1 + portfolio_m) + (budget - rent)
        total_rent_paid += rent

        running_home_value *= 1 + housing_m

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
        # What the loan itself costs. `over_full_term` runs to the end of the
        # mortgage, not the scenario horizon — that's the number that answers
        # "is this many years at this rate worth it?".
        "loan": {
            "principal": round(loan, 2),
            "interest_over_full_term": round(installment * term_months - loan, 2),
            "total_over_full_term": round(installment * term_months, 2),
            "interest_paid_by_horizon": round(total_interest_paid, 2),
        },
        "buy": {
            "home_value": round(home_value, 2),
            "remaining_loan": round(loan_balance, 2),
            "equity": round(buy_equity, 2),
            "side_investments": round(buy_side_portfolio, 2),
            "total_mortgage_paid": round(total_mortgage_paid, 2),
            "purchase_costs": round(purchase_costs, 2),
            # What actually reached the property after fees, and the cash it came
            # from — the gap is the number people don't budget for.
            "down_payment_applied": round(down_payment, 2),
            "cash_available": round(cash_available, 2),
            "total_upkeep_paid": round(total_upkeep_paid, 2),
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
            "title_deed_fee_pct": assumptions.TITLE_DEED_FEE_PCT,
            "agency_commission_pct": assumptions.AGENCY_COMMISSION_PCT,
            "vat_pct": assumptions.VAT_PCT,
            "agency_commission_with_vat_pct": assumptions.agency_commission_with_vat_pct(),
            "annual_upkeep_pct": assumptions.ANNUAL_UPKEEP_PCT,
            "annual_inflation_pct": inflation_pct,
        },
    }
