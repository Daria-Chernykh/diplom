from pathlib import Path

from flask import Blueprint, jsonify, request, send_from_directory

from app.auth.decorators import legal_documents_required
from app.files.schemas import file_to_dict
from app.files.services import (
    FileError,
    delete_file_by_user,
    get_entity_files,
    get_entity_single_file,
    get_upload_root,
    save_event_image,
    save_organizer_profile_image,
    save_user_profile_image,
)

files_bp = Blueprint("files", __name__)


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


@files_bp.get("/health")
def files_health():
    return success_response(
        {
            "module": "files",
            "message": "Модуль файлов подключен.",
        }
    )


@files_bp.get("/view/<path:relative_path>")
def view_file_route(relative_path: str):
    upload_root = get_upload_root()
    absolute_path = upload_root / relative_path

    if not absolute_path.exists():
        return error_response(404, "Файл не найден.")

    directory = Path(absolute_path).parent
    filename = Path(absolute_path).name

    return send_from_directory(directory, filename)


@files_bp.get("/entities/<string:entity_type>/<int:entity_id>")
def get_entity_files_route(entity_type: str, entity_id: int):
    files = get_entity_files(entity_type, entity_id)

    return success_response(
        {
            "files": [file_to_dict(file) for file in files],
        }
    )


@files_bp.get("/entities/<string:entity_type>/<int:entity_id>/main")
def get_entity_single_file_route(entity_type: str, entity_id: int):
    file = get_entity_single_file(entity_type, entity_id)

    return success_response(
        {
            "file": file_to_dict(file) if file else None,
        }
    )


@files_bp.post("/events/<int:event_id>/image")
@legal_documents_required
def upload_event_image_route(user, event_id: int):
    uploaded_file = request.files.get("file")

    try:
        file = save_event_image(user, event_id, uploaded_file)
    except FileError as error:
        return error_response(error.status_code, error.message, error.details)

    return success_response(
        {
            "message": "Изображение мероприятия загружено.",
            "file": file_to_dict(file),
        },
        status_code=201,
    )


@files_bp.post("/profile-image")
@legal_documents_required
def upload_user_profile_image_route(user):
    uploaded_file = request.files.get("file")

    try:
        file = save_user_profile_image(user, uploaded_file)
    except FileError as error:
        return error_response(error.status_code, error.message, error.details)

    return success_response(
        {
            "message": "Изображение профиля загружено.",
            "file": file_to_dict(file),
        },
        status_code=201,
    )


@files_bp.post("/organizer-image")
@legal_documents_required
def upload_organizer_profile_image_route(user):
    uploaded_file = request.files.get("file")

    try:
        file = save_organizer_profile_image(user, uploaded_file)
    except FileError as error:
        return error_response(error.status_code, error.message, error.details)

    return success_response(
        {
            "message": "Изображение организатора загружено.",
            "file": file_to_dict(file),
        },
        status_code=201,
    )


@files_bp.delete("/<int:file_id>")
@legal_documents_required
def delete_file_route(user, file_id: int):
    try:
        delete_file_by_user(user, file_id)
    except FileError as error:
        return error_response(error.status_code, error.message, error.details)

    return success_response(
        {
            "message": "Файл удален.",
        }
    )