"""
The portfolio for a reader's chosen investment path.

The engine used to build every portfolio on the whole budget and decide
about property funds by budget alone, whatever path the reader had chosen:

  * a "stocks only" reader was handed a property fund anyway;
  * a hybrid reader saw the budget split (reserve + property + markets) and,
    beside it, a portfolio built on 100% of the same budget that held a
    property fund and a cash sleeve of its own — property and cash counted
    twice. A German hybrid reader with EUR 20,000 ended up ~21% in property.

So the path decides:

  * stocks — the market part of the budget split (the budget less the
    emergency reserve), no property funds. It was the whole budget, while
    the budget-plan card on the same dashboard told the same reader to set
    half of it aside first: two plans for one sum;
  * hybrid / undecided — the portfolio is the MARKET part of the budget
    split: built on `market_amount`, with no property fund, because the
    split's property part (a home, or a REIT when a home is out of reach)
    already is the property exposure;
  * real_estate — the portfolio page is not offered on this path; the
    engine's budget rule stands for any caller that asks anyway.

Every caller that builds "this reader's portfolio" — the recommendation, the
drift target, the what-if — goes through here, so they cannot disagree.
"""
from typing import Optional

from backend.markets import get_market_pack
from backend.services import budget_split
from backend.services.portfolio_engine import build_portfolio

SPLIT_PATHS = {"stocks", "hybrid", "undecided"}


def build_for_path(path: Optional[str], risk_score: float, budget: float, market: str,
                   lang: str, *, monthly_outgoings: Optional[float] = None,
                   committed_property: float = 0.0):
    """(portfolio, plan) — `plan` is the split the portfolio is the market
    part of, or None when the whole budget is the portfolio."""
    path = path or "hybrid"
    if path not in SPLIT_PATHS:
        return build_portfolio(risk_score, budget, market, lang), None

    pack = get_market_pack(market)
    split = budget_split.split(
        budget=budget, risk_score=risk_score, monthly_outgoings=monthly_outgoings,
        entry_threshold=pack.property_entry_threshold,
        committed_property=committed_property, path=path,
    )
    amount = split.market_amount if split.market_amount > 0 else budget
    portfolio = build_portfolio(risk_score, amount, market, lang, include_reits=False)
    plan = {
        "path": path,
        "total_budget": round(budget, 2),
        "reserve": round(split.reserve, 2),
        "property_amount": round(split.property_amount, 2),
        "property_vehicle": split.property_vehicle,
        "market_amount": round(amount, 2),
    }
    portfolio.metadata["plan"] = plan
    return portfolio, plan


async def committed_property(db, user) -> float:
    """What the reader already holds in property — the split plans around it."""
    from backend.repositories import holding_repository
    from backend.services.holdings_valuation import REAL_ESTATE_TYPES

    holdings = await holding_repository.list_for_user(db, user.id)
    return sum((h.manual_current_value or h.purchase_amount or 0)
               for h in holdings if h.asset_type in REAL_ESTATE_TYPES)


def plan_targets(portfolio, plan, market: str | None = None, holdings=None) -> list[dict]:
    """
    The plan as target weights, for comparing with everything the reader owns.

    Only the parts of the plan the reader actually RECORDS are targets.
    "I bought it" records the market portfolio and nothing else — the reserve
    usually stays in a bank account nobody types in, and the property part
    may not be bought yet. Making them targets anyway told every reader who
    had just followed the recommendation exactly that they had drifted
    (stocks path: cash 10% against 19%; hybrid: "serious"). So:

      * the reserve is a cash target only if the reader holds cash outside
        the portfolio's own funds;
      * the property part is a property target only if they hold property —
        a home, land, or a property fund;
      * the market part always is, and the targets are rescaled to sum to 1.

    A hybrid reader who records the whole plan (reserve, home, portfolio) is
    still compared with the whole plan, which is the case this was built for.
    """
    allocations = [{"category": a.category, "ticker": a.ticker, "weight": a.weight}
                   for a in portfolio.allocations]
    portfolio_tickers = {a["ticker"] for a in allocations}
    # Every fund this market knows, at weight zero, so a holding is filed by
    # what it IS. A reader who bought the plan's property part as a REIT fund
    # had it counted as "stocks" (its type is ETF and it is not in the
    # portfolio), and was told property was 0% against a target of 8%.
    reit_tickers: set[str] = set()
    if market:
        from backend.markets import get_market_pack

        pack = get_market_pack(market)
        reit_tickers = {a["ticker"] for a in pack.reit_assets}
        allocations += [{"category": a["category"], "ticker": a["ticker"], "weight": 0.0}
                        for a in [*pack.asset_universe, *pack.reit_assets]
                        if a["ticker"] not in portfolio_tickers]
    if not plan or not plan.get("total_budget"):
        return allocations

    holdings = list(holdings or [])
    def ticker(h):
        return (getattr(h, "ticker", None) or "").upper()
    holds_reserve = any(h.asset_type == "cash" and ticker(h) not in portfolio_tickers
                        for h in holdings)
    holds_property = any(h.asset_type in ("real_estate", "land") or ticker(h) in reit_tickers
                         for h in holdings)

    parts = [(plan["market_amount"], None)]
    if plan["reserve"] > 0 and holds_reserve:
        parts.append((plan["reserve"], "cash"))
    if plan["property_amount"] > 0 and holds_property:
        parts.append((plan["property_amount"], "reit"))
    total = sum(amount for amount, _ in parts) or 1.0
    market_share = plan["market_amount"] / total
    out = [{**a, "weight": a["weight"] * market_share} for a in allocations]
    for amount, category in parts[1:]:
        out.append({"category": category, "ticker": "", "weight": amount / total})
    return out
