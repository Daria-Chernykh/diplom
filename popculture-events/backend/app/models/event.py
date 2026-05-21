from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class Event(db.Model):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(db.BigInteger, primary_key=True)

    organizer_id: Mapped[int] = mapped_column(
        db.BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    short_description: Mapped[str] = mapped_column(Text, nullable=False)
    long_description: Mapped[str] = mapped_column(Text, nullable=False)

    event_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    event_format: Mapped[str] = mapped_column(
        Enum("offline", "online", name="event_format"),
        nullable=False,
        default="offline",
        server_default="offline",
    )

    location: Mapped[str] = mapped_column(String(500), nullable=False)
    schedule: Mapped[str | None] = mapped_column(Text, nullable=True)
    participant_requirements: Mapped[str | None] = mapped_column(Text, nullable=True)

    registration_type: Mapped[str] = mapped_column(
        Enum("internal", "external", "none", name="event_registration_type"),
        nullable=False,
    )

    registration_confirmation: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    external_registration_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    price_type: Mapped[str] = mapped_column(
        Enum("free", "fixed", "from", name="event_price_type"),
        nullable=False,
        default="free",
        server_default="free",
    )

    price_value: Mapped[str | None] = mapped_column(String(100), nullable=True)

    status: Mapped[str] = mapped_column(
        Enum("published", "blocked", "on_review", "archived", name="event_status"),
        nullable=False,
        default="published",
        server_default="published",
    )

    organizer_complaint_comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=db.func.now(),
    )

    organizer = relationship(
        "User",
        back_populates="events",
        foreign_keys=[organizer_id],
    )

    registration_fields = relationship(
        "EventRegistrationField",
        back_populates="event",
        cascade="all, delete-orphan",
        order_by="EventRegistrationField.sort_order",
    )

    registrations = relationship(
        "EventRegistration",
        back_populates="event",
        cascade="all, delete-orphan",
    )

    event_tags = relationship(
        "EventTag",
        back_populates="event",
        cascade="all, delete-orphan",
    )

    favorites = relationship(
        "Favorite",
        back_populates="event",
        cascade="all, delete-orphan",
    )

    reviews = relationship(
        "EventReview",
        back_populates="event",
        cascade="all, delete-orphan",
    )

    event_complaints = relationship(
        "EventComplaint",
        back_populates="event",
        cascade="all, delete-orphan",
    )

    notifications = relationship(
        "Notification",
        back_populates="event",
        foreign_keys="Notification.event_id",
    )

    __table_args__ = (
        CheckConstraint(
            "registration_type <> 'external' OR external_registration_url IS NOT NULL",
            name="ck_events_external_url_required",
        ),
        CheckConstraint(
            "price_type = 'free' OR price_value IS NOT NULL",
            name="ck_events_paid_price_required",
        ),
        CheckConstraint(
            "registration_type <> 'internal' OR registration_confirmation IS NOT NULL",
            name="ck_events_internal_confirmation_required",
        ),
        Index("ix_events_organizer_id", "organizer_id"),
        Index("ix_events_status", "status"),
        Index("ix_events_registration_type", "registration_type"),
        Index("ix_events_event_datetime", "event_datetime"),
        Index("ix_events_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Event id={self.id} title={self.title} status={self.status}>"