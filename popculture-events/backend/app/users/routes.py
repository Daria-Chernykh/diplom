from flask import Blueprint, jsonify, request

from app.auth.decorators import admin_required, blocked_user_forbidden
from app.users.services import (
    UserError,
    change_password,
    get_users,
    set_user_blocked,
    update_profile,
    user_to_dict,
)

users_bp = Blueprint("users", __name__)


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


@users_bp.get("/health")
def users_health():
    return success_response(
        {
            "module": "users",
            "message": "Модуль пользователей подключен.",
        }
    )


@users_bp.get("/profile")
@blocked_user_forbidden
def get_profile_route(user):
    return success_response(
        {
            "user": user_to_dict(user),
        }
    )


@users_bp.put("/profile")
@blocked_user_forbidden
def update_profile_route(user):
    data = request.get_json(silent=True) or {}

    try:
        updated_user = update_profile(user, data)
    except UserError as error:
        return error_response(error.status_code, error.message, error.details)

    return success_response(
        {
            "message": "Профиль обновлен.",
            "user": user_to_dict(updated_user),
        }
    )


@users_bp.put("/password")
@blocked_user_forbidden
def change_password_route(user):
    data = request.get_json(silent=True) or {}

    try:
        change_password(user, data)
    except UserError as error:
        return error_response(error.status_code, error.message, error.details)

    return success_response(
        {
            "message": "Пароль изменен.",
        }
    )


@users_bp.get("")
@admin_required
def admin_users_route(user):
    query = request.args.get("q", "").strip().lower()
    role = request.args.get("role", "").strip()
    blocked = request.args.get("blocked", "").strip()

    users = get_users()

    if query:
        users = [
            current_user
            for current_user in users
            if query in (current_user.email or "").lower()
            or query in (current_user.full_name or "").lower()
            or query in (current_user.organization_name or "").lower()
        ]

    if role:
        users = [current_user for current_user in users if current_user.role == role]

    if blocked == "true":
        users = [current_user for current_user in users if current_user.is_blocked]

    if blocked == "false":
        users = [current_user for current_user in users if not current_user.is_blocked]

    return success_response(
        {
            "users": [user_to_dict(current_user) for current_user in users],
        }
    )


@users_bp.patch("/<int:user_id>/block")
@admin_required
def block_user_route(user, user_id: int):
    try:
        updated_user = set_user_blocked(user_id, True)
    except UserError as error:
        return error_response(error.status_code, error.message, error.details)

    return success_response(
        {
            "message": "Пользователь заблокирован.",
            "user": user_to_dict(updated_user),
        }
    )


@users_bp.patch("/<int:user_id>/unblock")
@admin_required
def unblock_user_route(user, user_id: int):
    try:
        updated_user = set_user_blocked(user_id, False)
    except UserError as error:
        return error_response(error.status_code, error.message, error.details)

    return success_response(
        {
            "message": "Пользователь разблокирован.",
            "user": user_to_dict(updated_user),
        }
    )