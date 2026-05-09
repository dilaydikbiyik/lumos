"""
TEFAS fund data service.

Fetches Turkish investment fund data.
Provides pre-built conservative / balanced / aggressive fund lists.
Real TEFAS API integration can be added later; for now we use curated static data.
"""

import json
from pathlib import Path

from backend.services import cache as cache_service

_FUND_LIST_PATH = Path(__file__).parent.parent / "data" / "fund_list.json"

FUND_TICKERS = {
    "conservative": ["TRBIST030", "TRGOLD", "TRMONEY"],
    "balanced": ["TRBIST100", "TRGOLD", "TRFOREIGN"],
    "aggressive": ["TRBIST100", "TRTECH", "TRFOREIGN"],
}


def get_fund_list() -> dict:
    """Return the full fund list from the JSON file (cached)."""
    cached = cache_service.get("fund_list")
    if cached:
        return cached
    with open(_FUND_LIST_PATH) as f:
        data = json.load(f)
    cache_service.set("fund_list", data)
    return data


def get_funds_by_risk(risk_score: float) -> list[dict]:
    """
    Return fund recommendations based on risk score.
      1–3  → conservative
      4–7  → balanced
      8–10 → aggressive
    """
    if risk_score <= 3:
        key = "conservative"
    elif risk_score <= 7:
        key = "balanced"
    else:
        key = "aggressive"

    fund_data = get_fund_list()
    return fund_data.get(key, [])
