from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    APP_ENV: str = "development"
    APP_PORT: int = 8000
    FRONTEND_URL: str = "http://localhost:5173"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./lumos.db"

    # AI provider: "gemini" (free tier) or "anthropic"
    AI_PROVIDER: str = "gemini"
    ANTHROPIC_API_KEY: str = ""   # set in .env before using AI features
    GEMINI_API_KEY: str = ""      # https://aistudio.google.com/apikey — free tier
    GEMINI_API_KEY_2: str = ""    # Optional: extra quota from a 2nd Google account
    GEMINI_API_KEY_3: str = ""    # Optional: extra quota from a 3rd Google account
    GEMINI_API_KEY_4: str = ""    # Optional: extra quota from a 4th Google account

    # Free failover providers — when Gemini's free quota is spent the free tier
    # falls to these (each has its own independent free tier). No card required.
    GROQ_API_KEY: str = ""        # https://console.groq.com/keys — free, very fast (Llama)
    OPENROUTER_API_KEY: str = ""  # https://openrouter.ai/keys — free `:free` models

    # Clerk
    CLERK_PUBLISHABLE_KEY: str = ""
    CLERK_SECRET_KEY: str = ""
    CLERK_JWT_ISSUER: str = ""

    # Exchange Rate (optional)
    EXCHANGE_RATE_API_KEY: str = ""

    # TCMB EVDS — live CPI (TUFE) + housing price index (free key)
    TCMB_EVDS_API_KEY: str = ""

    # ── Observability (optional) ──
    SENTRY_DSN: str = ""          # sentry.io — leave empty to disable error monitoring

    # Usage limits
    DAILY_MESSAGE_QUOTA: int = 50

    # Admin bootstrap: comma-separated Clerk user IDs that are auto-promoted
    # to role='admin' on startup. Set this in the Render env panel.
    # e.g. ADMIN_CLERK_IDS=user_2abc,user_2xyz
    ADMIN_CLERK_IDS: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()

# Make the quota practically unlimited in development
if settings.APP_ENV == "development":
    settings.DAILY_MESSAGE_QUOTA = 9999
