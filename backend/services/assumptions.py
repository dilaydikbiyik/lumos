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


def annual_inflation_pct() -> float:
    """Live trailing-12-month CPI inflation; fallback if unavailable."""
    try:
        from backend.services import inflation_service
        v = inflation_service.trailing_annual_inflation_pct()
        if v and v > 0:
            return round(v, 1)
    except Exception as exc:  # data layer down → don't break the calculator
        # A silent fallback makes a static number look like a live one; say so.
        logger.warning(
            "live inflation unavailable (%s) — using static fallback %.1f%%",
            type(exc).__name__, INFLATION_FALLBACK_PCT,
        )
    return INFLATION_FALLBACK_PCT


def _apply_spread(base_pct: float, real_spread_pct: float) -> float:
    """Compound a real spread onto a nominal base (Fisher): (1+b)(1+s)−1."""
    return round(((1 + base_pct / 100) * (1 + real_spread_pct / 100) - 1) * 100, 1)


def portfolio_growth_pct() -> float:
    return _apply_spread(annual_inflation_pct(), PORTFOLIO_REAL_SPREAD_PCT)


def housing_growth_pct() -> float:
    return _apply_spread(annual_inflation_pct(), HOUSING_REAL_SPREAD_PCT)


def rent_growth_pct() -> float:
    return _apply_spread(annual_inflation_pct(), RENT_REAL_SPREAD_PCT)


def mortgage_rate_pct() -> float:
    return MORTGAGE_RATE_PCT


def mortgage_term_years() -> int:
    return MORTGAGE_TERM_YEARS


def real_rate_pct(nominal_pct: float, inflation_pct: float | None = None) -> float:
    """Fisher real rate: what a nominal growth rate is worth after inflation."""
    if inflation_pct is None:
        inflation_pct = annual_inflation_pct()
    return round(((1 + nominal_pct / 100) / (1 + inflation_pct / 100) - 1) * 100, 2)


def real_value(nominal_amount: float, years: float,
               inflation_pct: float | None = None) -> float:
    """Today's purchasing power of a future nominal amount."""
    if inflation_pct is None:
        inflation_pct = annual_inflation_pct()
    return nominal_amount / (1 + inflation_pct / 100) ** years


def agency_commission_with_vat_pct() -> float:
    """Agency commission as actually invoiced — the cap plus VAT on top."""
    return round(AGENCY_COMMISSION_PCT * (1 + VAT_PCT / 100), 2)
