from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class EventRegistrationField(db.Model):
    __tablename__ = "event_registration_fields"

    id: Mapped[int] = mapped_column(db.BigInteger, primary_key=True)

    event_id: Mapped[int] = mapped_column(
        db.BigInteger,
        ForeignKey("events.id", ondelete="CASCADE"),
        nullable=False,
    )

    field_name: Mapped[str] = mapped_column(String(150), nullable=False)

    field_type: Mapped[str] = mapped_column(
        Enum(
            "text",
            "email",
            "phone",
            "number",
            "date",
            "select",
            "textarea",
            "checkbox",
            name="registration_field_type",
        ),
        nullable=False,
    )

    is_required: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=db.text("true"),
    )

    sort_order: Mapped[int] = mapped_column(
        db.Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    options: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    event = relationship("Event", back_populates="registration_fields")

    __table_args__ = (
        Index("ix_event_registration_fields_event_id", "event_id"),
        Index("ix_event_registration_fields_sort_order", "sort_order"),
    )

    def __repr__(self) -> str:
        return f"<EventRegistrationField id={self.id} event_id={self.event_id} name={self.field_name}>"


class EventRegistration(db.Model):
    __tablename__ = "event_registrations"

    id: Mapped[int] = mapped_column(db.BigInteger, primary_key=True)

    event_id: Mapped[int] = mapped_column(
        db.BigInteger,
        ForeignKey("events.id", ondelete="CASCADE"),
        nullable=False,
    )

    user_id: Mapped[int] = mapped_column(
        db.BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        Enum("pending", "registered", "rejected", "canceled", name="registration_status"),
        nullable=False,
    )

    answers: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default=db.text("'{}'::jsonb"),
    )

    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=db.func.now(),
    )

    event = relationship("Event", back_populates="registrations")
    user = relationship("User", back_populates="registrations")

    __table_args__ = (
        UniqueConstraint("event_id", "user_id", name="uq_event_registrations_event_user"),
        Index("ix_event_registrations_event_id", "event_id"),
        Index("ix_event_registrations_user_id", "user_id"),
        Index("ix_event_registrations_status", "status"),
        Index("ix_event_registrations_submitted_at", "submitted_at"),
    )

    def __repr__(self) -> str:
        return f"<EventRegistration id={self.id} event_id={self.event_id} user_id={self.user_id} status={self.status}>"