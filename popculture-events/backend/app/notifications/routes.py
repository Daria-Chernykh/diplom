from flask import Blueprint, jsonify, request

from app.auth.decorators import legal_documents_required
from app.notifications.schemas import notification_to_dict
from app.notifications.services import (
    NotificationError,
    delete_all_notifications,
    delete_notification,
    get_unread_count,
    get_user_notifications,
    mark_all_notifications_read,
    mark_notification_read,
)


notifications_bp = Blueprint("notifications", __name__)


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


@notifications_bp.get("/health")
def notifications_health():
    return success_response(
        {
            "module": "notifications",
            "message": "Модуль уведомлений подключен.",
        }
    )


@notifications_bp.get("")
@legal_documents_required
def notifications_list_route(user):
    only_unread = request.args.get("unread", "").lower() == "true"
    notifications = get_user_notifications(user, only_unread=only_unread)

    return success_response(
        {
            "notifications": [notification_to_dict(notification) for notification in notifications],
            "unread_count": get_unread_count(user),
        }
    )


@notifications_bp.patch("/<int:notification_id>/read")
@legal_documents_required
def mark_notification_read_route(user, notification_id: int):
    try:
        notification = mark_notification_read(user, notification_id)
    except NotificationError as error:
        return error_response(error.status_code, error.message, error.details)

    return success_response(
        {
            "message": "Уведомление отмечено как прочитанное.",
            "notification": notification_to_dict(notification),
            "unread_count": get_unread_count(user),
        }
    )


@notifications_bp.patch("/read-all")
@legal_documents_required
def mark_all_notifications_read_route(user):
    count = mark_all_notifications_read(user)

    return success_response(
        {
            "message": "Все уведомления отмечены как прочитанные.",
            "updated_count": count,
            "unread_count": get_unread_count(user),
        }
    )


@notifications_bp.delete("/<int:notification_id>")
@legal_documents_required
def delete_notification_route(user, notification_id: int):
    try:
        delete_notification(user, notification_id)
    except NotificationError as error:
        return error_response(error.status_code, error.message, error.details)

    return success_response(
        {
            "message": "Уведомление удалено.",
            "unread_count": get_unread_count(user),
        }
    )


@notifications_bp.delete("")
@legal_documents_required
def delete_all_notifications_route(user):
    count = delete_all_notifications(user)

    return success_response(
        {
            "message": "Уведомления удалены.",
            "deleted_count": count,
            "unread_count": 0,
        }
    )