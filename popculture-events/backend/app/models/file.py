from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class File(db.Model):
    __tablename__ = "files"

    id: Mapped[int] = mapped_column(db.BigInteger, primary_key=True)

    uploader_id: Mapped[int] = mapped_column(
        db.BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    entity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    entity_id: Mapped[int] = mapped_column(db.BigInteger, nullable=False, index=True)

    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)

    uploader = relationship(
        "User",
        back_populates="uploaded_files",
        foreign_keys=[uploader_id],
    )

    __table_args__ = (
        Index("ix_files_entity", "entity_type", "entity_id"),
    )

    def __repr__(self) -> str:
        return f"<File id={self.id} entity_type={self.entity_type} entity_id={self.entity_id}>"