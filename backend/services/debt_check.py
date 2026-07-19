"""
Debt before investing.

Paying off high-interest debt is a guaranteed return equal to its interest
rate. No portfolio offers a guaranteed return at all, let alone one that high.
So when a user carries credit-card debt, the honest answer is "clear this
first" — even though it means telling them not to use the rest of the app yet.

Nothing here is a judgement call by an LLM: it is the same compound-interest
arithmetic applied to both sides, and the user sees both numbers.
"""

from backend.services import assumptions

# PLANNING ASSUMPTION, not a quoted official figure. The TCMB revises the
# maximum monthly rate on TRY card balances periodically, so any constant here
# goes stale; this is a reasonable stand-in, shown to the user as an assumption
# and never presented as the current statutory rate. The conclusion is robust to
# it being somewhat off — the gap to portfolio returns is wide.
CARD_MONTHLY_RATE_PCT = 4.25

# Below this, the arithmetic still favours repayment but the amount is small
# enough that blocking someone's first investment does more harm than good.
MATERIAL_DEBT_TRY = 5_000.0


def annual_rate_from_monthly(monthly_pct: float) -> float:
    """Compounded annual cost of a monthly rate."""
    return round(((1 + monthly_pct / 100) ** 12 - 1) * 100, 1)


def check(
    debt: float | None,
    budget: float,
    card_monthly_rate_pct: float | None = None,
    portfolio_annual_growth_pct: float | None = None,
) -> dict | None:
    """
    Compare paying the debt against investing the same money for one year.

    Returns None when there is nothing to say — no debt, or an amount too small
    to be worth interrupting the user over.
    """
    if not debt or debt < MATERIAL_DEBT_TRY:
        return None

    if card_monthly_rate_pct is None:
        card_monthly_rate_pct = CARD_MONTHLY_RATE_PCT
    if portfolio_annual_growth_pct is None:
        portfolio_annual_growth_pct = assumptions.portfolio_growth_pct()

    debt_annual_pct = annual_rate_from_monthly(card_monthly_rate_pct)

    # Compare like with like: one year, on the amount the user could apply to
    # either side. Investing more than the debt leaves a genuine remainder.
    applied = min(debt, budget)
    interest_avoided = applied * debt_annual_pct / 100
    investment_gain = applied * portfolio_annual_growth_pct / 100
    advantage = interest_avoided - investment_gain

    # Covering the debt entirely still leaves something to start with.
    leftover = max(budget - debt, 0.0)

    return {
        "debt": round(debt, 2),
        "budget": round(budget, 2),
        "applied": round(applied, 2),
        "debt_annual_pct": debt_annual_pct,
        "portfolio_annual_pct": portfolio_annual_growth_pct,
        "interest_avoided": round(interest_avoided, 2),
        "investment_gain": round(investment_gain, 2),
        # How much better repayment is, over one year, in TRY.
        "advantage": round(advantage, 2),
        "leftover_after_repayment": round(leftover, 2),
        "covers_debt": budget >= debt,
        "assumptions": {
            "card_monthly_rate_pct": card_monthly_rate_pct,
            "annual_inflation_pct": assumptions.annual_inflation_pct(),
        },
    }
