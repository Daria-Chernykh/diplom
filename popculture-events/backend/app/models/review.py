from datetime import datetime, timezone

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Index, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class EventReview(db.Model):
    __tablename__ = "event_reviews"

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

    rating: Mapped[int] = mapped_column(db.SmallInteger, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    is_hidden: Mapped[bool] = mapped_column(
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

    event = relationship("Event", back_populates="reviews")
    user = relationship("User", back_populates="event_reviews")

    review_complaints = relationship(
        "ReviewComplaint",
        back_populates="review",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        CheckConstraint("rating >= 0 AND rating <= 5", name="ck_event_reviews_rating_range"),
        UniqueConstraint("event_id", "user_id", name="uq_event_reviews_event_user"),
        Index("ix_event_reviews_event_id", "event_id"),
        Index("ix_event_reviews_user_id", "user_id"),
        Index("ix_event_reviews_rating", "rating"),
        Index("ix_event_reviews_is_hidden", "is_hidden"),
        Index("ix_event_reviews_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<EventReview id={self.id} event_id={self.event_id} user_id={self.user_id} rating={self.rating}>"