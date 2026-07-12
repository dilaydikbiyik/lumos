from datetime import datetime, date, timezone
from typing import Optional

from sqlalchemy import String, DateTime, Date, Integer, Float, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.db.database import Base


class Holding(Base):
    """
    A single asset the user actually owns — stocks and funds, but also
    off-exchange wealth like land, apartments, vehicles, gold, and cash.
    """
    __tablename__ = "holdings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )

    # stock / fund / etf / real_estate / land / vehicle / gold / crypto / cash / other
    asset_type: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    ticker: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # exchange assets only

    purchase_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    purchase_amount: Mapped[float] = mapped_column(Float, nullable=False)  # total paid, TRY
    quantity: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Manual valuation for off-exchange assets (land, apartment, vehicle...)
    manual_current_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # Optional 1-tap emotion tag at purchase: plan / fomo / tuyo / panik
    emotion_tag: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )
