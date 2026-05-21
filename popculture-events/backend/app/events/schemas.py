from datetime import datetime

from sqlalchemy import func

from app.common.validators import (
    validate_choice,
    validate_future_datetime,
    validate_required_string,
    validate_url,
)
from app.extensions import db
from app.models import Event, EventReview, Favorite, File, OrganizerRating


EVENT_FORMATS = {"offline", "online"}
REGISTRATION_TYPES = {"internal", "external", "none"}
REGISTRATION_CONFIRMATION_TYPES = {"manual", "automatic"}
PRICE_TYPES = {"free", "fixed", "from"}

REGISTRATION_FIELD_TYPES = {
    "text",
    "email",
    "phone",
    "number",
    "date",
    "select",
    "textarea",
    "checkbox",
}


def file_to_dict(file: File | None) -> dict | None:
    if file is None:
        return None

    return {
        "id": file.id,
        "file_url": f"/api/files/view/{file.file_path}",
        "original_filename": file.original_filename,
        "mime_type": file.mime_type,
    }


def get_event_image(event: Event) -> File | None:
    return (
        File.query
        .filter(
            File.entity_type == "event",
            File.entity_id == event.id,
        )
        .order_by(File.id.desc())
        .first()
    )


def get_event_tags(event: Event) -> list[dict]:
    return [
        {
            "id": event_tag.tag.id,
            "name": event_tag.tag.name,
        }
        for event_tag in event.event_tags
        if event_tag.tag is not None
    ]


def get_event_average_rating(event: Event) -> dict:
    result = (
        db.session.query(
            func.avg(EventReview.rating),
            func.count(EventReview.id),
        )
        .filter(
            EventReview.event_id == event.id,
            EventReview.is_hidden.is_(False),
        )
        .first()
    )

    average_rating = result[0] if result and result[0] is not None else None
    reviews_count = result[1] if result and result[1] is not None else 0

    return {
        "average_rating": round(float(average_rating), 1) if average_rating is not None else None,
        "reviews_count": int(reviews_count),
    }


def get_organizer_average_rating(organizer_id: int) -> dict:
    event_reviews = (
        db.session.query(EventReview.rating)
        .join(Event, Event.id == EventReview.event_id)
        .filter(
            Event.organizer_id == organizer_id,
            Event.status == "archived",
            EventReview.is_hidden.is_(False),
        )
        .all()
    )

    organizer_ratings = (
        db.session.query(OrganizerRating.rating)
        .filter(OrganizerRating.organizer_id == organizer_id)
        .all()
    )

    values = [row[0] for row in event_reviews] + [row[0] for row in organizer_ratings]

    if not values:
        return {
            "average_rating": None,
            "ratings_count": 0,
        }

    return {
        "average_rating": round(sum(values) / len(values), 1),
        "ratings_count": len(values),
    }


def get_is_favorite(event: Event, current_user=None) -> bool:
    if current_user is None:
        return False

    favorite = (
        Favorite.query
        .filter(
            Favorite.event_id == event.id,
            Favorite.user_id == current_user.id,
        )
        .first()
    )

    return favorite is not None


def event_to_dict(event: Event, current_user=None) -> dict:
    image = get_event_image(event)
    tags = get_event_tags(event)
    event_rating = get_event_average_rating(event)
    organizer_rating = get_organizer_average_rating(event.organizer_id)

    return {
        "id": event.id,
        "organizer_id": event.organizer_id,
        "title": event.title,
        "short_description": event.short_description,
        "long_description": event.long_description,
        "event_datetime": event.event_datetime.isoformat() if event.event_datetime else None,
        "event_format": event.event_format,
        "location": event.location,
        "schedule": event.schedule,
        "participant_requirements": event.participant_requirements,
        "registration_type": event.registration_type,
        "registration_confirmation": event.registration_confirmation,
        "external_registration_url": event.external_registration_url,
        "price_type": event.price_type,
        "price_value": event.price_value,
        "status": event.status,
        "organizer_complaint_comment": event.organizer_complaint_comment,
        "created_at": event.created_at.isoformat() if event.created_at else None,
        "tags": tags,
        "image": file_to_dict(image),
        "is_favorite": get_is_favorite(event, current_user),
        "event_rating": event_rating,
        "organizer_rating": organizer_rating,
        "organizer": {
            "id": event.organizer.id,
            "full_name": event.organizer.full_name,
            "organization_name": event.organizer.organization_name,
            "organization_description": event.organizer.organization_description,
            "organizer_rating": organizer_rating,
        }
        if event.organizer
        else None,
    }


def validate_tags(value) -> list[str]:
    if value is None:
        return []

    if isinstance(value, str):
        raw_tags = [item.strip() for item in value.split(",")]
    elif isinstance(value, list):
        raw_tags = [str(item).strip() for item in value]
    else:
        raw_tags = []

    result = []

    for tag in raw_tags:
        if tag and tag not in result:
            result.append(tag[:80])

    return result[:20]


def validate_registration_fields(value) -> list[dict]:
    if value is None:
        return []

    if not isinstance(value, list):
        return []

    result = []

    for index, item in enumerate(value):
        if not isinstance(item, dict):
            continue

        field_name = str(item.get("field_name", "")).strip()
        field_type = str(item.get("field_type", "text")).strip()
        is_required = bool(item.get("is_required", False))
        options = item.get("options")

        if not field_name:
            continue

        if field_type not in REGISTRATION_FIELD_TYPES:
            field_type = "text"

        if options is not None and not isinstance(options, dict):
            options = None

        result.append(
            {
                "field_name": field_name[:150],
                "field_type": field_type,
                "is_required": is_required,
                "sort_order": index,
                "options": options,
            }
        )

    return result[:30]


def normalize_price_value(value) -> str | None:
    if value is None:
        return None

    value = str(value).strip()

    return value[:100] if value else None


def normalize_optional_text(value, max_length: int | None = None) -> str | None:
    if value is None:
        return None

    value = str(value).strip()

    if not value:
        return None

    if max_length is not None:
        return value[:max_length]

    return value


def validate_event_payload(data: dict, is_create: bool = True) -> dict:
    errors = {}

    title = validate_required_string(
        data,
        "title",
        "Название мероприятия",
        errors,
        max_length=200,
    )

    short_description = validate_required_string(
        data,
        "short_description",
        "Краткое описание",
        errors,
        max_length=2000,
    )

    long_description = validate_required_string(
        data,
        "long_description",
        "Расширенное описание",
        errors,
        max_length=10000,
    )

    if is_create:
        event_datetime = validate_future_datetime(
            data,
            "event_datetime",
            "Дата и время мероприятия",
            errors,
        )
    else:
        event_datetime_raw = data.get("event_datetime")

        if event_datetime_raw:
            try:
                event_datetime = datetime.fromisoformat(str(event_datetime_raw))
            except ValueError:
                event_datetime = None
                errors["event_datetime"] = "Дата и время мероприятия указаны в неверном формате."
        else:
            event_datetime = None
            errors["event_datetime"] = "Дата и время мероприятия обязательны для заполнения."

    event_format = validate_choice(
        data,
        "event_format",
        "Формат мероприятия",
        EVENT_FORMATS,
        errors,
    )

    location = validate_required_string(
        data,
        "location",
        "Место проведения",
        errors,
        max_length=500,
    )

    schedule = normalize_optional_text(data.get("schedule"), 5000)
    participant_requirements = normalize_optional_text(data.get("participant_requirements"), 5000)

    registration_type = validate_choice(
        data,
        "registration_type",
        "Тип регистрации",
        REGISTRATION_TYPES,
        errors,
    )

    registration_confirmation = normalize_optional_text(data.get("registration_confirmation"), 20)

    external_registration_url = None

    if registration_type == "external":
        external_registration_url = validate_url(
            data,
            "external_registration_url",
            "Ссылка на внешнюю регистрацию",
            errors,
            required=True,
        )
    else:
        external_registration_url = normalize_optional_text(data.get("external_registration_url"), 1000)

    price_type = validate_choice(
        data,
        "price_type",
        "Тип стоимости",
        PRICE_TYPES,
        errors,
        required=False,
    )

    if price_type is None:
        price_type = "free"

    price_value = normalize_price_value(data.get("price_value"))

    if registration_type == "internal":
        if registration_confirmation not in REGISTRATION_CONFIRMATION_TYPES:
            errors["registration_confirmation"] = (
                "Для внутренней регистрации необходимо выбрать подтверждение: manual или automatic."
            )
    else:
        registration_confirmation = None

    if registration_type == "none":
        external_registration_url = None
        registration_confirmation = None

    if price_type == "free":
        price_value = None

    if price_type in {"fixed", "from"} and not price_value:
        errors["price_value"] = "Для выбранного типа стоимости необходимо указать значение."

    tags = validate_tags(data.get("tags"))
    registration_fields = validate_registration_fields(data.get("registration_fields"))

    if registration_type == "internal" and len(registration_fields) == 0:
        registration_fields = [
            {
                "field_name": "Имя",
                "field_type": "text",
                "is_required": True,
                "sort_order": 0,
                "options": None,
            },
            {
                "field_name": "Электронная почта",
                "field_type": "email",
                "is_required": True,
                "sort_order": 1,
                "options": None,
            },
            {
                "field_name": "Телефон",
                "field_type": "phone",
                "is_required": True,
                "sort_order": 2,
                "options": None,
            },
        ]

    if registration_type != "internal":
        registration_fields = []

    organizer_complaint_comment = normalize_optional_text(
        data.get("organizer_complaint_comment"),
        5000,
    )

    if errors:
        raise ValueError(errors)

    return {
        "title": title,
        "short_description": short_description,
        "long_description": long_description,
        "event_datetime": event_datetime,
        "event_format": event_format,
        "location": location,
        "schedule": schedule,
        "participant_requirements": participant_requirements,
        "registration_type": registration_type,
        "registration_confirmation": registration_confirmation,
        "external_registration_url": external_registration_url,
        "price_type": price_type,
        "price_value": price_value,
        "tags": tags,
        "registration_fields": registration_fields,
        "organizer_complaint_comment": organizer_complaint_comment,
    }