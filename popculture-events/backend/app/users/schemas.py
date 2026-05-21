import re

from app.models import User


EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def normalize_string(value):
    if value is None:
        return None

    value = str(value).strip()

    return value or None


def validate_profile_payload(data: dict, current_user: User) -> dict:
    errors: dict[str, str] = {}

    full_name = normalize_string(data.get("full_name"))
    phone = normalize_string(data.get("phone"))

    organization_name = normalize_string(data.get("organization_name"))
    organization_description = normalize_string(data.get("organization_description"))

    if current_user.role == "organizer" and not organization_name:
        errors["organization_name"] = "Для организатора необходимо указать название организации."

    if errors:
        raise ValueError(errors)

    return {
        "full_name": full_name,
        "phone": phone,
        "organization_name": organization_name if current_user.role == "organizer" else current_user.organization_name,
        "organization_description": organization_description
        if current_user.role == "organizer"
        else current_user.organization_description,
    }


def validate_password_payload(data: dict) -> dict:
    errors: dict[str, str] = {}

    current_password = str(data.get("current_password", ""))
    new_password = str(data.get("new_password", ""))

    if not current_password:
        errors["current_password"] = "Укажите текущий пароль."

    if not new_password:
        errors["new_password"] = "Укажите новый пароль."
    elif len(new_password) < 8:
        errors["new_password"] = "Новый пароль должен содержать не менее 8 символов."

    if current_password and new_password and current_password == new_password:
        errors["new_password"] = "Новый пароль должен отличаться от текущего."

    if errors:
        raise ValueError(errors)

    return {
        "current_password": current_password,
        "new_password": new_password,
    }


def validate_user_search_params(args) -> dict:
    query = normalize_string(args.get("q"))
    role = normalize_string(args.get("role"))
    blocked = normalize_string(args.get("blocked"))

    if role is not None and role not in {"user", "organizer", "admin"}:
        raise ValueError({"role": "Недопустимая роль пользователя."})

    if blocked is not None and blocked not in {"true", "false"}:
        raise ValueError({"blocked": "Параметр blocked может принимать значения true или false."})

    return {
        "query": query,
        "role": role,
        "blocked": blocked,
    }


def user_to_dict(user: User) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "full_name": user.full_name,
        "phone": user.phone,
        "organization_name": user.organization_name,
        "organization_description": user.organization_description,
        "is_blocked": user.is_blocked,
        "legal_documents_accepted": user.legal_documents_accepted,
        "legal_documents_accepted_at": user.legal_documents_accepted_at.isoformat()
        if user.legal_documents_accepted_at
        else None,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }