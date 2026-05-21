from app.models import EventRegistration, EventRegistrationField


def registration_field_to_dict(field: EventRegistrationField) -> dict:
    return {
        "id": field.id,
        "field_name": field.field_name,
        "field_type": field.field_type,
        "is_required": field.is_required,
        "sort_order": field.sort_order,
    }


def registration_to_dict(registration: EventRegistration) -> dict:
    return {
        "id": registration.id,
        "event_id": registration.event_id,
        "user_id": registration.user_id,
        "status": registration.status,
        "answers": registration.answers or {},
        "submitted_at": registration.submitted_at.isoformat() if registration.submitted_at else None,
        "event": {
            "id": registration.event.id,
            "title": registration.event.title,
            "registration_type": registration.event.registration_type,
            "event_datetime": registration.event.event_datetime.isoformat()
            if registration.event.event_datetime
            else None,
            "status": registration.event.status,
        }
        if registration.event
        else None,
        "user": {
            "id": registration.user.id,
            "full_name": registration.user.full_name,
            "email": registration.user.email,
        }
        if registration.user
        else None,
    }


def validate_registration_answers(fields: list[EventRegistrationField], answers: dict) -> dict:
    errors = {}

    if not isinstance(answers, dict):
        raise ValueError({"answers": "Ответы формы должны быть переданы объектом."})

    result = {}

    for field in fields:
        key = str(field.id)
        value = answers.get(key)

        if field.is_required and (value is None or str(value).strip() == ""):
            errors[key] = f"Поле «{field.field_name}» обязательно для заполнения."
            continue

        if value is None:
            result[key] = None
            continue

        if field.field_type == "email" and value:
            string_value = str(value).strip()

            if "@" not in string_value or "." not in string_value:
                errors[key] = f"Поле «{field.field_name}» должно содержать корректную электронную почту."

            result[key] = string_value
        elif field.field_type == "number" and value != "":
            try:
                result[key] = float(value)
            except (TypeError, ValueError):
                errors[key] = f"Поле «{field.field_name}» должно содержать число."
        elif field.field_type == "checkbox":
            result[key] = bool(value)
        else:
            string_value = str(value).strip()

            if len(string_value) > 1000:
                errors[key] = f"Поле «{field.field_name}» не должно превышать 1000 символов."

            result[key] = string_value

    if errors:
        raise ValueError(errors)

    return result