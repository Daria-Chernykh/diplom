from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from app.models import User


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


def get_current_user_from_token() -> User | None:
    user_id = get_jwt_identity()

    if user_id is None:
        return None

    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return None

    return User.query.filter(User.id == user_id).first()


def auth_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()

        user = get_current_user_from_token()

        if user is None:
            return error_response(401, "Пользователь не найден или токен недействителен.")

        if user.is_blocked:
            return error_response(403, "Учетная запись заблокирована.")

        return fn(user, *args, **kwargs)

    return wrapper


def legal_documents_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()

        user = get_current_user_from_token()

        if user is None:
            return error_response(401, "Пользователь не найден или токен недействителен.")

        if user.is_blocked:
            return error_response(403, "Учетная запись заблокирована.")

        if not user.legal_documents_accepted:
            return error_response(
                403,
                "Необходимо принять актуальные правовые документы.",
                {
                    "reason": "legal_documents_required",
                    "redirect_to": "/legal-acceptance",
                },
            )

        return fn(user, *args, **kwargs)

    return wrapper


def role_required(allowed_roles: set[str]):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()

            user = get_current_user_from_token()

            if user is None:
                return error_response(401, "Пользователь не найден или токен недействителен.")

            if user.is_blocked:
                return error_response(403, "Учетная запись заблокирована.")

            if not user.legal_documents_accepted:
                return error_response(
                    403,
                    "Необходимо принять актуальные правовые документы.",
                    {
                        "reason": "legal_documents_required",
                        "redirect_to": "/legal-acceptance",
                    },
                )

            if user.role not in allowed_roles:
                return error_response(403, "Недостаточно прав для выполнения действия.")

            return fn(user, *args, **kwargs)

        return wrapper

    return decorator


def participant_required(fn):
    return role_required({"user", "organizer", "admin"})(fn)


def organizer_required(fn):
    return role_required({"organizer", "admin"})(fn)


def admin_required(fn):
    return role_required({"admin"})(fn)


def blocked_user_forbidden(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()

        user = get_current_user_from_token()

        if user is None:
            return error_response(401, "Пользователь не найден или токен недействителен.")

        if user.is_blocked:
            return error_response(403, "Учетная запись заблокирована.")

        return fn(user, *args, **kwargs)

    return wrapper