"""
Goal-based investing — "800.000 TL for a house deposit in 3 years" turned into
a concrete monthly contribution plan, with drift detection.
"""


def required_monthly_contribution(
    target_amount: float,
    years: float,
    current_savings: float = 0.0,
    annual_growth_pct: float = 15.0,
) -> dict:
    """
    Standard future-value-of-annuity solve: how much must be added each
    month, given existing savings grow at annual_growth_pct, to reach
    target_amount by the deadline.
    """
    months = max(round(years * 12), 1)
    monthly_rate = (1 + annual_growth_pct / 100) ** (1 / 12) - 1

    future_value_of_current = current_savings * (1 + monthly_rate) ** months

    remaining = target_amount - future_value_of_current
    if remaining <= 0:
        return {
            "monthly_contribution": 0.0,
            "already_on_track": True,
            "projected_shortfall_or_surplus": round(-remaining, 2),
        }

    if monthly_rate == 0:
        monthly_contribution = remaining / months
    else:
        # Future value of an ordinary annuity, solved for payment
        monthly_contribution = remaining * monthly_rate / ((1 + monthly_rate) ** months - 1)

    return {
        "monthly_contribution": round(monthly_contribution, 2),
        "already_on_track": False,
        "projected_shortfall_or_surplus": 0.0,
    }


def progress_and_drift(
    target_amount: float,
    years_remaining: float,
    current_savings: float,
    actual_monthly_contribution: float,
    annual_growth_pct: float = 15.0,
) -> dict:
    """
    Given what the user is ACTUALLY contributing, project whether they'll
    hit the goal on time, early, or late — "bu tempoda hedefin 8 ay gecikir".
    """
    months = max(round(years_remaining * 12), 1)
    monthly_rate = (1 + annual_growth_pct / 100) ** (1 / 12) - 1

    # Project forward with the user's real contribution rate
    balance = current_savings
    for _ in range(months):
        balance = balance * (1 + monthly_rate) + actual_monthly_contribution
    projected_at_deadline = balance

    progress_pct = round(min(current_savings / target_amount, 1.0) * 100, 1) if target_amount > 0 else 0.0

    delay_months = 0
    if projected_at_deadline < target_amount:
        # Keep simulating beyond the deadline until target is reached
        extra_months = 0
        balance = projected_at_deadline
        while balance < target_amount and extra_months < 600:  # 50-year safety cap
            balance = balance * (1 + monthly_rate) + actual_monthly_contribution
            extra_months += 1
        delay_months = extra_months

    return {
        "progress_pct": progress_pct,
        "projected_value_at_deadline": round(projected_at_deadline, 2),
        "on_track": projected_at_deadline >= target_amount,
        "delay_months": delay_months,
    }
