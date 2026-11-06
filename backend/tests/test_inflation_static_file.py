"""
The Turkish CPI the app deflates by — pinned to what TÜİK published.

Two defects lived here. The bundled fallback had 20 hand-entered points
and understated a year of inflation by more than half; and the live series
that replaced a stalled one was the PRODUCER price index, so every Turkish
real return was deflated by the wrong prices. Both are checked against
TÜİK's published December-on-December consumer inflation.
"""
import json
from pathlib import Path

import pandas as pd
import pytest

from backend.services import evds_service

STATIC = json.loads((Path(__file__).resolve().parents[1] / "data" / "tufe_index.json").read_text())["index"]

# TÜİK, TÜFE annual change, December on December.
PUBLISHED_DEC_ON_DEC = {2021: 36.08, 2022: 64.27, 2023: 64.77, 2024: 44.38, 2025: 30.89}


def test_the_static_file_has_one_value_for_every_month():
    months = sorted(STATIC)
    expected = list(pd.period_range(months[0], months[-1], freq="M").strftime("%Y-%m"))
    assert months == expected, "gaps make 'the previous month' five months back"


@pytest.mark.parametrize("year,published", sorted(PUBLISHED_DEC_ON_DEC.items()))
def test_the_static_file_matches_tuik(year, published):
    measured = (STATIC[f"{year}-12"] / STATIC[f"{year - 1}-12"] - 1) * 100
    assert measured == pytest.approx(published, abs=0.05)


def test_the_live_series_are_consumer_prices_never_the_producer_index():
    codes = (evds_service.CPI_ARCHIVE_SERIES, evds_service.CPI_CURRENT_SERIES)
    assert "TUFE1YI" not in " ".join(codes), "TP.TUFE1YI.T1 is the domestic PPI"
    assert not hasattr(evds_service, "CPI_SERIES")


def test_chain_keeps_the_archive_and_applies_the_new_series_changes():
    archive = {"2025-11": 200.0, "2025-12": 210.0, "2026-01": 999.0}
    current = {"2025-12": 100.0, "2026-01": 105.0, "2026-02": 110.25}
    chained = evds_service.chain_cpi(archive, current)
    assert chained["2025-11"] == 200.0 and chained["2025-12"] == 210.0
    assert chained["2026-01"] == pytest.approx(220.5)       # +5%, not the archive's stray value
    assert chained["2026-02"] == pytest.approx(231.525)


def test_chain_without_the_new_series_is_the_archive_alone():
    archive = {"2025-11": 200.0, "2025-12": 210.0}
    assert evds_service.chain_cpi(archive, {}) == archive
