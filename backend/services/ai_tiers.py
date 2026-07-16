"""
AI plan tiers — billing-ready infrastructure for paid model access.

Each tier bundles: provider, an ordered model fallback chain (the quota-
resilience pattern proven on the free tier), a daily message quota, and
display metadata for a future pricing page.

Payments are deliberately NOT implemented here. The integration point is
a single call: set_user_plan(user, "plus") — a Stripe/Iyzico webhook (or
an admin) flips the plan, everything else (models, quotas, fallbacks)
follows from this table. No other code needs to change when billing lands.
"""

AI_TIERS: dict[str, dict] = {
    "free": {
        "label": "Ateş Böceği",
        "provider": "gemini",  # legacy/default single-provider hint (still read by _resolve_tier)
        # Each model has its OWN free quota — the chain multiplies free capacity
        "model_chain": ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.0-flash", "gemini-2.0-flash-lite"],
        # CROSS-PROVIDER free failover: when Gemini's shared free quota is
        # spent, the request falls to Groq, then to OpenRouter's :free models.
        # Three independent free tiers rarely run dry at once → no dead ends,
        # no paid credit, no ToS-violating key farming.
        "provider_chain": [
            {"provider": "gemini", "model_chain": [
                "gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.0-flash", "gemini-2.0-flash-lite",
            ]},
            {"provider": "groq", "model_chain": [
                # gpt-oss-120b: strong open model, quiz-eligible, very fast on Groq
                "openai/gpt-oss-120b",
                "llama-3.3-70b-versatile", "llama-3.1-8b-instant",
            ]},
            {"provider": "openrouter", "model_chain": [
                "meta-llama/llama-3.3-70b-instruct:free",
                "deepseek/deepseek-chat-v3-0324:free",
                # Google-quality models — also eligible for the scripted quiz
                "google/gemma-4-31b-it:free",
                "google/gemma-4-26b-a4b-it:free",
            ]},
        ],
        "daily_quota": 50,
        "max_tokens": 4096,
        "price_monthly_usd": 0,
        "pitch": "Öğrenmeye başlamak için ihtiyacın olan her şey — sonsuza dek ücretsiz.",
    },
    "plus": {
        "label": "Fener",
        "provider": "gemini",
        # Paid Gemini: pro model first, flash chain as backup
        "model_chain": ["gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.5-flash-lite"],
        "daily_quota": 500,
        "max_tokens": 8192,
        "price_monthly_usd": 4.99,
        "pitch": "Daha derin analizler, 10 kat mesaj hakkı, öncelikli model.",
    },
    "pro": {
        "label": "Şafak",
        "provider": "anthropic",
        # Claude family: strongest model first, light model as quota/credit backup
        "model_chain": ["claude-sonnet-4-6", "claude-haiku-4-5"],
        "daily_quota": 2000,
        "max_tokens": 8192,
        "price_monthly_usd": 14.99,
        "pitch": "En güçlü danışman deneyimi — Claude destekli, en yüksek limitler.",
    },
}

DEFAULT_PLAN = "free"


def get_tier(plan: str) -> dict:
    """Tier config for a plan name; unknown plans degrade safely to free."""
    return AI_TIERS.get(plan, AI_TIERS[DEFAULT_PLAN])


def public_tiers() -> list[dict]:
    """Pricing-page payload — no internal fields like model chains."""
    return [
        {
            "plan": name,
            "label": t["label"],
            "daily_quota": t["daily_quota"],
            "price_monthly_usd": t["price_monthly_usd"],
            "pitch": t["pitch"],
        }
        for name, t in AI_TIERS.items()
    ]
