import re


EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def normalize_email(email: str) -> str:
    return email.strip().lower()


def validate_registration_payload(data: dict) -> dict:
    errors: dict[str, str] = {}

    email = str(data.get("email", "")).strip()
    password = str(data.get("password", ""))
    full_name = str(data.get("full_name", "")).strip()
    phone = str(data.get("phone", "")).strip()
    role = str(data.get("role", "user")).strip()

    organization_name = str(data.get("organization_name", "")).strip()
    organization_description = str(data.get("organization_description", "")).strip()

    if not email:
        errors["email"] = "Укажите электронную почту."
    elif not EMAIL_PATTERN.match(email):
        errors["email"] = "Укажите корректную электронную почту."

    if not password:
        errors["password"] = "Укажите пароль."
    elif len(password) < 8:
        errors["password"] = "Пароль должен содержать не менее 8 символов."

    if role not in {"user", "organizer"}:
        errors["role"] = "При регистрации можно выбрать роль user или organizer."

    if role == "organizer" and not organization_name:
        errors["organization_name"] = "Для организатора укажите название организации."

    if errors:
        raise ValueError(errors)

    return {
        "email": normalize_email(email),
        "password": password,
        "full_name": full_name or None,
        "phone": phone or None,
        "role": role,
        "organization_name": organization_name or None,
        "organization_description": organization_description or None,
    }


def validate_login_payload(data: dict) -> dict:
    errors: dict[str, str] = {}

    email = str(data.get("email", "")).strip()
    password = str(data.get("password", ""))

    if not email:
        errors["email"] = "Укажите электронную почту."
    elif not EMAIL_PATTERN.match(email):
        errors["email"] = "Укажите корректную электронную почту."

    if not password:
        errors["password"] = "Укажите пароль."

    if errors:
        raise ValueError(errors)

    return {
        "email": normalize_email(email),
        "password": password,
    }


def user_to_dict(user) -> dict:
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