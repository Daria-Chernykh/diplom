from datetime import datetime

from flask_jwt_extended import create_access_token, create_refresh_token
from werkzeug.security import check_password_hash, generate_password_hash

from app.common.validators import (
    validate_choice,
    validate_email,
    validate_password,
    validate_required_string,
)
from app.extensions import db
from app.models import User


class AuthError(Exception):
    def __init__(self, message: str, status_code: int = 400, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details


def user_to_auth_dict(user: User) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "is_blocked": user.is_blocked,
        "organization_name": user.organization_name,
        "organization_description": user.organization_description,
        "legal_documents_accepted": user.legal_documents_accepted,
        "legal_documents_accepted_at": user.legal_documents_accepted_at.isoformat()
        if user.legal_documents_accepted_at
        else None,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }


def create_tokens_for_user(user: User) -> dict:
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    user.refresh_token = refresh_token
    db.session.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


def validate_legal_confirmations(data: dict) -> None:
    errors = {}

    if not bool(data.get("user_agreement_accepted")):
        errors["user_agreement_accepted"] = "Необходимо принять Пользовательское соглашение."

    if not bool(data.get("privacy_policy_acknowledged")):
        errors["privacy_policy_acknowledged"] = "Необходимо подтвердить ознакомление с Политикой обработки персональных данных."

    if not bool(data.get("personal_data_consent_given")):
        errors["personal_data_consent_given"] = "Необходимо отдельно дать согласие на обработку персональных данных."

    if errors:
        raise AuthError("Необходимо выполнить все правовые подтверждения.", status_code=400, details=errors)


def validate_registration_payload(data: dict) -> dict:
    errors = {}

    email = validate_email(data, "email", errors)
    password = validate_password(data, "password", errors)
    full_name = validate_required_string(data, "full_name", "Имя пользователя", errors, max_length=255)
    role = validate_choice(data, "role", "Тип учетной записи", {"user", "organizer"}, errors)

    organization_name = str(data.get("organization_name", "")).strip()
    organization_description = str(data.get("organization_description", "")).strip()

    if role == "organizer" and not organization_name:
        errors["organization_name"] = "Название организации обязательно для организатора."

    if organization_name and len(organization_name) > 255:
        errors["organization_name"] = "Название организации не должно превышать 255 символов."

    if organization_description and len(organization_description) > 3000:
        errors["organization_description"] = "Описание организации не должно превышать 3000 символов."

    if errors:
        raise AuthError("Ошибка регистрации.", status_code=400, details=errors)

    validate_legal_confirmations(data)

    return {
        "email": email,
        "password": password,
        "full_name": full_name,
        "role": role,
        "organization_name": organization_name,
        "organization_description": organization_description,
    }


def validate_login_payload(data: dict) -> dict:
    errors = {}

    email = validate_email(data, "email", errors)
    password = str(data.get("password", ""))

    if not password:
        errors["password"] = "Пароль обязателен для заполнения."

    if errors:
        raise AuthError("Ошибка входа.", status_code=400, details=errors)

    return {
        "email": email,
        "password": password,
    }


def create_user(data: dict) -> dict:
    payload = validate_registration_payload(data)

    existing_user = User.query.filter(User.email == payload["email"]).first()

    if existing_user is not None:
        raise AuthError(
            "Пользователь с такой электронной почтой уже существует.",
            status_code=409,
            details={"email": "Эта электронная почта уже используется."},
        )

    user = User(
        email=payload["email"],
        password_hash=generate_password_hash(payload["password"]),
        full_name=payload["full_name"],
        role=payload["role"],
        organization_name=payload["organization_name"] if payload["role"] == "organizer" else None,
        organization_description=payload["organization_description"] if payload["role"] == "organizer" else None,
        legal_documents_accepted=False,
        legal_documents_accepted_at=None,
        is_blocked=False,
    )

    db.session.add(user)
    db.session.commit()

    tokens = create_tokens_for_user(user)

    return {
        "message": "Регистрация выполнена.",
        "user": user_to_auth_dict(user),
        **tokens,
    }


def authenticate_user(data: dict) -> dict:
    payload = validate_login_payload(data)

    user = User.query.filter(User.email == payload["email"]).first()

    if user is None or not check_password_hash(user.password_hash, payload["password"]):
        raise AuthError("Неверная электронная почта или пароль.", status_code=401)

    if user.is_blocked:
        raise AuthError(
            "Учетная запись заблокирована.",
            status_code=403,
            details={"reason": "blocked"},
        )

    tokens = create_tokens_for_user(user)

    return {
        "message": "Вход выполнен.",
        "user": user_to_auth_dict(user),
        **tokens,
    }


def refresh_user_tokens(user_id: int | str, refresh_token: str) -> dict:
    try:
        user_id = int(user_id)
    except (TypeError, ValueError) as error:
        raise AuthError("Токен недействителен.", status_code=401) from error

    user = User.query.filter(User.id == user_id).first()

    if user is None:
        raise AuthError("Пользователь не найден.", status_code=401)

    if user.is_blocked:
        raise AuthError(
            "Учетная запись заблокирована.",
            status_code=403,
            details={"reason": "blocked"},
        )

    if not user.refresh_token or user.refresh_token != refresh_token:
        raise AuthError("Refresh token недействителен.", status_code=401)

    tokens = create_tokens_for_user(user)

    return {
        "user": user_to_auth_dict(user),
        **tokens,
    }


def clear_refresh_token(user: User) -> None:
    user.refresh_token = None
    db.session.commit()


def accept_legal_documents_for_user(user: User, data: dict) -> User:
    if user.is_blocked:
        raise AuthError(
            "Учетная запись заблокирована.",
            status_code=403,
            details={"reason": "blocked"},
        )

    validate_legal_confirmations(data)

    user.legal_documents_accepted = True
    user.legal_documents_accepted_at = datetime.now()

    db.session.commit()

    return user
