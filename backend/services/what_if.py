"""
What-If assistant — tool-use pattern: the AI never invents portfolio math.

Flow:
  1. LLM extracts the hypothetical CHANGE (budget delta, risk delta) as JSON
  2. We call the real portfolio_engine twice (before/after) — actual numbers
  3. LLM only phrases the comparison in plain language, given the real deltas

This guarantees every number the user sees came from portfolio_engine, not
from the model's imagination.
"""
import json
import logging
import re
from pathlib import Path

from backend.exceptions import AIServiceError
from backend.schemas.portfolio import PortfolioRecommendResponse
from backend.services.ai_service import _dispatch, generate_text
from backend.services.portfolio_engine import build_portfolio

logger = logging.getLogger("lumos.what_if")

_EXTRACT_PROMPT = (
    Path(__file__).parent.parent / "prompts" / "what_if_extract_prompt.txt"
).read_text()

_ANSWER_SYSTEM = """You are Lumos's what-if assistant. You are given the user's
question and REAL before/after numbers computed by the portfolio engine.
Explain the change in 2-3 calm, jargon-free sentences using ONLY the numbers
given to you — never invent or round differently than shown. If the risk
score changed, briefly note what that means for volatility. Respond in the
same language as the user's question.
End with the standard educational disclaimer."""


def _extract_change(question: str) -> dict:
    raw = _dispatch(
        [{"role": "user", "content": question}], _EXTRACT_PROMPT, max_tokens=200
    )
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip())
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        raise AIServiceError("What-if extraction returned non-JSON output")


def _diff_summary(before: PortfolioRecommendResponse, after: PortfolioRecommendResponse) -> dict:
    before_map = {a.ticker: a.weight for a in before.allocations}
    after_map = {a.ticker: a.weight for a in after.allocations}
    tickers = set(before_map) | set(after_map)
    changes = []
    for t in tickers:
        b, a = before_map.get(t, 0), after_map.get(t, 0)
        if abs(a - b) > 0.005:
            changes.append({"ticker": t, "before_pct": round(b * 100, 1), "after_pct": round(a * 100, 1)})
    return {
        "before_budget": before.budget,
        "after_budget": after.budget,
        "before_risk_score": before.risk_score,
        "after_risk_score": after.risk_score,
        "allocation_changes": sorted(changes, key=lambda c: abs(c["after_pct"] - c["before_pct"]), reverse=True),
    }


def answer_what_if(question: str, current_risk_score: float, current_budget: float) -> dict:
    """
    Returns {"understood": bool, "answer": str|None, "diff": dict|None}.
    When not understood, the caller should fall back to normal chat.
    """
    change = _extract_change(question)
    if not change.get("understood"):
        return {"understood": False, "answer": None, "diff": None}

    new_budget = max(current_budget + change.get("budget_delta", 0), 1)
    new_risk = min(max(current_risk_score + change.get("risk_score_delta", 0), 1), 10)

    before = build_portfolio(risk_score=current_risk_score, budget=current_budget)
    after = build_portfolio(risk_score=new_risk, budget=new_budget)
    diff = _diff_summary(before, after)

    context = (
        f"Question: {question}\n\n"
        f"REAL before/after numbers (computed by the portfolio engine):\n"
        f"{json.dumps(diff, ensure_ascii=False, indent=2)}"
    )
    answer = generate_text(context, system=_ANSWER_SYSTEM)

    logger.info(
        "what_if_answered budget_delta=%s risk_delta=%s",
        change.get("budget_delta"), change.get("risk_score_delta"),
    )
    return {"understood": True, "answer": answer, "diff": diff}
