"""
Portfolio explainer — uses the configured AI provider for plain-language summaries.
"""

from pathlib import Path
from backend.models.portfolio import PortfolioRecommendResponse
from backend.services.ai_service import generate_text

_REIT_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "reit_explain_prompt.txt"
_REIT_PROMPT_TEMPLATE = _REIT_PROMPT_PATH.read_text()


def explain_portfolio(portfolio: PortfolioRecommendResponse, user_profile: dict) -> str:
    """Generate a plain-language portfolio explanation."""
    alloc_lines = "\n".join(
        f"  - {a.name} ({a.ticker}): {a.weight * 100:.1f}%"
        for a in portfolio.allocations
    )
    profile_lines = "\n".join(f"  - {k}: {v}" for k, v in user_profile.items() if v)
    prompt = (
        f"The user has a risk score of {portfolio.risk_score}/10 "
        f"and a budget of {portfolio.budget:,.0f} TRY.\n"
        f"Their profile:\n{profile_lines or '  (no extra profile data)'}\n\n"
        f"Their recommended portfolio allocation:\n{alloc_lines}\n\n"
        "Write a 4–5 sentence explanation for someone who has NEVER invested before:\n"
        "1. What this mix is in plain words (explain any finance term inline, e.g. "
        "'fund (a ready-made basket of investments)').\n"
        "2. WHY this specific balance fits THEIR risk score and goal — reference their "
        "profile, don't be generic.\n"
        "3. One honest sentence about what could go wrong (e.g. temporary drops) and why "
        "the mix is designed to soften it — calm, not alarming.\n"
        "Respond in the same language the user has been using (Turkish or English).\n\n"
        "⚠️ Always end with: 'This is for educational purposes only and does not constitute "
        "investment advice. Please consult a licensed financial advisor.'"
    )
    return generate_text(prompt)


def explain_reit_inclusion(portfolio: PortfolioRecommendResponse, user_profile: dict) -> str:
    """Generate a personalised REIT explanation (3 sentences per prompt template)."""
    filled_prompt = _REIT_PROMPT_TEMPLATE.format(
        risk_score=portfolio.risk_score,
        budget=portfolio.budget,
        time_horizon=user_profile.get("time_horizon", "medium"),
        loss_tolerance=user_profile.get("loss_tolerance", "medium"),
        goal=user_profile.get("goal", "growth"),
        experience=user_profile.get("experience", "beginner"),
    )
    return generate_text(filled_prompt)
