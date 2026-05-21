from flask import Blueprint, jsonify, request

from app.auth.decorators import admin_required
from app.events.schemas import event_to_dict
from app.organizers.services import (
    OrganizerError,
    get_admin_organizers,
    get_organizer_events,
    get_organizer_or_404,
    get_public_organizers,
    organizer_to_dict,
    set_organizer_blocked,
)

organizers_bp = Blueprint("organizers", __name__)


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


@organizers_bp.get("/health")
def organizers_health():
    return success_response(
        {
            "module": "organizers",
            "message": "Модуль организаторов подключен.",
        }
    )


@organizers_bp.get("")
def list_public_organizers_route():
    organizers = get_public_organizers()

    return success_response(
        {
            "organizers": [organizer_to_dict(organizer) for organizer in organizers],
        }
    )


@organizers_bp.get("/<int:organizer_id>")
def get_public_organizer_route(organizer_id: int):
    try:
        organizer = get_organizer_or_404(organizer_id)
    except OrganizerError as error:
        return error_response(error.status_code, error.message, error.details)

    events = get_organizer_events(organizer.id, status="published")
    archived_events = get_organizer_events(organizer.id, status="archived")

    return success_response(
        {
            "organizer": organizer_to_dict(organizer),
            "events": [event_to_dict(event) for event in events],
            "archived_events": [event_to_dict(event) for event in archived_events],
        }
    )


@organizers_bp.get("/admin")
@admin_required
def admin_list_organizers_route(user):
    query = request.args.get("query", "").strip().lower()

    organizers = get_admin_organizers()

    if query:
        organizers = [
            organizer
            for organizer in organizers
            if query in (organizer.full_name or "").lower()
            or query in (organizer.email or "").lower()
            or query in (organizer.organization_name or "").lower()
        ]

    return success_response(
        {
            "organizers": [organizer_to_dict(organizer) for organizer in organizers],
        }
    )


@organizers_bp.patch("/admin/<int:organizer_id>/block")
@admin_required
def admin_block_organizer_route(user, organizer_id: int):
    if user.id == organizer_id:
        return error_response(400, "Администратор не может заблокировать свою учетную запись.")

    try:
        organizer = set_organizer_blocked(organizer_id, True)
    except OrganizerError as error:
        return error_response(error.status_code, error.message, error.details)

    return success_response(
        {
            "message": "Организатор заблокирован.",
            "organizer": organizer_to_dict(organizer),
        }
    )


@organizers_bp.patch("/admin/<int:organizer_id>/unblock")
@admin_required
def admin_unblock_organizer_route(user, organizer_id: int):
    try:
        organizer = set_organizer_blocked(organizer_id, False)
    except OrganizerError as error:
        return error_response(error.status_code, error.message, error.details)

    return success_response(
        {
            "message": "Организатор разблокирован.",
            "organizer": organizer_to_dict(organizer),
        }
    )