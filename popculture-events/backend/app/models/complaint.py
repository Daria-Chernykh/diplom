from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class EventComplaint(db.Model):
    __tablename__ = "event_complaints"

    id: Mapped[int] = mapped_column(db.BigInteger, primary_key=True)

    event_id: Mapped[int] = mapped_column(
        db.BigInteger,
        ForeignKey("events.id", ondelete="CASCADE"),
        nullable=False,
    )

    reporter_id: Mapped[int] = mapped_column(
        db.BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    complaint_type: Mapped[str] = mapped_column(
        Enum(
            "misinformation",
            "fraud",
            "prohibited_content",
            "duplicate",
            "other",
            name="event_complaint_type",
        ),
        nullable=False,
    )

    comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    organizer_comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    last_changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=db.func.now(),
    )

    event = relationship("Event", back_populates="event_complaints")
    reporter = relationship("User", back_populates="event_complaints")

    __table_args__ = (
        UniqueConstraint("event_id", "reporter_id", name="uq_event_complaints_event_reporter"),
        Index("ix_event_complaints_event_id", "event_id"),
        Index("ix_event_complaints_reporter_id", "reporter_id"),
        Index("ix_event_complaints_complaint_type", "complaint_type"),
        Index("ix_event_complaints_last_changed_at", "last_changed_at"),
    )

    def __repr__(self) -> str:
        return f"<EventComplaint id={self.id} event_id={self.event_id} reporter_id={self.reporter_id}>"


class ReviewComplaint(db.Model):
    __tablename__ = "review_complaints"

    id: Mapped[int] = mapped_column(db.BigInteger, primary_key=True)

    review_id: Mapped[int] = mapped_column(
        db.BigInteger,
        ForeignKey("event_reviews.id", ondelete="CASCADE"),
        nullable=False,
    )

    reporter_id: Mapped[int] = mapped_column(
        db.BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    last_changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=db.func.now(),
    )

    review = relationship("EventReview", back_populates="review_complaints")
    reporter = relationship("User", back_populates="review_complaints")

    __table_args__ = (
        UniqueConstraint("review_id", "reporter_id", name="uq_review_complaints_review_reporter"),
        Index("ix_review_complaints_review_id", "review_id"),
        Index("ix_review_complaints_reporter_id", "reporter_id"),
        Index("ix_review_complaints_last_changed_at", "last_changed_at"),
    )

    def __repr__(self) -> str:
        return f"<ReviewComplaint id={self.id} review_id={self.review_id} reporter_id={self.reporter_id}>"