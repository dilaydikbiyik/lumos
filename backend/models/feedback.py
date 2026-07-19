from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import String, DateTime, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.db.database import Base


class Feedback(Base):
    """
    A message a user sent from inside the app.

    Beginners rarely report problems — they close the tab. Lowering the cost of
    saying "I didn't understand this screen" to one tap is the point, so the
    only required field is the message itself.
    """
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    # Kept even if the user is later deleted: the report stays useful, and
    # nulling the link is enough to detach it from the person.
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), index=True, nullable=True
    )

    message: Mapped[str] = mapped_column(Text, nullable=False)
    # bug / confusing / idea / other — what the user picked, not inferred
    category: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    # Which screen they were on. The single most useful field for reproducing
    # a problem, and free to capture.
    page: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
