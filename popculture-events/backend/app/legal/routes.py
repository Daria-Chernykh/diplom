from flask import Blueprint, jsonify, request, send_file

from app.auth.decorators import admin_required, blocked_user_forbidden
from app.legal.schemas import legal_document_to_dict
from app.legal.services import (
    LegalDocumentError,
    accept_legal_documents,
    get_actual_documents,
    get_document_file_path,
    update_legal_document,
)


legal_bp = Blueprint("legal", __name__)


def success_response(data: dict | None = None, status_code: int = 200):
    payload = {"success": True}

    if data is not None:
        payload.update(data)

    response = jsonify(payload)
    response.status_code = status_code

    return response


def error_response(status_code: int, message: str, details: dict | None = None):
    payload = {
        "success": False,
        "error": {
            "code": status_code,
            "message": message,
        },
    }

    if details is not None:
        payload["error"]["details"] = details

    response = jsonify(payload)
    response.status_code = status_code

    return response


@legal_bp.get("/health")
def legal_health():
    return success_response(
        {
            "module": "legal",
            "message": "Модуль правовых документов подключен.",
        }
    )


@legal_bp.get("/documents")
def legal_documents_route():
    documents = get_actual_documents()

    return success_response(
        {
            "documents": [legal_document_to_dict(document) for document in documents],
        }
    )


@legal_bp.get("/documents/<string:document_type>/download")
def legal_document_download_route(document_type: str):
    try:
        file_path = get_document_file_path(document_type)
    except LegalDocumentError as error:
        return error_response(error.status_code, error.message, error.details)

    return send_file(file_path, as_attachment=False)


@legal_bp.post("/accept")
@blocked_user_forbidden
def accept_legal_documents_route(user):
    data = request.get_json(silent=True) or {}

    try:
        accepted_user = accept_legal_documents(user, data)
    except LegalDocumentError as error:
        return error_response(error.status_code, error.message, error.details)

    return success_response(
        {
            "message": "Правовые документы приняты.",
            "user": {
                "id": accepted_user.id,
                "email": accepted_user.email,
                "role": accepted_user.role,
                "legal_documents_accepted": accepted_user.legal_documents_accepted,
                "legal_documents_accepted_at": accepted_user.legal_documents_accepted_at.isoformat()
                if accepted_user.legal_documents_accepted_at
                else None,
            },
        }
    )


@legal_bp.put("/documents/<string:document_type>")
@admin_required
def update_legal_document_route(user, document_type: str):
    file = request.files.get("file")

    try:
        document = update_legal_document(document_type, file)
    except LegalDocumentError as error:
        return error_response(error.status_code, error.message, error.details)

    return success_response(
        {
            "message": "Правовой документ обновлен.",
            "document": legal_document_to_dict(document),
        }
    )


@legal_bp.post("/admin/documents/<string:document_type>")
@admin_required
def update_legal_document_admin_alias_route(user, document_type: str):
    file = request.files.get("file")

    try:
        document = update_legal_document(document_type, file)
    except LegalDocumentError as error:
        return error_response(error.status_code, error.message, error.details)

    return success_response(
        {
            "message": "Правовой документ обновлен.",
            "document": legal_document_to_dict(document),
        }
    )
