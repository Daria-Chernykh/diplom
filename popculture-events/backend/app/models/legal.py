from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, DateTime, Enum, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db


class LegalDocument(db.Model):
    __tablename__ = "legal_documents"

    id: Mapped[int] = mapped_column(db.BigInteger, primary_key=True)

    document_type: Mapped[str] = mapped_column(
        Enum(
            "user_agreement",
            "privacy_policy",
            "personal_data_consent",
            name="legal_document_type",
        ),
        nullable=False,
        unique=True,
    )

    version: Mapped[int] = mapped_column(
        db.Integer,
        nullable=False,
        default=1,
        server_default="1",
    )

    file_path: Mapped[str] = mapped_column(String(1000), nullable=False)

    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=db.func.now(),
    )

    __table_args__ = (
        CheckConstraint("version > 0", name="ck_legal_documents_version_positive"),
        Index("ix_legal_documents_document_type", "document_type"),
        Index("ix_legal_documents_uploaded_at", "uploaded_at"),
    )

    def __repr__(self) -> str:
        return f"<LegalDocument id={self.id} type={self.document_type} version={self.version}>"