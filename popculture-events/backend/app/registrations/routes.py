from io import BytesIO

from flask import Blueprint, jsonify, request, send_file

from app.auth.decorators import legal_documents_required, organizer_required
from app.registrations.schemas import (
    registration_field_to_dict,
    registration_to_dict,
    validate_registration_answers,
)
from app.registrations.services import (
    RegistrationError,
    approve_registration,
    build_participants_workbook,
    cancel_registration,
    confirm_external_registration,
    create_internal_registration,
    get_event_participants,
    get_event_registration_fields,
    get_user_event_registration,
    get_user_registration_archive,
    get_user_registrations,
    reject_registration,
)


registrations_bp = Blueprint("registrations", __name__)


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


@registrations_bp.get("/health")
def registrations_health():
    return success_response(
        {
            "module": "registrations",
            "message": "Модуль регистраций подключен.",
        }
    )


@registrations_bp.get("/events/<int:event_id>/fields")
@legal_documents_required
def event_registration_fields_route(user, event_id: int):
    fields = get_event_registration_fields(event_id)

    return success_response(
        {
            "fields": [registration_field_to_dict(field) for field in fields],
        }
    )


@registrations_bp.get("/events/<int:event_id>/status")
@legal_documents_required
def user_event_registration_status_route(user, event_id: int):
    registration = get_user_event_registration(user, event_id)

    return success_response(
        {
            "registration": registration_to_dict(registration) if registration else None,
        }
    )


@registrations_bp.post("/events/<int:event_id>/internal")
@legal_documents_required
def create_internal_registration_route(user, event_id: int):
    data = request.get_json(silent=True) or {}
    fields = get_event_registration_fields(event_id)

    try:
        answers = validate_registration_answers(fields, data.get("answers", {}))
        registration = create_internal_registration(user, event_id, answers)
    except ValueError as error:
        return error_response(400, "Ошибка заполнения регистрационной формы.", error.args[0])
    except RegistrationError as error:
        return error_response(error.status_code, error.message, error.details)

    return success_response(
        {
            "message": "Регистрация отправлена.",
            "registration": registration_to_dict(registration),
        },
        status_code=201,
    )


@registrations_bp.post("/events/<int:event_id>/external")
@legal_documents_required
def confirm_external_registration_route(user, event_id: int):
    try:
        registration = confirm_external_registration(user, event_id)
    except RegistrationError as error:
        return error_response(error.status_code, error.message, error.details)

    return success_response(
        {
            "message": "Внешняя регистрация подтверждена.",
            "registration": registration_to_dict(registration),
        }
    )


@registrations_bp.patch("/<int:registration_id>/cancel")
@legal_documents_required
def cancel_registration_route(user, registration_id: int):
    try:
        registration = cancel_registration(user, registration_id)
    except RegistrationError as error:
        return error_response(error.status_code, error.message, error.details)

    return success_response(
        {
            "message": "Регистрация отменена.",
            "registration": registration_to_dict(registration),
        }
    )


@registrations_bp.patch("/<int:registration_id>/approve")
@organizer_required
def approve_registration_route(user, registration_id: int):
    try:
        registration = approve_registration(user, registration_id)
    except RegistrationError as error:
        return error_response(error.status_code, error.message, error.details)

    return success_response(
        {
            "message": "Заявка подтверждена.",
            "registration": registration_to_dict(registration),
        }
    )


@registrations_bp.patch("/<int:registration_id>/reject")
@organizer_required
def reject_registration_route(user, registration_id: int):
    try:
        registration = reject_registration(user, registration_id)
    except RegistrationError as error:
        return error_response(error.status_code, error.message, error.details)

    return success_response(
        {
            "message": "Заявка отклонена.",
            "registration": registration_to_dict(registration),
        }
    )


@registrations_bp.get("/user")
@legal_documents_required
def user_registrations_route(user):
    registrations = get_user_registrations(user)

    return success_response(
        {
            "registrations": [registration_to_dict(registration) for registration in registrations],
        }
    )


@registrations_bp.get("/user/archive")
@legal_documents_required
def user_registration_archive_route(user):
    registrations = get_user_registration_archive(user)

    return success_response(
        {
            "registrations": [registration_to_dict(registration) for registration in registrations],
        }
    )


@registrations_bp.get("/events/<int:event_id>/participants")
@organizer_required
def event_participants_route(user, event_id: int):
    try:
        participants = get_event_participants(user, event_id)
    except RegistrationError as error:
        return error_response(error.status_code, error.message, error.details)

    return success_response(
        {
            "participants": [registration_to_dict(registration) for registration in participants],
        }
    )


@registrations_bp.get("/events/<int:event_id>/participants/export")
@organizer_required
def export_event_participants_route(user, event_id: int):
    try:
        workbook = build_participants_workbook(user, event_id)
    except RegistrationError as error:
        return error_response(error.status_code, error.message, error.details)

    output = BytesIO()
    workbook.save(output)
    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name=f"event_{event_id}_participants.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )