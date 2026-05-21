from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.auth.decorators import blocked_user_forbidden
from app.auth.services import (
    AuthError,
    accept_legal_documents_for_user,
    authenticate_user,
    clear_refresh_token,
    create_user,
    refresh_user_tokens,
    user_to_auth_dict,
)

auth_bp = Blueprint("auth", __name__)


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


@auth_bp.get("/health")
def auth_health():
    return success_response(
        {
            "module": "auth",
            "message": "Модуль авторизации подключен.",
        }
    )


@auth_bp.post("/register")
def register_route():
    data = request.get_json(silent=True) or {}

    try:
        result = create_user(data)
    except AuthError as error:
        return error_response(error.status_code, error.message, error.details)

    return success_response(result, status_code=201)


@auth_bp.post("/login")
def login_route():
    data = request.get_json(silent=True) or {}

    try:
        result = authenticate_user(data)
    except AuthError as error:
        return error_response(error.status_code, error.message, error.details)

    return success_response(result)


@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh_route():
    user_id = get_jwt_identity()
    refresh_token = request.headers.get("Authorization", "").replace("Bearer ", "").strip()

    try:
        result = refresh_user_tokens(user_id, refresh_token)
    except AuthError as error:
        return error_response(error.status_code, error.message, error.details)

    return success_response(result)


@auth_bp.post("/logout")
@blocked_user_forbidden
def logout_route(user):
    clear_refresh_token(user)

    return success_response(
        {
            "message": "Выход выполнен.",
        }
    )


@auth_bp.get("/me")
@blocked_user_forbidden
def current_user_route(user):
    return success_response(
        {
            "user": user_to_auth_dict(user),
        }
    )


@auth_bp.post("/accept-legal-documents")
@blocked_user_forbidden
def accept_legal_documents_route(user):
    data = request.get_json(silent=True) or {}

    try:
        updated_user = accept_legal_documents_for_user(user, data)
    except AuthError as error:
        return error_response(error.status_code, error.message, error.details)

    return success_response(
        {
            "message": "Правовые документы приняты.",
            "user": user_to_auth_dict(updated_user),
        }
    )
