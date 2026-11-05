"""
Risk-blended portfolio engine — v4 (glide-path + defensive sleeve).

WHY v4 (2026-07-13): v3 blended every asset with an inverse-/direct-volatility
mix keyed on the risk score. Two realism gaps surfaced in an end-to-end audit:
  1. The universe had no cash/bond, so even the most conservative profile was
     ~100% equities+gold — irresponsible for a cautious/older/irregular-income
     beginner.
  2. The risk score barely moved the allocation (a risk-2 and a risk-9 portfolio
     looked almost identical).

v4 splits the portfolio into two sleeves whose SIZES are set by the risk score,
so the profile genuinely shapes the result:

    defensive_target = clamp(0.60 − 0.055·risk, 0, 0.60)   (→0 for aggressive)
    growth_target    = 1 − defensive_target

  • DEFENSIVE sleeve (cash + bonds): capital-preservation weight. Cash is the
    safest; bonds a low-volatility buffer. cash_share falls as risk rises.
  • GROWTH sleeve (equities + gold + REIT): the existing volatility blend
    (α = risk/10) decides the mix WITHIN this sleeve, then it's scaled to
    growth_target.

A per-position cap (MAX_POSITION_PCT) prevents any single asset from dominating
a small portfolio, and a small-weight floor removes dust. The result: defensive
weight decreases monotonically with the risk score, and every weight is still
explainable in one sentence.

Cash/bond are sized directly (not fetched), so compute_volatility is only ever
called on the real, fetchable growth tickers.

WHY v5 (2026-11-06): gold has a FIXED role in the growth sleeve. The blend's
premise for a bold profile is that a more volatile asset is a bigger growth
engine — reasonable for a company, whose swings come with earnings and
dividends that pay for the risk. Gold produces neither, so its volatility is
not a promise of growth, and treating it as one put a third of the most
aggressive American portfolio into gold. Gold now takes GOLD_GROWTH_SHARE of
the growth sleeve at every risk level, as a diversifier — it often holds up
while stocks fall, which is a real benefit and the reason it stays. Which
assets are SELECTED is unchanged; only gold's weight stopped following its
volatility.
"""

import json
from pathlib import Path

from backend.i18n import t as _t
from backend.schemas.portfolio import AssetAllocation, PortfolioRecommendResponse
from backend.services.hybrid_basket import get_reit_assets, should_include_reits
from backend.services.holdings_valuation import ticker_currency
from backend.services.volatility import compute_volatility

_ASSET_UNIVERSE_PATH = Path(__file__).parent.parent / "data" / "asset_universe.json"

MIN_WEIGHT_PCT = 5          # below this is "dust" — pruned and reported
MAX_POSITION_PCT = 45       # no single asset may exceed this (concentration guard)
# Gold's share of the growth sleeve, whatever the risk score. See "WHY v5".
GOLD_GROWTH_SHARE = 0.15
_BUDGET_POSITION_CAPS = [   # (budget upper bound, max positions)
    (75_000, 3),
    (200_000, 4),
    (float("inf"), 6),
]

# Defensive sleeve — sized by the glide path, but REAL fetchable tickers so
# every downstream feature (projection, time-machine, backtest, what-if) can
# pull their history. BIL = 1-3 month T-bills (cash-like), BND = total bond.
# The defensive names are translated at build time; the ticker is the identity.
_CASH_ASSET = {"ticker": "BIL", "name_key": "asset.cash.name", "category": "cash"}
_BOND_ASSET = {"ticker": "BND", "name_key": "asset.bond.name", "category": "bond"}


def _load_universe() -> list[dict]:
    with open(_ASSET_UNIVERSE_PATH) as f:
        return json.load(f)


def _pick_diversified(ranked: list[str], universe: list[dict], slots: int) -> list[str]:
    """
    One asset per category, best-ranked first. `slots` is a MAXIMUM, not a
    target: when the categories run out, the portfolio simply holds fewer
    positions.

    Ranking alone produced portfolios whose entire growth sleeve sat in two
    REIT ETFs tracking the same index — four slices on the chart, one real
    exposure underneath. Deferring the duplicate to the end of the list was
    not enough, because a budget large enough for six slots then pulled it
    back in: an aggressive profile ended up with VNQ and SCHH together, ~44%
    of the portfolio in what is effectively one holding. That is the exact
    thing the app tells users it avoids, and the reason text it shows for
    dropping an asset says so in as many words. So a second asset from an
    already-represented category is not filled in at all.
    """
    group_of = {a["ticker"]: _overlap_group(a) for a in universe}
    kept: list[str] = []
    used: set[str] = set()

    for ticker in ranked:                       # one per overlap group
        if len(kept) >= slots:
            break
        group = group_of.get(ticker)
        if group not in used:
            kept.append(ticker)
            used.add(group)

    return kept


def _overlap_group(asset: dict) -> str:
    """
    What a fund actually holds, for the one-per-exposure rule.

    The rule used to key on `category`, and "stocks" was too coarse to be the
    unit of overlap. Two funds on the same index ARE one exposure — VNQ and
    SCHH, SPY and QQQ, the S&P 500 and an MSCI World that is mostly the
    S&P 500 — and the rule is right to keep only one. But BIST 100 and the
    S&P 500 are different countries, currencies and companies, and they
    shared the "stocks" bucket, so a Turkish portfolio held SPY in every
    scenario measured and never a single Turkish company; an American one
    never held VXUS, the international fund already in its own universe;
    and the most aggressive Turkish profile put HALF its money in gold,
    because one stocks slot left the growth sleeve nothing else to fill
    with. Assets declare their `overlap`; anything that does not falls back
    to its category, so the REIT pair keeps working exactly as before.
    """
    return asset.get("overlap", asset["category"])


def _position_cap(budget: float) -> int:
    for limit, cap in _BUDGET_POSITION_CAPS:
        if budget < limit:
            return cap
    return _BUDGET_POSITION_CAPS[-1][1]


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def effective_position_cap(n_positions: int) -> float:
    """
    The concentration cap this many positions can actually honour.

    `n` positions summing to 1.0 cannot all sit below 1/n, so the published
    guard has to be at least that.
    """
    if n_positions <= 0:
        return MAX_POSITION_PCT / 100.0
    return max(MAX_POSITION_PCT / 100.0, 1.0 / n_positions)


def _apply_max_position(weights: dict[str, float],
                        defensive: set[str] | None = None,
                        fixed: set[str] | None = None) -> dict[str, float]:
    """
    Cap any position at MAX_POSITION_PCT, redistributing the excess
    proportionally onto the uncapped positions (iterated to convergence).

    THE EXCESS STAYS IN ITS OWN SLEEVE. Spilling it across every uncapped
    position let a capped growth holding push weight onto cash and bonds, so
    the defensive share drifted above the formula the allocation card prints
    and invites the reader to check — by nearly two points whenever the
    growth sleeve was small enough for one asset to hit the cap. The sleeve's
    size is decided by the risk score; a concentration guard on one equity is
    not a reason to make somebody more defensive than they asked to be.

    Only if a sleeve cannot absorb its own excess — every member already at
    the cap — does it fall back to the other one, because the weights must
    still sum to 1.0.

    `fixed` positions do not take excess either, for the same reason one
    level down. Gold's share of the growth sleeve is a stated rule; when the
    guard capped QQQ in the most aggressive American portfolio, the spill
    landed partly on gold and the card said "a fixed 15%" beside 16.4%.
    """
    defensive = defensive or set()
    fixed = fixed or set()
    w = dict(weights)
    # A cap of 45% is unreachable with two positions: they must still sum to
    # 1.0, so one of them is 55% whatever the guard says. Rather than publish
    # a limit the portfolio visibly breaks, the cap relaxes to the tightest
    # value the position count actually admits, and that is the number
    # reported back. An unenforceable published bound is worse than an
    # honestly wider one.
    cap = effective_position_cap(len(w))

    for _ in range(40):
        over = [t for t, x in w.items() if x > cap + 1e-9]
        if not over:
            break
        excess = sum(w[t] - cap for t in over)
        for t in over:
            w[t] = cap

        same_sleeve = {t in defensive for t in over}
        candidates = [t for t in w if w[t] < cap - 1e-9]
        if len(same_sleeve) == 1:
            sleeve = same_sleeve.pop()
            preferred = [t for t in candidates if (t in defensive) is sleeve]
            if preferred and sum(w[t] for t in preferred) > 0:
                candidates = preferred
        movable = [t for t in candidates if t not in fixed]
        if movable and sum(w[t] for t in movable) > 0:
            candidates = movable

        under_sum = sum(w[t] for t in candidates)
        if under_sum <= 0:
            break
        for t in candidates:
            w[t] += excess * (w[t] / under_sum)
    return w


def _role(category: str, lang: str) -> str:
    """Category → its role in the portfolio (core of the per-asset rationale)."""
    key = f"role.{category}"
    return _t(key, lang) if key in _ROLE_KEYS else _t("role.default", lang)


_ROLE_KEYS = {"role.stocks", "role.gold", "role.reit", "role.bond", "role.cash", "role.fund"}


def _growth_rationale(category: str, vol: float, weight: float, alpha: float, lang: str) -> str:
    vol_pct = round(vol * 100)
    if alpha < 0.45:
        tilt_key = "weight.tilt.cautious"
    elif alpha > 0.7:
        tilt_key = "weight.tilt.bold"
    else:
        tilt_key = "weight.tilt.balanced"
    return _t("weight.growth", lang,
              role=_role(category, lang),
              tilt=_t(tilt_key, lang, vol=vol_pct),
              pct=round(weight * 100, 1))


def _defensive_rationale(category: str, weight: float, defensive_target: float, lang: str) -> str:
    return _t("weight.defensive", lang,
              role=_role(category, lang),
              defensive=round(defensive_target * 100),
              pct=round(weight * 100, 1))


def build_portfolio(risk_score: float, budget: float, market: str = "TR",
                    lang: str = "tr") -> PortfolioRecommendResponse:
    """
    Compute a glide-path portfolio: a risk-sized defensive sleeve (cash + bonds)
    plus a volatility-blended growth sleeve (equities + gold + REIT).

    Args:
        risk_score: 1-10 score from the risk engine
        budget:     Investment budget in the market's own currency

    Returns:
        PortfolioRecommendResponse with per-asset weights, per-asset rationale,
        and fully transparent allocation logic in metadata.
    """
    include_reits = should_include_reits(budget, market)
    # The investable universe is a legal fact, not a preference: EU retail
    # investors cannot buy US-domiciled ETFs (no PRIIPs Key Information
    # Document), so a market that defines its own universe always wins over
    # the shared default. Recommending SPY to a German user would name
    # something their broker must refuse.
    from backend.markets import get_market_pack

    pack = get_market_pack(market)
    growth_universe = list(pack.asset_universe) or _load_universe()
    if include_reits:
        growth_universe = growth_universe + (list(pack.reit_assets) or get_reit_assets())

    # The defensive sleeve is bound by the same rule — BIL and BND are
    # US-domiciled, so a German portfolio cannot hold them either.
    cash_asset = pack.cash_asset or _CASH_ASSET
    bond_asset = pack.bond_asset or _BOND_ASSET

    # Fetch volatility ONLY for the real, fetchable growth tickers
    growth_tickers = [a["ticker"] for a in growth_universe]
    volatilities = compute_volatility(growth_tickers)

    alpha = _clamp(risk_score / 10.0, 0.1, 1.0)

    # ── Sleeve sizing (glide path) — the risk score sets the split ──
    defensive_target = _clamp(0.60 - 0.055 * risk_score, 0.0, 0.60)
    if defensive_target < 0.10:            # aggressive: a clean, cash-free growth mix
        defensive_target = 0.0
    growth_target = 1.0 - defensive_target
    cash_share = _clamp(0.75 - 0.05 * risk_score, 0.30, 0.75)

    # How many SLOTS the budget supports — distinct from the per-position
    # WEIGHT cap below, which used to reuse this same name.
    slot_cap = _position_cap(budget)
    n_defensive = 0 if defensive_target == 0 else min(2, max(slot_cap - 2, 1))
    growth_slots = max(slot_cap - n_defensive, 1)

    # ── Growth sleeve: volatility blend, keep the top `growth_slots` ──
    raw: dict[str, float] = {}
    for asset in growth_universe:
        t = asset["ticker"]
        vol = max(volatilities.get(t, 0.15), 0.01)
        raw[t] = (1 - alpha) * (1.0 / vol) + alpha * vol
    total_raw = sum(raw.values())
    growth_w = {t: v / total_raw for t, v in raw.items()}

    ranked = sorted(growth_w, key=growth_w.get, reverse=True)
    is_gold = {a["ticker"] for a in growth_universe if a["category"] == "gold"}
    if growth_slots == 1:
        # A diversifier needs something to diversify. With room for one
        # growth asset, a fixed 15% role would become the whole sleeve.
        ranked = [t for t in ranked if t not in is_gold] or ranked
    kept = _pick_diversified(ranked, growth_universe, growth_slots)

    category_of = {a["ticker"]: a["category"] for a in growth_universe}
    group_of = {a["ticker"]: _overlap_group(a) for a in growth_universe}
    kept_groups = {group_of[t] for t in kept}
    dropped: list[dict] = []
    for t in growth_w:
        if t not in kept:
            # Two funds tracking the same market are one exposure wearing two
            # names. Say which, so a dropped-but-higher-ranked asset doesn't
            # look arbitrary.
            # Keyed on the overlap group, like the picker: a fund dropped
            # only for lack of slots must not be told it duplicated another.
            if group_of[t] in kept_groups:
                reason = _t("drop.same_category", lang,
                           category=_t(f"category.{category_of[t]}", lang))
            else:
                reason = _t("drop.position_cap", lang, cap=slot_cap,
                           budget=f"{budget:,.0f} {pack.currency_symbol}")
            dropped.append({
                "ticker": t,
                "weight_pct": round(growth_w[t] * 100, 1),
                "reason": reason,
            })
    growth_w = {t: growth_w[t] for t in kept}
    gold_kept = [t for t in kept if t in is_gold]
    others = [t for t in kept if t not in is_gold]
    if gold_kept and others:
        # Gold's share is fixed; the volatility blend divides the rest.
        osum = sum(growth_w[t] for t in others) or 1.0
        shares = {t: growth_w[t] / osum * (1 - GOLD_GROWTH_SHARE) for t in others}
        shares.update({t: GOLD_GROWTH_SHARE / len(gold_kept) for t in gold_kept})
    else:
        gsum = sum(growth_w.values()) or 1.0
        shares = {t: v / gsum for t, v in growth_w.items()}
    weights = {t: share * growth_target for t, share in shares.items()}

    # ── Defensive sleeve: sized directly, split cash/bond by risk ──
    defensive_categories: dict[str, str] = {}
    if n_defensive == 1:
        weights[cash_asset["ticker"]] = defensive_target
        defensive_categories[cash_asset["ticker"]] = "cash"
    elif n_defensive == 2:
        weights[cash_asset["ticker"]] = defensive_target * cash_share
        weights[bond_asset["ticker"]] = defensive_target * (1 - cash_share)
        defensive_categories[cash_asset["ticker"]] = "cash"
        defensive_categories[bond_asset["ticker"]] = "bond"

    # ── Dust floor first, then the concentration guard as the LAST step so no
    #    position can exceed the cap after the final re-normalisation ──
    min_w = MIN_WEIGHT_PCT / 100.0

    # A dust-sized CASH or BOND position is still part of a sleeve whose size
    # the risk score decided. Dropping it and renormalising everything spread
    # that weight across the growth assets, so a profile told "31% stays on
    # the safe side" quietly received 9% — the published number and the real
    # portfolio disagreed. The weight moves to the surviving defensive
    # position instead; only if BOTH are dust does the sleeve really vanish.
    defensive_tickers = [t for t in defensive_categories if t in weights]
    defensive_dust = [t for t in defensive_tickers if weights[t] < min_w]
    survivors = [t for t in defensive_tickers if weights[t] >= min_w]
    if defensive_dust and survivors:
        rescued = sum(weights.pop(t) for t in defensive_dust)
        for t in survivors:
            weights[t] += rescued / len(survivors)

    dust = [t for t, w in weights.items() if w < min_w]
    for t in dust:
        dropped.append({
            "ticker": t,
            "weight_pct": round(weights[t] * 100, 1),
            "reason": _t("drop.crumb", lang, min=MIN_WEIGHT_PCT),
        })
        weights.pop(t)

    total = sum(weights.values()) or 1.0
    weights = {t: w / total for t, w in weights.items()}
    # sum-preserving; final cap wins, and the excess stays in its own sleeve
    weights = _apply_max_position(weights, set(defensive_categories),
                                  fixed=set(gold_kept) if others else set())

    # ── Assemble allocations with per-asset rationale ──
    by_ticker = {a["ticker"]: a for a in growth_universe}
    by_ticker[cash_asset["ticker"]] = cash_asset
    by_ticker[bond_asset["ticker"]] = bond_asset

    allocations = []
    for t, weight in sorted(weights.items(), key=lambda kv: -kv[1]):
        asset = by_ticker[t]
        category = asset.get("category", "other")
        if t in defensive_categories:
            explanation = _defensive_rationale(category, weight, defensive_target, lang)
        elif category == "gold" and t in is_gold and len(kept) > 1:
            # The stated rule, or an honest note of why it does not hold here.
            # With three positions under a 45% cap, two capped positions
            # leave the third whatever is left; a small portfolio can force
            # gold off its share, and the card must then say so rather than
            # print "a fixed 15%" beside another number.
            growth_total = sum(w for tk, w in weights.items()
                               if tk not in defensive_categories) or 1.0
            actual = weight / growth_total
            key = ("weight.gold_diversifier"
                   if abs(actual - GOLD_GROWTH_SHARE) < 0.005
                   else "weight.gold_diversifier_capped")
            explanation = _t(key, lang,
                             role=_role(category, lang),
                             share=round(GOLD_GROWTH_SHARE * 100),
                             actual=round(actual * 100),
                             pct=round(weight * 100, 1))
        else:
            vol = volatilities.get(t, 0.15)
            explanation = _growth_rationale(category, vol, weight, alpha, lang)
        allocations.append(
            AssetAllocation(
                ticker=t,
                name=(_t(asset["name_key"], lang) if "name_key" in asset
                      else asset.get("name", t)),
                weight=round(weight, 4),
                category=category,
                explanation=explanation,
                # Resolved offline from the symbol, so the client can tell a
                # reader whether this holding carries currency risk for them.
                currency=ticker_currency(t),
            )
        )

    # The rounding remainder has to land somewhere for the weights to sum to
    # exactly 1.0 — but not on a position already at the cap, which is how a
    # portfolio ended up publishing "max 45%" next to a 45.01% holding.
    # Named apart from the POSITION-COUNT cap above, which it used to shadow:
    # `position_cap` in the metadata below was reading this 0.45 rather than
    # the number of slots it is documented to report.
    weight_cap = effective_position_cap(len(allocations))
    rounding_gap = round(1.0 - sum(a.weight for a in allocations), 4)
    if allocations and abs(rounding_gap) > 0:
        target = next(
            (a for a in allocations if a.weight + rounding_gap <= weight_cap + 1e-9),
            allocations[-1],   # everything is at the cap: the smallest absorbs it
        )
        target.weight = round(target.weight + rounding_gap, 4)

    return PortfolioRecommendResponse(
        risk_score=risk_score,
        budget=budget,
        allocations=allocations,
        plain_explanation="",  # filled by explainer service
        includes_reits=include_reits and any(a.category == "reit" for a in allocations),
        formula_used="glide-path-defensive-sleeve-v5",
        metadata={
            "volatilities": {k: round(v, 4) for k, v in volatilities.items()},
            "allocation_logic": {
                "alpha": round(alpha, 2),
                "defensive_target_pct": round(defensive_target * 100, 1),
                "growth_target_pct": round(growth_target * 100, 1),
                "formula": _t("formula.allocation", lang),
                "position_cap": slot_cap,
                "max_position_pct": round(weight_cap * 100, 1),
                "min_weight_pct": MIN_WEIGHT_PCT,
                "dropped": dropped,
            },
        },
    )
