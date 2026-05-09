"""
Portfolio explainer — uses Claude to generate a plain-language summary.
"""

from pathlib import Path
from backend.models.portfolio import PortfolioRecommendResponse
from backend.services.ai_service import generate_text

_REIT_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "reit_explain_prompt.txt"
_REIT_PROMPT_TEMPLATE = _REIT_PROMPT_PATH.read_text()


def explain_portfolio(portfolio: PortfolioRecommendResponse, user_profile: dict) -> str:
    """Generate a plain-language portfolio explanation via Claude."""
    alloc_lines = "\n".join(
        f"  - {a.name} ({a.ticker}): {a.weight * 100:.1f}%"
        for a in portfolio.allocations
    )
    prompt = (
        f"The user has a risk score of {portfolio.risk_score}/10 "
        f"and a budget of {portfolio.budget:,.0f} TRY.\n\n"
        f"Their portfolio allocation:\n{alloc_lines}\n\n"
        "In 3–4 sentences, explain this portfolio in simple, jargon-free language. "
        "Mention what each major category is and why it suits their profile.\n\n"
        "⚠️ Always end with: 'This is for educational purposes only and does not constitute "
        "investment advice. Please consult a licensed financial advisor.'"
    )
    return generate_text(prompt)


def explain_reit_inclusion(portfolio: PortfolioRecommendResponse, user_profile: dict) -> str:
    """Generate a personalised 2-sentence REIT explanation via Claude."""
    filled_prompt = _REIT_PROMPT_TEMPLATE.format(
        risk_score=portfolio.risk_score,
        budget=portfolio.budget,
        time_horizon=user_profile.get("time_horizon", "medium"),
        loss_tolerance=user_profile.get("loss_tolerance", "medium"),
        goal=user_profile.get("goal", "growth"),
        experience=user_profile.get("experience", "beginner"),
    )
    return generate_text(filled_prompt)
