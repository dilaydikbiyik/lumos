from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import String, DateTime, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column

from backend.db.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    clerk_user_id: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Risk profile (denormalised for fast reads)
    risk_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    budget: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    time_horizon: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    loss_tolerance: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    goal: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    experience: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Access role: user (default) / admin — admin unlocks /admin/stats
    role: Mapped[str] = mapped_column(String, default="user", nullable=False, server_default="user")

    # Chosen journey: stocks / real_estate / hybrid / undecided (Akış 0)
    investment_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Onboarding fear check-in: param_eriyor / kandirilirim / anlamiyorum / batiririm
    primary_fear: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Daily AI message quota (resets when quota_date changes)
    quota_date: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # YYYY-MM-DD
    quota_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False, server_default="0")
