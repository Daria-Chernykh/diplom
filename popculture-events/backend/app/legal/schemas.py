from app.models import LegalDocument


DOCUMENT_TYPE_LABELS = {
    "user_agreement": "Пользовательское соглашение",
    "privacy_policy": "Политика обработки персональных данных",
    "personal_data_consent": "Согласие на обработку персональных данных",
}

REQUIRED_DOCUMENT_TYPES = {
    "user_agreement",
    "privacy_policy",
    "personal_data_consent",
}


def validate_document_type(document_type: str) -> str:
    normalized_document_type = str(document_type or "").strip()

    if normalized_document_type not in REQUIRED_DOCUMENT_TYPES:
        raise ValueError(
            {
                "document_type": "Недопустимый тип правового документа.",
                "allowed_values": sorted(REQUIRED_DOCUMENT_TYPES),
            }
        )

    return normalized_document_type


def legal_document_to_dict(document: LegalDocument) -> dict:
    return {
        "id": document.id,
        "document_type": document.document_type,
        "title": DOCUMENT_TYPE_LABELS.get(document.document_type, document.document_type),
        "version": document.version,
        "file_path": document.file_path,
        "download_url": f"/api/legal/documents/{document.document_type}/download",
        "uploaded_at": document.uploaded_at.isoformat() if document.uploaded_at else None,
    }