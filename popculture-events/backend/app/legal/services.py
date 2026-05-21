from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from flask import current_app
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import LegalDocument, User


ALLOWED_LEGAL_DOCUMENT_TYPES = {
    "user_agreement",
    "privacy_policy",
    "personal_data_consent",
}

ALLOWED_LEGAL_DOCUMENT_EXTENSIONS = {
    ".pdf",
}


class LegalDocumentError(Exception):
    def __init__(self, message: str, status_code: int = 400, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details


def validate_document_type(document_type: str) -> None:
    if document_type not in ALLOWED_LEGAL_DOCUMENT_TYPES:
        raise LegalDocumentError(
            "Недопустимый тип правового документа.",
            status_code=400,
            details={
                "document_type": (
                    "Допустимые значения: user_agreement, privacy_policy, personal_data_consent."
                )
            },
        )


def validate_legal_confirmations(data: dict) -> None:
    errors = {}

    if not bool(data.get("user_agreement_accepted")):
        errors["user_agreement_accepted"] = "Необходимо принять Пользовательское соглашение."

    if not bool(data.get("privacy_policy_acknowledged")):
        errors["privacy_policy_acknowledged"] = "Необходимо подтвердить ознакомление с Политикой обработки персональных данных."

    if not bool(data.get("personal_data_consent_given")):
        errors["personal_data_consent_given"] = "Необходимо отдельно дать согласие на обработку персональных данных."

    if errors:
        raise LegalDocumentError(
            "Необходимо выполнить все правовые подтверждения.",
            status_code=400,
            details=errors,
        )


def get_legal_documents_upload_dir() -> Path:
    upload_folder = current_app.config.get("UPLOAD_FOLDER", "uploads")
    upload_dir = Path(upload_folder) / "legal_documents"
    upload_dir.mkdir(parents=True, exist_ok=True)

    return upload_dir


def get_actual_documents() -> list[LegalDocument]:
    return (
        LegalDocument.query
        .order_by(LegalDocument.document_type.asc())
        .all()
    )


def get_actual_document(document_type: str) -> LegalDocument:
    validate_document_type(document_type)

    document = (
        LegalDocument.query
        .filter(LegalDocument.document_type == document_type)
        .first()
    )

    if document is None:
        raise LegalDocumentError(
            "Правовой документ не найден.",
            status_code=404,
        )

    return document


def get_document_file_path(document_type: str) -> Path:
    document = get_actual_document(document_type)

    upload_folder = current_app.config.get("UPLOAD_FOLDER", "uploads")
    file_path = Path(upload_folder) / document.file_path

    if not file_path.exists() or not file_path.is_file():
        raise LegalDocumentError(
            "Файл правового документа не найден.",
            status_code=404,
        )

    return file_path


def validate_uploaded_document(file: FileStorage | None) -> None:
    if file is None:
        raise LegalDocumentError(
            "Файл документа обязателен для загрузки.",
            status_code=400,
            details={"file": "Выберите файл правового документа."},
        )

    if not file.filename:
        raise LegalDocumentError(
            "Файл документа обязателен для загрузки.",
            status_code=400,
            details={"file": "Выберите файл правового документа."},
        )

    original_filename = secure_filename(file.filename)
    extension = Path(original_filename).suffix.lower()

    if extension not in ALLOWED_LEGAL_DOCUMENT_EXTENSIONS:
        raise LegalDocumentError(
            "Недопустимый формат правового документа.",
            status_code=400,
            details={
                "file": "Разрешены только файлы PDF.",
            },
        )


def delete_old_document_file(document: LegalDocument) -> None:
    if not document.file_path:
        return

    upload_folder = current_app.config.get("UPLOAD_FOLDER", "uploads")
    file_path = Path(upload_folder) / document.file_path

    if file_path.exists() and file_path.is_file():
        file_path.unlink()


def save_legal_document_file(document_type: str, file: FileStorage) -> str:
    upload_dir = get_legal_documents_upload_dir()

    original_filename = secure_filename(file.filename)
    extension = Path(original_filename).suffix.lower()
    stored_filename = f"{document_type}_{uuid4().hex}{extension}"
    stored_path = upload_dir / stored_filename

    file.save(stored_path)

    return str(Path("legal_documents") / stored_filename).replace("\\", "/")


def update_legal_document(document_type: str, file: FileStorage | None) -> LegalDocument:
    validate_document_type(document_type)
    validate_uploaded_document(file)

    document = (
        LegalDocument.query
        .filter(LegalDocument.document_type == document_type)
        .first()
    )

    if document is not None:
        delete_old_document_file(document)

    relative_path = save_legal_document_file(document_type, file)

    if document is None:
        document = LegalDocument(
            document_type=document_type,
            file_path=relative_path,
            version=1,
            uploaded_at=datetime.now(timezone.utc),
        )
        db.session.add(document)
    else:
        document.file_path = relative_path
        document.version = document.version + 1
        document.uploaded_at = datetime.now(timezone.utc)

    User.query.update(
        {
            User.legal_documents_accepted: False,
            User.legal_documents_accepted_at: None,
        },
        synchronize_session=False,
    )

    db.session.commit()

    return document


def accept_legal_documents(user: User, data: dict) -> User:
    actual_documents = get_actual_documents()

    if len(actual_documents) == 0:
        raise LegalDocumentError(
            "Правовые документы еще не загружены.",
            status_code=400,
        )

    validate_legal_confirmations(data)

    user.legal_documents_accepted = True
    user.legal_documents_accepted_at = datetime.now(timezone.utc)

    db.session.commit()

    return user
