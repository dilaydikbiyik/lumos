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
        "provider": "gemini",
        # Her modelin AYRI free kotası var — zincir, ücretsiz kapasiteyi katlar
        "model_chain": ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.0-flash"],
        "daily_quota": 50,
        "max_tokens": 4096,
        "price_monthly_usd": 0,
        "pitch": "Öğrenmeye başlamak için ihtiyacın olan her şey — sonsuza dek ücretsiz.",
    },
    "plus": {
        "label": "Fener",
        "provider": "gemini",
        # Ücretli Gemini: pro model önde, flash zinciri yedekte
        "model_chain": ["gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.5-flash-lite"],
        "daily_quota": 500,
        "max_tokens": 8192,
        "price_monthly_usd": 4.99,
        "pitch": "Daha derin analizler, 10 kat mesaj hakkı, öncelikli model.",
    },
    "pro": {
        "label": "Şafak",
        "provider": "anthropic",
        # Claude ailesi: en güçlü model önde, hafif model kota/kredi yedeği
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
