from werkzeug.security import check_password_hash, generate_password_hash

from app.common.validators import (
    validate_optional_string,
    validate_password,
    validate_required_string,
)
from app.extensions import db
from app.models import File, User


class UserError(Exception):
    def __init__(self, message: str, status_code: int = 400, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details


def file_to_dict(file: File | None) -> dict | None:
    if file is None:
        return None

    return {
        "id": file.id,
        "file_url": f"/api/files/{file.id}",
        "original_filename": file.original_filename,
        "mime_type": file.mime_type,
    }


def get_user_entity_file(user_id: int, entity_type: str) -> dict | None:
    file = (
        File.query
        .filter(
            File.entity_type == entity_type,
            File.entity_id == user_id,
        )
        .order_by(File.id.desc())
        .first()
    )

    return file_to_dict(file)


def user_to_dict(user: User) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "phone": user.phone,
        "role": user.role,
        "is_blocked": user.is_blocked,
        "organization_name": user.organization_name,
        "organization_description": user.organization_description,
        "legal_documents_accepted": user.legal_documents_accepted,
        "legal_documents_accepted_at": user.legal_documents_accepted_at.isoformat()
        if user.legal_documents_accepted_at
        else None,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "profile_image": get_user_entity_file(user.id, "user_profile"),
        "organizer_image": get_user_entity_file(user.id, "organizer_profile"),
    }


def get_users() -> list[User]:
    return User.query.order_by(User.id.asc()).all()


def get_user_by_id(user_id: int) -> User:
    user = User.query.filter(User.id == user_id).first()

    if user is None:
        raise UserError("Пользователь не найден.", status_code=404)

    return user


def update_profile(user: User, data: dict) -> User:
    errors = {}

    full_name = validate_required_string(
        data,
        "full_name",
        "Имя пользователя",
        errors,
        max_length=150,
    )

    phone = validate_optional_string(
        data,
        "phone",
        "Телефон",
        errors,
        max_length=30,
    )

    organization_name = validate_optional_string(
        data,
        "organization_name",
        "Название организации",
        errors,
        max_length=150,
    )

    organization_description = validate_optional_string(
        data,
        "organization_description",
        "Описание организации",
        errors,
        max_length=3000,
    )

    if user.role == "organizer" and not organization_name:
        errors["organization_name"] = "Для организатора необходимо указать название организации."

    if errors:
        raise UserError("Ошибка обновления профиля.", status_code=400, details=errors)

    user.full_name = full_name
    user.phone = phone

    if user.role == "organizer":
        user.organization_name = organization_name
        user.organization_description = organization_description

    db.session.commit()

    return user


def change_password(user: User, data: dict) -> None:
    errors = {}

    current_password = str(data.get("current_password", ""))
    new_password = validate_password(data, "new_password", errors, "Новый пароль")

    if not current_password:
        errors["current_password"] = "Текущий пароль обязателен для заполнения."
    elif not check_password_hash(user.password_hash, current_password):
        errors["current_password"] = "Текущий пароль указан неверно."

    if current_password and new_password and current_password == new_password:
        errors["new_password"] = "Новый пароль должен отличаться от текущего."

    if errors:
        raise UserError("Ошибка изменения пароля.", status_code=400, details=errors)

    user.password_hash = generate_password_hash(new_password)
    db.session.commit()


def set_user_blocked(user_id: int, is_blocked: bool) -> User:
    user = get_user_by_id(user_id)

    if user.role == "admin":
        raise UserError("Администратора нельзя заблокировать.", status_code=400)

    user.is_blocked = is_blocked

    if is_blocked:
        user.refresh_token = None

    db.session.commit()

    return user