"""
Split a budget between property, market assets and a cash reserve.

The entry point for the hybrid and undecided paths: "I have 1,000,000 — what
goes where?" A single-world path does not call this at all; the whole budget
is planned inside the world that reader chose, which is the point of having
chosen it.

Rule-based and explained, like `path_advisor` and `readiness_score`. Someone
being told to put six tenths of their savings into a flat deserves the
reasoning in terms they can push back on.

THE ORDER MATTERS, and it is not the order people expect:

  1. CASH RESERVE COMES FIRST, off the top. It is not an allocation competing
     with the others; it is the thing that stops a bad month turning into a
     forced sale at the worst price. Taking it out first is the difference
     between a plan and a wish.

  2. PROPERTY ONLY IF IT ACTUALLY CLEARS THE BAR. Below the market's entry
     threshold, physical property is not an option, and allocating "40% to
     real estate" on a budget that cannot buy any is advice that cannot be
     followed. The honest answer names REITs instead.

  3. WHAT IS LEFT goes to market assets, shaped by the risk score, which the
     portfolio engine already knows how to do.
"""

import logging
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger("lumos.budget_split")

# Months of outgoings to hold back before anything is invested. Six is the
# common counsel; three is the floor for someone with steady income, and this
# app's readers are mostly not in a position to hold more.
RESERVE_MONTHS = 6

# Never lock more than this share of everything into one illiquid asset,
# however much the numbers favour it. A plan that leaves someone unable to
# move for a decade is not a good plan, it is a well-argued trap.
MAX_PROPERTY_SHARE = 0.70

# Below this share of a home's price, a down payment is not realistic and the
# mortgage that would be needed is punitive.
MIN_PROPERTY_SHARE = 0.25


@dataclass(frozen=True)
class BudgetSplit:
    reserve: float
    property_amount: float
    market_amount: float
    property_vehicle: str          # physical | reit | none
    reasons: list[str] = field(default_factory=list)

    @property
    def total(self) -> float:
        return self.reserve + self.property_amount + self.market_amount

    def as_dict(self) -> dict:
        total = self.total or 1.0
        return {
            "reserve": round(self.reserve, 2),
            "property_amount": round(self.property_amount, 2),
            "market_amount": round(self.market_amount, 2),
            "property_vehicle": self.property_vehicle,
            "reserve_pct": round(self.reserve / total * 100, 1),
            "property_pct": round(self.property_amount / total * 100, 1),
            "market_pct": round(self.market_amount / total * 100, 1),
            "reasons": self.reasons,
        }


def split(*, budget: float,
          risk_score: Optional[float] = None,
          monthly_outgoings: Optional[float] = None,
          entry_threshold: Optional[float] = None,
          path: str = "hybrid") -> BudgetSplit:
    """
    Divide `budget` three ways, with the reasoning that produced it.

    `entry_threshold` is the market's realistic minimum for buying property
    and comes from the caller's pack — "enough to buy a flat" is a fact about
    a country, not a constant.
    """
    reasons: list[str] = []
    budget = max(float(budget or 0), 0.0)
    if budget <= 0:
        return BudgetSplit(0.0, 0.0, 0.0, "none", ["split.reason.no_budget"])

    # ── 1. The reserve, off the top ──────────────────────────────────────
    if monthly_outgoings and monthly_outgoings > 0:
        reserve = min(monthly_outgoings * RESERVE_MONTHS, budget * 0.5)
        reasons.append("split.reason.reserve_from_outgoings")
    else:
        # No figure to work from: a tenth is a placeholder, and saying so is
        # better than implying it was calculated.
        reserve = budget * 0.10
        reasons.append("split.reason.reserve_assumed")

    investable = budget - reserve

    # A single-world path plans everything inside the world that was chosen.
    if path == "stocks":
        reasons.append("split.reason.path_stocks")
        return BudgetSplit(reserve, 0.0, investable, "none", reasons)
    if path == "real_estate":
        reasons.append("split.reason.path_real_estate")
        vehicle = "physical" if entry_threshold and investable >= entry_threshold else "reit"
        if vehicle == "reit":
            reasons.append("split.reason.below_entry_reit")
        return BudgetSplit(reserve, investable, 0.0, vehicle, reasons)

    # ── 2. Can property actually be bought here? ─────────────────────────
    if not entry_threshold or investable < entry_threshold:
        # Allocating to something the reader cannot buy is advice that cannot
        # be followed. Name the instrument that works at this size instead.
        reasons.append("split.reason.below_entry_reit")
        reit_share = 0.15 if risk_score is None else min(0.25, 0.10 + risk_score / 100)
        property_amount = investable * reit_share
        return BudgetSplit(reserve, property_amount,
                           investable - property_amount, "reit", reasons)

    # ── 3. Both are genuinely open ───────────────────────────────────────
    # A lower risk score leans toward property: it moves less, it is not
    # watched daily, and it is the asset people find easiest to hold through
    # a bad year without selling. That behavioural fact is the point, not a
    # claim that property returns more.
    score = 5.0 if risk_score is None else max(0.0, min(10.0, float(risk_score)))
    property_share = MAX_PROPERTY_SHARE - (score / 10) * (MAX_PROPERTY_SHARE - MIN_PROPERTY_SHARE)
    property_amount = investable * property_share

    # Rounding down to something buyable: a property allocation that lands
    # just under the threshold buys nothing at all.
    if property_amount < entry_threshold:
        property_amount = entry_threshold
        reasons.append("split.reason.rounded_to_entry")
        if property_amount > investable * MAX_PROPERTY_SHARE:
            # Clearing the bar would mean over-committing. Don't.
            reasons.append("split.reason.entry_would_overcommit")
            reit_share = 0.20
            property_amount = investable * reit_share
            return BudgetSplit(reserve, property_amount,
                               investable - property_amount, "reit", reasons)

    reasons.append("split.reason.risk_shaped")
    return BudgetSplit(reserve, property_amount,
                       investable - property_amount, "physical", reasons)
