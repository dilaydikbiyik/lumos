from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.db.database import Base


class PushSubscription(Base):
    """
    One browser's permission to be told something in real time.

    The behavioural coach's most important message — "the market dropped, here
    is why not to sell" — is worthless if it waits for the reader to open the
    app, because by then they have already sold. This is the carrier.

    It exists WITHOUT a store account. Until iOS 16.4 (March 2023) the only
    way to reach an iPhone was APNs through a native wrapper, which meant an
    Apple Developer Program membership; a home-screen web app can now be
    pushed to directly, and as of iOS 26 a site added to the Home Screen opens
    as a web app by default. Android Chrome has carried it for years.

    ONE ROW PER BROWSER, not per user: somebody who installs the app on a
    phone and a laptop expects both to alert. The endpoint is the identity —
    browsers reissue it, so it is unique and a re-subscribe updates in place
    rather than accumulating dead rows.
    """
    __tablename__ = "push_subscriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    # The push service URL the browser issued. Unique: it IS the device.
    endpoint: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    # Encryption material. These are the browser's public values — they let a
    # message be sealed FOR that browser and are useless for reading one.
    p256dh: Mapped[str] = mapped_column(String(255), nullable=False)
    auth: Mapped[str] = mapped_column(String(255), nullable=False)
    # Which UI language this browser asked in. A notification arriving in a
    # language the reader does not use is worse than no notification: it looks
    # like the wrong app, at the moment they are already anxious.
    lang: Mapped[str] = mapped_column(String(8), default="tr", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    # Set when the push service says the subscription is gone (404/410), so a
    # dead browser stops being retried on every market move.
    failed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
