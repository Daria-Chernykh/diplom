from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(db.BigInteger, primary_key=True)

    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)

    role: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="user",
        server_default="user",
    )

    is_blocked: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=db.text("false"),
    )

    organization_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    organization_description: Mapped[str | None] = mapped_column(String(3000), nullable=True)

    legal_documents_accepted: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=db.text("false"),
    )

    legal_documents_accepted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    refresh_token: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=db.func.now(),
    )

    events = relationship(
        "Event",
        back_populates="organizer",
        cascade="all, delete-orphan",
        foreign_keys="Event.organizer_id",
    )

    registrations = relationship(
        "EventRegistration",
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="EventRegistration.user_id",
    )

    favorites = relationship(
        "Favorite",
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="Favorite.user_id",
    )

    event_reviews = relationship(
        "EventReview",
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="EventReview.user_id",
    )

    organizer_ratings_given = relationship(
        "OrganizerRating",
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="OrganizerRating.user_id",
    )

    organizer_ratings_received = relationship(
        "OrganizerRating",
        back_populates="organizer",
        cascade="all, delete-orphan",
        foreign_keys="OrganizerRating.organizer_id",
    )

    event_complaints = relationship(
        "EventComplaint",
        back_populates="reporter",
        cascade="all, delete-orphan",
        foreign_keys="EventComplaint.reporter_id",
    )

    review_complaints = relationship(
        "ReviewComplaint",
        back_populates="reporter",
        cascade="all, delete-orphan",
        foreign_keys="ReviewComplaint.reporter_id",
    )

    notifications = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="Notification.user_id",
    )

    uploaded_files = relationship(
        "File",
        back_populates="uploader",
        cascade="all, delete-orphan",
        foreign_keys="File.uploader_id",
    )

    __table_args__ = (
        Index("ix_users_email", "email"),
        Index("ix_users_role", "role"),
        Index("ix_users_is_blocked", "is_blocked"),
        Index("ix_users_legal_documents_accepted", "legal_documents_accepted"),
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} role={self.role}>"