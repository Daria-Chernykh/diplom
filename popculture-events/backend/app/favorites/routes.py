from flask import Blueprint, jsonify

from app.auth.decorators import legal_documents_required
from app.events.schemas import event_to_dict
from app.favorites.services import (
    FavoriteError,
    add_event_to_favorites,
    get_user_favorites,
    is_event_in_favorites,
    remove_event_from_favorites,
)
from app.organizers.services import calculate_organizer_rating

favorites_bp = Blueprint("favorites", __name__)


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


@favorites_bp.get("/health")
def favorites_health():
    return success_response(
        {
            "module": "favorites",
            "message": "Модуль избранного подключен.",
        }
    )


@favorites_bp.get("")
@legal_documents_required
def get_favorites_route(user):
    events = get_user_favorites(user)

    return success_response(
        {
            "events": [
                event_to_dict(
                    event,
                    calculate_organizer_rating(event.organizer_id),
                )
                for event in events
            ]
        }
    )


@favorites_bp.get("/<int:event_id>/status")
@legal_documents_required
def get_favorite_status_route(user, event_id: int):
    return success_response(
        {
            "event_id": event_id,
            "is_favorite": is_event_in_favorites(user, event_id),
        }
    )


@favorites_bp.post("/<int:event_id>")
@legal_documents_required
def add_favorite_route(user, event_id: int):
    try:
        add_event_to_favorites(user, event_id)
    except FavoriteError as error:
        return error_response(error.status_code, error.message, error.details)

    return success_response(
        {
            "message": "Мероприятие добавлено в избранное.",
            "event_id": event_id,
            "is_favorite": True,
        },
        status_code=201,
    )


@favorites_bp.delete("/<int:event_id>")
@legal_documents_required
def remove_favorite_route(user, event_id: int):
    try:
        remove_event_from_favorites(user, event_id)
    except FavoriteError as error:
        return error_response(error.status_code, error.message, error.details)

    return success_response(
        {
            "message": "Мероприятие удалено из избранного.",
            "event_id": event_id,
            "is_favorite": False,
        }
    )