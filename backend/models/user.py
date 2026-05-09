from datetime import datetime

from sqlalchemy import String, DateTime, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column

from backend.db.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    clerk_user_id: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Risk profile (denormalised for fast reads)
    risk_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    budget: Mapped[float | None] = mapped_column(Float, nullable=True)
    time_horizon: Mapped[str | None] = mapped_column(String, nullable=True)
    loss_tolerance: Mapped[str | None] = mapped_column(String, nullable=True)
    goal: Mapped[str | None] = mapped_column(String, nullable=True)
    experience: Mapped[str | None] = mapped_column(String, nullable=True)
