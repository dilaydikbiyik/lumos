"""
Inflation reality layer — nominal returns lie in Turkey; real (TÜFE-adjusted)
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


def _get_index() -> dict[str, float]:
    """Live EVDS index when available (cached daily), else the static file."""
    from backend.services import evds_service  # local import avoids cycles

    live = evds_service.get_live_cpi_index()
    if live:
        return live
    return _STATIC_INDEX


def _index_at(index: dict[str, float], sorted_months: list, month: str) -> float:
    """Nearest known index value at or before the given YYYY-MM month."""
    if month in index:
        return index[month]
    pos = bisect_right(sorted_months, month) - 1
    pos = max(pos, 0)
    return index[sorted_months[pos]]


def cpi_change_pct(start_month: str, end_month: str) -> float:
    """% change in the price index between two YYYY-MM months."""
    index = _get_index()
    sorted_months = sorted(index)
    start_idx = _index_at(index, sorted_months, start_month)
    end_idx = _index_at(index, sorted_months, end_month)
    return (end_idx / start_idx - 1) * 100


def real_return_pct(nominal_return_pct: float, start_month: str, end_month: str) -> float:
    """
    Fisher-adjusted real return: what the nominal gain is actually worth
    after inflation eats into it. This is the number that keeps people
    from celebrating a loss that felt like a win.
    """
    inflation_pct = cpi_change_pct(start_month, end_month)
    real = ((1 + nominal_return_pct / 100) / (1 + inflation_pct / 100) - 1) * 100
    return round(real, 2)


def monthly_cash_erosion(cash_amount: float, reference_month: Optional[str] = None) -> dict:
    """
    'Param eriyor mu?' — how much real purchasing power idle cash loses
    per month at the most recent known inflation rate.
    """
    index = _get_index()
    sorted_months = sorted(index)
    reference_month = reference_month or sorted_months[-1]
    idx = sorted_months.index(reference_month) if reference_month in sorted_months else len(sorted_months) - 1
    if idx == 0:
        return {"monthly_inflation_pct": 0.0, "erosion_amount": 0.0}

    prev_month = sorted_months[idx - 1]
    curr_month = sorted_months[idx]
    monthly_pct = cpi_change_pct(prev_month, curr_month)
    erosion = cash_amount * (monthly_pct / 100)
    return {
        "monthly_inflation_pct": round(monthly_pct, 2),
        "erosion_amount": round(erosion, 2),
    }


def years_to_months_ago(years: float, today: Optional[date] = None) -> str:
    """Helper: 'N years ago' as a YYYY-MM string, for wiring into backtest periods."""
    today = today or date.today()
    total_months = today.year * 12 + today.month - round(years * 12)
    year, month = divmod(total_months - 1, 12)
    return f"{year}-{month + 1:02d}"
