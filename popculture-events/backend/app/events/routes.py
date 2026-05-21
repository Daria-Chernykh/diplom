from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from app.auth.decorators import legal_documents_required, organizer_required
from app.events.schemas import event_to_dict, validate_event_payload
from app.events.services import (
    EventError,
    archive_finished_events,
    create_event,
    get_event_by_id,
    get_events,
    get_organizer_event,
    get_organizer_events,
    update_event,
)
from app.models import User


events_bp = Blueprint("events", __name__)


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


def get_optional_current_user():
    try:
        verify_jwt_in_request(optional=True)
    except Exception:
        return None

    user_id = get_jwt_identity()

    if not user_id:
        return None

    return User.query.filter(User.id == int(user_id)).first()


@events_bp.get("/health")
def events_health():
    return success_response(
        {
            "module": "events",
            "message": "Модуль мероприятий подключен.",
        }
    )


@events_bp.get("")
def public_events_route():
    archive_finished_events()

    query = request.args.get("q", "").strip()
    tag = request.args.get("tag", "").strip()
    registration_type = request.args.get("registration_type", "").strip()
    event_format = request.args.get("event_format", "").strip()

    events = get_events(
        query=query,
        tag=tag,
        registration_type=registration_type,
        event_format=event_format,
    )

    current_user = get_optional_current_user()

    return success_response(
        {
            "events": [event_to_dict(event, current_user) for event in events],
        }
    )


@events_bp.get("/<int:event_id>")
def public_event_route(event_id: int):
    archive_finished_events()
    current_user = get_optional_current_user()

    try:
        event = get_event_by_id(event_id, current_user)
    except EventError as error:
        return error_response(error.status_code, error.message, error.details)

    return success_response(
        {
            "event": event_to_dict(event, current_user),
        }
    )


@events_bp.post("")
@organizer_required
def create_event_route(user):
    data = request.get_json(silent=True) or {}

    try:
        payload = validate_event_payload(data, is_create=True)
        event = create_event(user, payload)
    except ValueError as error:
        return error_response(400, "Ошибка заполнения формы мероприятия.", error.args[0])
    except EventError as error:
        return error_response(error.status_code, error.message, error.details)

    return success_response(
        {
            "message": "Мероприятие создано.",
            "event": event_to_dict(event, user),
        },
        status_code=201,
    )


@events_bp.get("/organizer")
@organizer_required
def organizer_events_route(user):
    archive_finished_events()

    status = request.args.get("status", "").strip()
    events = get_organizer_events(user, status=status)

    return success_response(
        {
            "events": [event_to_dict(event, user) for event in events],
        }
    )


@events_bp.get("/organizer/<int:event_id>")
@organizer_required
def organizer_event_route(user, event_id: int):
    try:
        event = get_organizer_event(user, event_id)
    except EventError as error:
        return error_response(error.status_code, error.message, error.details)

    return success_response(
        {
            "event": event_to_dict(event, user),
        }
    )


@events_bp.put("/organizer/<int:event_id>")
@organizer_required
def update_event_route(user, event_id: int):
    data = request.get_json(silent=True) or {}

    try:
        payload = validate_event_payload(data, is_create=False)
        payload["send_to_admin"] = bool(data.get("send_to_admin", False))
        event = update_event(user, event_id, payload)
    except ValueError as error:
        return error_response(400, "Ошибка заполнения формы мероприятия.", error.args[0])
    except EventError as error:
        return error_response(error.status_code, error.message, error.details)

    return success_response(
        {
            "message": "Мероприятие обновлено.",
            "event": event_to_dict(event, user),
        }
    )


@events_bp.post("/archive-finished")
@legal_documents_required
def archive_finished_events_route(user):
    archived_count = archive_finished_events()

    return success_response(
        {
            "message": "Архивные состояния обновлены.",
            "archived_count": archived_count,
        }
    )