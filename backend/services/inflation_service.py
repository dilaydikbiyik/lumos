"""
Inflation reality layer — nominal returns lie in Turkey; real (TÜFE-adjusted)
returns tell the truth. This is a differentiator: almost no consumer
investing app in Turkey shows real returns by default.

Data source: backend/data/tufe_index.json (monthly TÜİK/TCMB index).
When settings.TCMB_EVDS_API_KEY is configured, swap _load_index() for a
live EVDS call — the rest of this module is source-agnostic.
"""
import json
import logging
from bisect import bisect_right
from datetime import date
from pathlib import Path
from typing import Optional

logger = logging.getLogger("lumos.inflation")

_INDEX_PATH = Path(__file__).parent.parent / "data" / "tufe_index.json"


def _load_index() -> dict[str, float]:
    data = json.loads(_INDEX_PATH.read_text())
    return data["index"]


_INDEX = _load_index()
_SORTED_MONTHS = sorted(_INDEX)


def _index_at(month: str) -> float:
    """
    Nearest known index value at or before the given YYYY-MM month
    (the dataset only has sparse checkpoints, not every month).
    """
    if month in _INDEX:
        return _INDEX[month]
    pos = bisect_right(_SORTED_MONTHS, month) - 1
    pos = max(pos, 0)
    return _INDEX[_SORTED_MONTHS[pos]]


def cpi_change_pct(start_month: str, end_month: str) -> float:
    """% change in the price index between two YYYY-MM months."""
    start_idx = _index_at(start_month)
    end_idx = _index_at(end_month)
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
    reference_month = reference_month or _SORTED_MONTHS[-1]
    idx = _SORTED_MONTHS.index(reference_month) if reference_month in _SORTED_MONTHS else len(_SORTED_MONTHS) - 1
    if idx == 0:
        return {"monthly_inflation_pct": 0.0, "erosion_amount": 0.0}

    prev_month = _SORTED_MONTHS[idx - 1]
    curr_month = _SORTED_MONTHS[idx]
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
