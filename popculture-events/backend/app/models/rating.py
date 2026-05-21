from sqlalchemy import CheckConstraint, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class OrganizerRating(db.Model):
    __tablename__ = "organizer_ratings"

    id: Mapped[int] = mapped_column(db.BigInteger, primary_key=True)

    organizer_id: Mapped[int] = mapped_column(
        db.BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    user_id: Mapped[int] = mapped_column(
        db.BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    rating: Mapped[int] = mapped_column(db.SmallInteger, nullable=False)

    organizer = relationship(
        "User",
        back_populates="organizer_ratings_received",
        foreign_keys=[organizer_id],
    )

    user = relationship(
        "User",
        back_populates="organizer_ratings_given",
        foreign_keys=[user_id],
    )

    __table_args__ = (
        CheckConstraint("rating >= 0 AND rating <= 5", name="ck_organizer_ratings_rating_range"),
        UniqueConstraint("organizer_id", "user_id", name="uq_organizer_ratings_organizer_user"),
        Index("ix_organizer_ratings_organizer_id", "organizer_id"),
        Index("ix_organizer_ratings_user_id", "user_id"),
        Index("ix_organizer_ratings_rating", "rating"),
    )

    def __repr__(self) -> str:
        return (
            f"<OrganizerRating id={self.id} "
            f"organizer_id={self.organizer_id} "
            f"user_id={self.user_id} "
            f"rating={self.rating}>"
        )