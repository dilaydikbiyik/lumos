"""
What-If assistant tests — extraction and phrasing mocked, portfolio_engine real
(market data mocked so the volatility calc is deterministic and offline).

The key guarantee under test: the LLM never invents numbers. Every value
in the diff comes from build_portfolio(), called twice with real inputs.
"""
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest

from backend.services.what_if import answer_what_if

EXTRACT_ADD_BUDGET = '{"budget_delta": 50000, "risk_score_delta": 0, "understood": true}'
EXTRACT_MORE_AGGRESSIVE = '{"budget_delta": 0, "risk_score_delta": 3, "understood": true}'
EXTRACT_UNRELATED = '{"budget_delta": 0, "risk_score_delta": 0, "understood": false}'

_rng = np.random.default_rng(3)
_DATES = pd.bdate_range("2025-01-01", periods=252)


def _fake_history(tickers, period="1y"):
    return {
        t: pd.Series(100 * np.cumprod(1 + _rng.normal(0.0003, 0.01 + i * 0.004, 252)), index=_DATES)
        for i, t in enumerate(tickers)
    }


@pytest.fixture(autouse=True)
def _mock_market_data():
    with patch("backend.services.volatility.fetch_price_history", side_effect=_fake_history):
        yield


def test_what_if_budget_increase_uses_real_engine():
    with patch("backend.services.what_if._dispatch", return_value=EXTRACT_ADD_BUDGET), \
         patch("backend.services.what_if.generate_text", return_value="Açıklama metni."):
        result = answer_what_if("10.000 TL daha eklesem?", 5.0, 100000)

    assert result["understood"] is True
    assert result["diff"]["before_budget"] == 100000
    assert result["diff"]["after_budget"] == 150000
    assert result["diff"]["before_risk_score"] == 5.0
    assert result["diff"]["after_risk_score"] == 5.0
    assert result["answer"] == "Açıklama metni."


def test_what_if_risk_change_shifts_allocations():
    with patch("backend.services.what_if._dispatch", return_value=EXTRACT_MORE_AGGRESSIVE), \
         patch("backend.services.what_if.generate_text", return_value="Daha agresif olurdun."):
        result = answer_what_if("daha agresif olsam?", 4.0, 100000)

    assert result["diff"]["after_risk_score"] == 7.0
    assert isinstance(result["diff"]["allocation_changes"], list)


def test_what_if_unrelated_question_falls_back():
    with patch("backend.services.what_if._dispatch", return_value=EXTRACT_UNRELATED):
        result = answer_what_if("hava nasıl?", 5.0, 100000)

    assert result["understood"] is False
    assert result["answer"] is None


def test_what_if_risk_score_clamped_to_bounds():
    extreme = '{"budget_delta": 0, "risk_score_delta": 20, "understood": true}'
    with patch("backend.services.what_if._dispatch", return_value=extreme), \
         patch("backend.services.what_if.generate_text", return_value="ok"):
        result = answer_what_if("çok daha riskli olsam?", 9.0, 100000)
    assert result["diff"]["after_risk_score"] == 10


def test_what_if_endpoint(client):
    with patch("backend.services.what_if._dispatch", return_value=EXTRACT_ADD_BUDGET), \
         patch("backend.services.what_if.generate_text", return_value="Açıklama."):
        res = client.post("/chat/what-if", json={
            "question": "10.000 TL eklesem?", "risk_score": 5.0, "budget": 100000,
        })
    assert res.status_code == 200
    assert res.json()["understood"] is True


def test_what_if_endpoint_validates_risk_score(client):
    res = client.post("/chat/what-if", json={
        "question": "test", "risk_score": 15, "budget": 100000,
    })
    assert res.status_code == 422
