from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class Tag(db.Model):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(db.BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)

    event_tags = relationship(
        "EventTag",
        back_populates="tag",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_tags_name", "name"),
    )

    def __repr__(self) -> str:
        return f"<Tag id={self.id} name={self.name}>"


class EventTag(db.Model):
    __tablename__ = "event_tags"

    event_id: Mapped[int] = mapped_column(
        db.BigInteger,
        ForeignKey("events.id", ondelete="CASCADE"),
        primary_key=True,
    )

    tag_id: Mapped[int] = mapped_column(
        db.BigInteger,
        ForeignKey("tags.id", ondelete="CASCADE"),
        primary_key=True,
    )

    event = relationship("Event", back_populates="event_tags")
    tag = relationship("Tag", back_populates="event_tags")

    __table_args__ = (
        Index("ix_event_tags_event_id", "event_id"),
        Index("ix_event_tags_tag_id", "tag_id"),
    )

    def __repr__(self) -> str:
        return f"<EventTag event_id={self.event_id} tag_id={self.tag_id}>"