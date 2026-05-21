from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class Favorite(db.Model):
    __tablename__ = "favorites"

    user_id: Mapped[int] = mapped_column(
        db.BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )

    event_id: Mapped[int] = mapped_column(
        db.BigInteger,
        ForeignKey("events.id", ondelete="CASCADE"),
        primary_key=True,
    )

    user = relationship("User", back_populates="favorites")
    event = relationship("Event", back_populates="favorites")

    __table_args__ = (
        Index("ix_favorites_user_id", "user_id"),
        Index("ix_favorites_event_id", "event_id"),
    )

    def __repr__(self) -> str:
        return f"<Favorite user_id={self.user_id} event_id={self.event_id}>"