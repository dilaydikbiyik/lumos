"""
"A 500,000 plot, or a 500,000 portfolio?"

The question the hybrid path exists to answer, and the one a beginner cannot
answer alone: the two worlds are quoted in different units, reported over
different periods, and discussed by people with opposite incentives.

Deliberately BACKWARD-LOOKING. Both sides are what actually happened to the
same amount over the same window — the region's own price index against a
real portfolio backtest. No projections on either side: a forecast comparison
would be two guesses dressed as an answer, and the side with the friendlier
assumptions would always win.

Three honesty rules, because this is the screen most able to mislead:

  1. SAME WINDOW OR NO COMPARISON. If the region's index does not cover the
     period the portfolio was tested over, the answer is "cannot compare",
     not a number from a shorter window quietly set beside a longer one.

  2. REAL TERMS ON BOTH SIDES, deflated by the same inflation series. In a
     high-inflation market nominal figures make both sides look like wins.

  3. THE COSTS THAT ONLY ONE SIDE PAYS. Property carries transfer tax,
     agency commission and yearly upkeep; a portfolio does not. Leaving them
     out is how property wins an argument it might not deserve.
"""

import logging
from typing import Optional

from backend.i18n import t
from backend.services import assumptions

logger = logging.getLogger("lumos.property_vs_portfolio")

_PERIOD_YEARS = {"1y": 1, "3y": 3, "5y": 5}


def _region_growth_pct(code: str, years: int, market: str,
                       lang: str) -> Optional[tuple[float, int]]:
    """
    (total % change, years actually covered) for a region's price index.

    Returns None when the area is unknown. The covered span is returned
    rather than assumed: an index that only reaches back three years cannot
    answer a five-year question, and pretending otherwise is the whole
    failure this module is trying to avoid.
    """
    from backend.services.province_intelligence import _area_source, _PERIODS_PER_YEAR

    source = _area_source(market)
    if source is None:
        return None
    read = source(lang)
    entry = read["areas"].get(code.upper()) or read["areas"].get(code)
    if not entry:
        return None

    periods = sorted(entry["series"])
    per_year = _PERIODS_PER_YEAR[read["frequency"]]
    wanted = years * per_year
    if len(periods) < 2:
        return None

    step = min(wanted, len(periods) - 1)
    start, end = entry["series"][periods[-1 - step]], entry["series"][periods[-1]]
    if not start:
        return None
    return round((end / start - 1) * 100, 2), round(step / per_year, 2)


def compare(*, amount: float, region_code: str, weights: dict[str, float],
            period: str = "5y", market: str = "TR", lang: str = "tr") -> dict:
    """
    The same amount, the same window, both worlds — as it actually went.
    """
    years = _PERIOD_YEARS.get(period, 5)
    market = (market or "TR").upper()
    pack_costs = {
        "transfer_tax_pct": assumptions.transfer_tax_pct(market),
        "agency_pct": assumptions.agency_commission_with_vat_pct(market),
        "annual_upkeep_pct": assumptions.annual_upkeep_pct(market),
    }

    region = _region_growth_pct(region_code, years, market, lang)
    if region is None:
        return {"available": False,
                "reason": t("compare.no_region", lang)}

    region_pct, covered_years = region
    if covered_years < years * 0.8:
        # Rule 1: a shorter window is not the same question.
        return {"available": False,
                "reason": t("compare.short_history", lang,
                            years=years, covered=covered_years)}

    try:
        from backend.services.backtest import run_backtest

        portfolio = run_backtest(weights, amount, period=period)
    except Exception as exc:
        logger.warning("portfolio side unavailable (%s)", type(exc).__name__)
        return {"available": False, "reason": t("compare.no_portfolio", lang)}

    # ── Property, with the costs only it pays ───────────────────────────
    entry_cost_pct = pack_costs["transfer_tax_pct"] + pack_costs["agency_pct"]
    # The purchase costs come out of the amount, so less is actually invested.
    invested = amount * (1 - entry_cost_pct / 100)
    gross_value = invested * (1 + region_pct / 100)
    upkeep = invested * (pack_costs["annual_upkeep_pct"] / 100) * covered_years
    # Rent received over the period, at the market's documented gross yield.
    rent = invested * assumptions.gross_rental_yield(market) * covered_years
    property_value = gross_value - upkeep + rent

    portfolio_value = amount * (1 + portfolio["total_return_pct"] / 100)

    inflation = assumptions.annual_inflation_pct(market)
    deflator = (1 + inflation / 100) ** covered_years

    def _side(nominal: float) -> dict:
        return {
            "value": round(nominal, 2),
            "return_pct": round((nominal / amount - 1) * 100, 2),
            "real_value": round(nominal / deflator, 2),
            "real_return_pct": round((nominal / deflator / amount - 1) * 100, 2),
        }

    return {
        "available": True,
        "amount": amount,
        "years": covered_years,
        "market": market,
        "inflation_pct": inflation,
        "property": {
            **_side(property_value),
            "index_growth_pct": region_pct,
            "entry_costs": round(amount - invested, 2),
            "upkeep_paid": round(upkeep, 2),
            "rent_received": round(rent, 2),
        },
        "portfolio": {
            **_side(portfolio_value),
            "nominal_return_pct": portfolio["total_return_pct"],
        },
        # Named, not implied: the reader should see which costs were charged
        # to which side rather than having to trust the totals.
        "assumptions": pack_costs | {
            "gross_rental_yield_pct": round(assumptions.gross_rental_yield(market) * 100, 2),
        },
        "note": t("compare.note", lang),
    }


def yield_comparison(*, market: str = "TR", dividend_yield_pct: Optional[float] = None,
                     lang: str = "tr") -> dict:
    """
    "This flat yields 4% a year; this portfolio pays 6%."

    Income only, kept separate from the growth comparison above, because
    conflating the two is how people end up believing rent is free money.
    Rent is NET of upkeep here; a gross yield beside a dividend yield is not
    a like-for-like number, and the gross figure is the one agents quote.
    """
    gross = assumptions.gross_rental_yield(market) * 100
    upkeep = assumptions.annual_upkeep_pct(market)
    net_rent = round(gross - upkeep, 2)

    return {
        "market": market,
        "gross_rental_yield_pct": round(gross, 2),
        "annual_upkeep_pct": upkeep,
        "net_rental_yield_pct": net_rent,
        "dividend_yield_pct": dividend_yield_pct,
        "note": t("compare.yield_note", lang, upkeep=upkeep),
    }
