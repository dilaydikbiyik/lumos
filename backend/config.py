from pydantic_settings import BaseSettings


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

    # Clerk
    CLERK_PUBLISHABLE_KEY: str = ""
    CLERK_SECRET_KEY: str = ""
    CLERK_JWT_ISSUER: str = ""

    # Exchange Rate (optional)
    EXCHANGE_RATE_API_KEY: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
