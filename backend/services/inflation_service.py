"""
Inflation reality layer — nominal returns lie in Turkey; real (CPI-adjusted)
returns tell the truth. This is a differentiator: almost no consumer
investing app in Turkey shows real returns by default.

Data sources, in preference order:
  1. Live TCMB EVDS TÜFE series (when TCMB_EVDS_API_KEY is set) — full
     monthly resolution, always current
  2. Bundled backend/data/tufe_index.json — sparse static checkpoints

All math works on index RATIOS, so the two sources' different base years
(2003=100 vs 2020-01=100) don't matter.
"""
import json
import logging
from bisect import bisect_right
from datetime import date
from pathlib import Path
from typing import Optional

logger = logging.getLogger("lumos.inflation")

_INDEX_PATH = Path(__file__).parent.parent / "data" / "tufe_index.json"


def _load_static_index() -> dict[str, float]:
    data = json.loads(_INDEX_PATH.read_text())
    return data["index"]


_STATIC_INDEX = _load_static_index()


def _get_index(market: str = "TR") -> dict[str, float]:
    """
    The CPI index for a market, keyed by YYYY-MM.

    Routed through the market pack rather than hardcoded: "real return" is
    this app's core claim, and it was only ever true for Türkiye — every
    other market silently measured US and German portfolios against Turkish
    inflation. Falls back to the bundled Turkish static file only for TR;
    a market whose live source fails returns nothing rather than borrowing
    another country's prices.
    """
    from backend.markets import get_market_pack

    source = get_market_pack(market).inflation_source

    if source == "tcmb_evds":
        from backend.services import evds_service  # local import avoids cycles

        live = evds_service.get_live_cpi_index()
        # Freshest wins, rather than "live always". The upstream series can
        # stall — one did, at 2026-01 — and blindly preferring it served data
        # eight months older than the copy already bundled in the repo.
        return _freshest(live, _STATIC_INDEX)
    if source == "bls":
        from backend.services import bls_service

        return bls_service.get_cpi_index() or {}
    if source == "eurostat":
        from backend.services import eurostat_service

        return eurostat_service.get_hicp_index(market) or {}
    if source == "bundesbank":
        from backend.services import bundesbank_service

        return bundesbank_service.get_hicp_index() or {}
    return {}


def index_as_of(market: str = "TR") -> Optional[str]:
    """
    The most recent month the CPI index actually covers, as YYYY-MM.

    Published with a lag that differs by country — and one upstream series
    stalled for eight months without warning. A number carrying a visible
    "as of" date is one a user can judge; the same number without it is a
    claim about today that may be nine months old.
    """
    index = _get_index(market)
    return max(index) if index else None


def _freshest(*indices) -> dict[str, float]:
    """The index whose most recent observation is latest; {} if none have any."""
    usable = [i for i in indices if i]
    if not usable:
        return {}
    return max(usable, key=lambda i: max(i))


def get_rent_index(market: str = "TR") -> dict[str, float]:
    """Rent index for a market, or {} when that market has no direct series."""
    from backend.markets import get_market_pack

    source = get_market_pack(market).rent_index_source
    if source == "bls":
        from backend.services import bls_service

        return bls_service.get_rent_index() or {}
    if source == "eurostat":
        from backend.services import eurostat_service

        return eurostat_service.get_rent_index(market) or {}
    if source == "bundesbank":
        from backend.services import bundesbank_service

        return bundesbank_service.get_rent_index() or {}
    return {}


def _index_at(index: dict[str, float], sorted_months: list, month: str) -> float:
    """Nearest known index value at or before the given YYYY-MM month."""
    if month in index:
        return index[month]
    pos = bisect_right(sorted_months, month) - 1
    pos = max(pos, 0)
    return index[sorted_months[pos]]


def cpi_change_pct(start_month: str, end_month: str, market: str = "TR") -> float:
    """% change in the price index between two YYYY-MM months."""
    index = _get_index(market)
    if not index:
        return 0.0
    sorted_months = sorted(index)
    start_idx = _index_at(index, sorted_months, start_month)
    end_idx = _index_at(index, sorted_months, end_month)
    return (end_idx / start_idx - 1) * 100


def trailing_annual_inflation_pct(market: str = "TR") -> float:
    """
    Realized inflation over the last ~12 months from the CPI index (live TCMB
    when configured, else the bundled static file). This is a MEASURED number,
    not a guess — it's what planning tools use as the live inflation assumption.
    Returns 0.0 only if the index has too few points to compute.
    """
    index = _get_index(market)
    months = sorted(index)
    if len(months) < 2:
        return 0.0
    latest = months[-1]
    year, month = latest.split("-")
    a_year_ago = f"{int(year) - 1}-{month}"  # cpi_change_pct snaps to nearest prior month
    return round(cpi_change_pct(a_year_ago, latest, market), 2)


def real_return_pct(nominal_return_pct: float, start_month: str, end_month: str,
                    market: str = "TR") -> float:
    """
    Fisher-adjusted real return: what the nominal gain is actually worth
    after inflation eats into it. This is the number that keeps people
    from celebrating a loss that felt like a win.
    """
    inflation_pct = cpi_change_pct(start_month, end_month, market)
    real = ((1 + nominal_return_pct / 100) / (1 + inflation_pct / 100) - 1) * 100
    return round(real, 2)


def monthly_cash_erosion(cash_amount: float, reference_month: Optional[str] = None,
                         market: str = "TR") -> dict:
    """
    "Is my money melting?" — how much real purchasing power idle cash loses
    in a typical month at the current inflation rate.

    The rate is the last twelve months' inflation as a monthly equivalent,
    (1 + annual)^(1/12) - 1, not the single latest month. One month is
    noise: Germany's October 2026 HICP fell, so the card read "eroding
    -€25 per month" under a heading about money melting, while the goal
    planner for the same reader used 2.8% a year. The bundled Turkish file
    also had gaps, and "the previous key" was five months back, so a
    five-month change was printed as monthly inflation. Twelve months from
    the same index the planner reads keeps the two pages on one number.

    The loss is the purchasing power that disappears, not the price rise:
    after a month of 3% inflation, 10,000 buys what 9,708.74 bought, so
    291.26 of value is gone — not 300.
    """
    index = _get_index(market)
    if len(index) < 2:
        return {"monthly_inflation_pct": 0.0, "erosion_amount": 0.0}
    sorted_months = sorted(index)
    end = reference_month if reference_month in index else sorted_months[-1]
    year, month = end.split("-")
    start = f"{int(year) - 1}-{month}"
    if start < sorted_months[0]:
        # Less than a year of history: the span there is, per month.
        start = sorted_months[0]
    span = _months_between(start, end)
    if span <= 0:
        return {"monthly_inflation_pct": 0.0, "erosion_amount": 0.0}
    change = cpi_change_pct(start, end, market) / 100
    monthly_pct = ((1 + change) ** (1 / span) - 1) * 100
    erosion = cash_amount - cash_amount / (1 + monthly_pct / 100)
    return {
        "monthly_inflation_pct": round(monthly_pct, 2),
        "erosion_amount": round(erosion, 2),
    }


def _months_between(start: str, end: str) -> int:
    sy, sm = map(int, start.split("-"))
    ey, em = map(int, end.split("-"))
    return (ey - sy) * 12 + (em - sm)


def inflation_window(years: float, market: str = "TR") -> tuple[str, str]:
    """
    (start, end) months for deflating a return over the last `years`.

    Ends at the latest month the index covers and starts exactly `years`
    earlier, so it spans `years` x 12 months. It used to end at "this month"
    and start `years` before that; CPI is published with a lag, so the end
    snapped back a month and five years of prices were deflated by 59 months
    of inflation — Turkish real returns overstated by about two points.
    """
    end = index_as_of(market) or years_to_months_ago(0)
    y, m = map(int, end.split("-"))
    total = y * 12 + (m - 1) - round(years * 12)
    return f"{total // 12}-{total % 12 + 1:02d}", end


def years_to_months_ago(years: float, today: Optional[date] = None) -> str:
    """Helper: 'N years ago' as a YYYY-MM string, for wiring into backtest periods."""
    today = today or date.today()
    total_months = today.year * 12 + today.month - round(years * 12)
    year, month = divmod(total_months - 1, 12)
    return f"{year}-{month + 1:02d}"
