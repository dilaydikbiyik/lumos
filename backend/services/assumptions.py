"""
Single source of truth for the planning assumptions used across the app's
projection tools (goal planner, rent-vs-buy).

MARKET-LINKED, NOT GUESSED: the dominant number — inflation — is read LIVE from
the TCMB CPI series (via inflation_service; falls back to the bundled static
CPI file when the EVDS key is absent, still a measured figure, not a hand-picked
one). Housing, rent and portfolio growth are then expressed as small, documented
REAL spreads over that live inflation, so every rate moves with the actual
market instead of being frozen at a stale guess.

Everything still degrades safely: if inflation can't be read at all, the tools
use INFLATION_FALLBACK_PCT. These remain PLANNING assumptions, not forecasts;
the real spreads are the only hand-set inputs and they live here, in one spot.
"""

import logging

logger = logging.getLogger("lumos.assumptions")


# Fallback inflation used only when no CPI data can be read at all.
INFLATION_FALLBACK_PCT = 40.0

# Real (inflation-adjusted) spreads — the only hand-set inputs. Housing and rent
# broadly track inflation in Turkey; a diversified portfolio is assumed to beat
# it by a modest long-run real premium. Conservative and easy to tune here.
PORTFOLIO_REAL_SPREAD_PCT = 3.0
HOUSING_REAL_SPREAD_PCT = 0.0
RENT_REAL_SPREAD_PCT = 0.0

# Mortgage terms are policy-driven, not inflation-derived — kept explicit.
MORTGAGE_RATE_PCT = 39.0
MORTGAGE_TERM_YEARS = 10

# ── Property transaction and ownership costs ────────────────────────────────
# Buying a home costs materially more than its price, and leaving these out
# flatters the "buy" side of every comparison. They are statutory or
# convention-driven rather than market-derived, so they are set here and shown
# to the user as assumptions.
#
# These are RATES SET BY REGULATION OR CUSTOM AND THEY CHANGE. Verify against
# the current tariff before treating any output as decision-grade.
#
# Title deed fee (tapu harcı): 4% of the declared value in total, split by law
# 2% buyer / 2% seller. Who actually pays is a matter of agreement between the
# parties, and in second-hand sales the buyer commonly absorbs all 4% — so the
# conservative default charges the buyer the full amount. This is an ASSUMPTION
# about market practice, not a legal requirement.
TITLE_DEED_FEE_PCT = 4.0
# Agency commission: the regulation caps it at 2% from each side, and the agent
# invoices VAT on top of that. Kept as two numbers because the VAT rate is set
# centrally and moves independently of the commission cap.
AGENCY_COMMISSION_PCT = 2.0
VAT_PCT = 20.0
# Recurring ownership costs as a share of home value per year: building dues,
# compulsory earthquake insurance (DASK) and upkeep. Renters pay dues too in
# many buildings, so only the ownership-specific part belongs here.
ANNUAL_UPKEEP_PCT = 1.0


def _pack(market: str = "TR"):
    from backend.markets import get_market_pack

    return get_market_pack(market)


def annual_inflation_pct(market: str = "TR") -> float:
    """Live trailing-12-month CPI inflation for a market; fallback if unavailable."""
    fallback = _pack(market).inflation_fallback_pct
    try:
        from backend.services import inflation_service
        v = inflation_service.trailing_annual_inflation_pct(market)
        if v and v > 0:
            return round(v, 1)
    except Exception as exc:  # data layer down → don't break the calculator
        # A silent fallback makes a static number look like a live one; say so.
        logger.warning(
            "live inflation unavailable for %s (%s) — using fallback %.1f%%",
            market, type(exc).__name__, fallback,
        )
    return fallback


def _apply_spread(base_pct: float, real_spread_pct: float) -> float:
    """Compound a real spread onto a nominal base (Fisher): (1+b)(1+s)−1."""
    return round(((1 + base_pct / 100) * (1 + real_spread_pct / 100) - 1) * 100, 1)


def _yoy_from_index(index: dict) -> float | None:
    """
    Trailing 12-period change from a {period: value} index.

    Works for monthly ("2026-07") and quarterly ("2026-Q1") keys alike: both
    sort lexicographically, and stepping back 4 or 12 entries is what "a year
    ago" means for each. Returns None when there isn't a full year of data —
    a partial year would understate growth without saying so.
    """
    if not index:
        return None
    periods = sorted(index)
    step = 4 if "Q" in periods[-1] else 12
    if len(periods) <= step:
        return None
    latest, prior = periods[-1], periods[-1 - step]
    if not index.get(prior):
        return None
    return round((index[latest] / index[prior] - 1) * 100, 1)


def portfolio_growth_pct(market: str = "TR") -> float:
    return _apply_spread(annual_inflation_pct(market), _pack(market).portfolio_real_spread_pct)


def housing_growth_pct(market: str = "TR") -> float:
    """
    Housing growth — measured where a real house PRICE index exists, and a
    documented spread over inflation where it doesn't. Germany publishes one
    quarterly; the US does not without a Case-Shiller key, and a rent index
    is not a substitute for it.
    """
    pack = _pack(market)
    if pack.housing_index_source == "eurostat":
        from backend.services import eurostat_service

        measured = _yoy_from_index(eurostat_service.get_house_price_index(market) or {})
        if measured is not None:
            return measured
    return _apply_spread(annual_inflation_pct(market), pack.housing_real_spread_pct)


def rent_growth_pct(market: str = "TR") -> float:
    """Measured rent growth where a rent index exists, else a spread over CPI."""
    pack = _pack(market)
    if pack.rent_index_source != "none":
        from backend.services import inflation_service

        measured = _yoy_from_index(inflation_service.get_rent_index(market))
        if measured is not None:
            return measured
    return _apply_spread(annual_inflation_pct(market), pack.rent_real_spread_pct)


def mortgage_rate_pct(market: str = "TR") -> float:
    return _pack(market).mortgage_rate_pct


def mortgage_term_years(market: str = "TR") -> int:
    return _pack(market).mortgage_term_years


def transfer_tax_pct(market: str = "TR") -> float:
    return _pack(market).transfer_tax_pct


def agency_commission_with_vat_pct(market: str = "TR") -> float:
    """Agency commission as actually invoiced — the rate plus VAT on top."""
    pack = _pack(market)
    return round(pack.agency_commission_pct * (1 + pack.vat_pct / 100), 2)


def annual_upkeep_pct(market: str = "TR") -> float:
    return _pack(market).annual_upkeep_pct


def gross_rental_yield(market: str = "TR") -> float:
    return _pack(market).gross_rental_yield


def real_rate_pct(nominal_pct: float, inflation_pct: float | None = None,
                  market: str = "TR") -> float:
    """Fisher real rate: what a nominal growth rate is worth after inflation."""
    if inflation_pct is None:
        inflation_pct = annual_inflation_pct(market)
    return round(((1 + nominal_pct / 100) / (1 + inflation_pct / 100) - 1) * 100, 2)


def real_value(nominal_amount: float, years: float,
               inflation_pct: float | None = None, market: str = "TR") -> float:
    """Today's purchasing power of a future nominal amount."""
    if inflation_pct is None:
        inflation_pct = annual_inflation_pct(market)
    return nominal_amount / (1 + inflation_pct / 100) ** years

