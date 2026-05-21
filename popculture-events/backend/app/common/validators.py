import re
from datetime import datetime
from urllib.parse import urlparse


EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
URL_PATTERN = re.compile(r"^https?://.+")


class ValidationError(Exception):
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


def clean_string(value) -> str:
    if value is None:
        return ""

    return str(value).strip()


def clean_optional_string(value) -> str | None:
    cleaned_value = clean_string(value)

    return cleaned_value if cleaned_value else None


def validate_required_string(
    data: dict,
    field: str,
    label: str,
    errors: dict,
    min_length: int = 1,
    max_length: int | None = None,
) -> str:
    value = clean_string(data.get(field))

    if len(value) < min_length:
        errors[field] = f"{label} обязательно для заполнения."
        return value

    if max_length is not None and len(value) > max_length:
        errors[field] = f"{label} не должно превышать {max_length} символов."

    return value


def validate_optional_string(
    data: dict,
    field: str,
    label: str,
    errors: dict,
    max_length: int | None = None,
) -> str | None:
    value = clean_optional_string(data.get(field))

    if value and max_length is not None and len(value) > max_length:
        errors[field] = f"{label} не должно превышать {max_length} символов."

    return value


def validate_email(data: dict, field: str, errors: dict) -> str:
    value = clean_string(data.get(field)).lower()

    if not value:
        errors[field] = "Электронная почта обязательна для заполнения."
        return value

    if not EMAIL_PATTERN.match(value):
        errors[field] = "Введите корректную электронную почту."

    if len(value) > 255:
        errors[field] = "Электронная почта не должна превышать 255 символов."

    return value


def validate_password(data: dict, field: str, errors: dict, label: str = "Пароль") -> str:
    value = str(data.get(field, ""))

    if not value:
        errors[field] = f"{label} обязателен для заполнения."
        return value

    if len(value) < 6:
        errors[field] = f"{label} должен содержать не менее 6 символов."

    if len(value) > 128:
        errors[field] = f"{label} не должен превышать 128 символов."

    return value


def validate_choice(
    data: dict,
    field: str,
    label: str,
    allowed_values: set[str],
    errors: dict,
    required: bool = True,
) -> str | None:
    value = clean_string(data.get(field))

    if not value:
        if required:
            errors[field] = f"{label} обязательно для выбора."
        return None

    if value not in allowed_values:
        errors[field] = f"{label} имеет недопустимое значение."

    return value


def validate_datetime(data: dict, field: str, label: str, errors: dict) -> datetime | None:
    value = clean_string(data.get(field))

    if not value:
        errors[field] = f"{label} обязательно для заполнения."
        return None

    try:
        parsed_value = datetime.fromisoformat(value)
    except ValueError:
        errors[field] = f"{label} указано в неверном формате."
        return None

    return parsed_value


def validate_future_datetime(data: dict, field: str, label: str, errors: dict) -> datetime | None:
    parsed_value = validate_datetime(data, field, label, errors)

    if parsed_value and parsed_value <= datetime.now():
        errors[field] = f"{label} должно быть позже текущего времени."

    return parsed_value


def validate_url(data: dict, field: str, label: str, errors: dict, required: bool = True) -> str | None:
    value = clean_optional_string(data.get(field))

    if not value:
        if required:
            errors[field] = f"{label} обязательна для заполнения."
        return None

    parsed_url = urlparse(value)

    if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
        errors[field] = f"{label} должна быть корректной ссылкой."

    if len(value) > 500:
        errors[field] = f"{label} не должна превышать 500 символов."

    return value


def validate_rating(data: dict, field: str, errors: dict) -> int | None:
    raw_value = data.get(field)

    if raw_value is None or raw_value == "":
        errors[field] = "Оценка обязательна для заполнения."
        return None

    try:
        value = int(raw_value)
    except (TypeError, ValueError):
        errors[field] = "Оценка должна быть числом от 0 до 5."
        return None

    if value < 0 or value > 5:
        errors[field] = "Оценка должна быть от 0 до 5."

    return value


def raise_if_errors(errors: dict, message: str = "Ошибка валидации данных.") -> None:
    if errors:
        raise ValidationError(message, errors)