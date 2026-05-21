from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class Notification(db.Model):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(db.BigInteger, primary_key=True)

    user_id: Mapped[int] = mapped_column(
        db.BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    event_id: Mapped[int | None] = mapped_column(
        db.BigInteger,
        ForeignKey("events.id", ondelete="SET NULL"),
        nullable=True,
    )

    organizer_id: Mapped[int | None] = mapped_column(
        db.BigInteger,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    notification_type: Mapped[str] = mapped_column(String(100), nullable=False)

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)

    action_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    is_read: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=db.text("false"),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=db.func.now(),
    )

    user = relationship(
        "User",
        back_populates="notifications",
        foreign_keys=[user_id],
    )

    event = relationship(
        "Event",
        back_populates="notifications",
        foreign_keys=[event_id],
    )

    organizer = relationship(
        "User",
        foreign_keys=[organizer_id],
    )

    __table_args__ = (
        Index("ix_notifications_user_id", "user_id"),
        Index("ix_notifications_event_id", "event_id"),
        Index("ix_notifications_organizer_id", "organizer_id"),
        Index("ix_notifications_notification_type", "notification_type"),
        Index("ix_notifications_is_read", "is_read"),
        Index("ix_notifications_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Notification id={self.id} user_id={self.user_id} type={self.notification_type}>"