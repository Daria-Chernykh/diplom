from datetime import datetime, timezone

from sqlalchemy import func

from app.extensions import db
from app.models import Event, EventRegistration, EventRegistrationField, EventTag, Favorite, Tag, User
from app.notifications.services import (
    create_event_change_notifications,
    create_notification,
    create_notification_once,
)


class EventError(Exception):
    def __init__(self, message: str, status_code: int = 400, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details


def get_or_create_tags(tag_names: list[str]) -> list[Tag]:
    tags = []

    for tag_name in tag_names:
        normalized_name = str(tag_name).strip()

        if not normalized_name:
            continue

        tag = (
            Tag.query
            .filter(func.lower(Tag.name) == normalized_name.lower())
            .first()
        )

        if tag is None:
            tag = Tag(name=normalized_name)
            db.session.add(tag)
            db.session.flush()

        tags.append(tag)

    return tags


def set_event_tags(event: Event, tag_names: list[str]) -> None:
    event.event_tags.clear()
    db.session.flush()

    for tag in get_or_create_tags(tag_names):
        event.event_tags.append(EventTag(event=event, tag=tag))


def set_event_registration_fields(event: Event, fields: list[dict]) -> None:
    event.registration_fields.clear()
    db.session.flush()

    for field in fields:
        registration_field = EventRegistrationField(
            event=event,
            field_name=field["field_name"],
            field_type=field["field_type"],
            is_required=field["is_required"],
            sort_order=field["sort_order"],
            options=field.get("options"),
        )

        db.session.add(registration_field)


def get_events(
    query: str = "",
    tag: str = "",
    registration_type: str = "",
    event_format: str = "",
) -> list[Event]:
    events_query = Event.query.filter(Event.status == "published")

    if query:
        like_query = f"%{query.lower()}%"
        events_query = events_query.filter(
            db.or_(
                func.lower(Event.title).like(like_query),
                func.lower(Event.short_description).like(like_query),
                func.lower(Event.long_description).like(like_query),
                func.lower(Event.location).like(like_query),
            )
        )

    if registration_type:
        events_query = events_query.filter(Event.registration_type == registration_type)

    if event_format:
        events_query = events_query.filter(Event.event_format == event_format)

    if tag:
        like_tag = f"%{tag.lower()}%"
        events_query = (
            events_query
            .join(EventTag, EventTag.event_id == Event.id)
            .join(Tag, Tag.id == EventTag.tag_id)
            .filter(func.lower(Tag.name).like(like_tag))
        )

    return events_query.order_by(Event.event_datetime.asc()).all()


def get_event_by_id(event_id: int, current_user=None) -> Event:
    event = Event.query.filter(Event.id == event_id).first()

    if event is None:
        raise EventError("Мероприятие не найдено.", status_code=404)

    if event.status in {"published", "archived"}:
        return event

    if current_user is None:
        raise EventError("Мероприятие недоступно.", status_code=404)

    if current_user.role == "admin":
        return event

    if event.organizer_id == current_user.id:
        return event

    raise EventError("Мероприятие недоступно.", status_code=404)


def get_organizer_events(user: User, status: str = "") -> list[Event]:
    query = Event.query.filter(Event.organizer_id == user.id)

    if status:
        query = query.filter(Event.status == status)
    else:
        query = query.filter(Event.status != "archived")

    return query.order_by(Event.event_datetime.asc()).all()


def get_organizer_event(user: User, event_id: int) -> Event:
    event = Event.query.filter(Event.id == event_id).first()

    if event is None:
        raise EventError("Мероприятие не найдено.", status_code=404)

    if event.organizer_id != user.id and user.role != "admin":
        raise EventError("Нет доступа к этому мероприятию.", status_code=403)

    return event


def create_event(user: User, data: dict) -> Event:
    if user.role not in {"organizer", "admin"}:
        raise EventError("Создавать мероприятия может только организатор.", status_code=403)

    if user.is_blocked:
        raise EventError("Учетная запись заблокирована.", status_code=403)

    event = Event(
        organizer_id=user.id,
        title=data["title"],
        short_description=data["short_description"],
        long_description=data["long_description"],
        event_datetime=data["event_datetime"],
        event_format=data["event_format"],
        location=data["location"],
        schedule=data.get("schedule"),
        participant_requirements=data.get("participant_requirements"),
        registration_type=data["registration_type"],
        registration_confirmation=data.get("registration_confirmation"),
        external_registration_url=data.get("external_registration_url"),
        price_type=data["price_type"],
        price_value=data.get("price_value"),
        status="published",
        organizer_complaint_comment=None,
    )

    db.session.add(event)
    db.session.flush()

    set_event_tags(event, data.get("tags", []))

    if event.registration_type == "internal":
        set_event_registration_fields(event, data.get("registration_fields", []))

    create_notification(
        user_id=user.id,
        event_id=event.id,
        organizer_id=user.id,
        title="Мероприятие опубликовано",
        message=f"Карточка мероприятия «{event.title}» опубликована и доступна пользователям.",
        notification_type="event_created",
        action_url=f"/events/{event.id}",
        commit=False,
    )

    db.session.commit()

    return event


def get_changed_fields(event: Event, data: dict) -> set[str]:
    fields_to_check = {
        "title",
        "short_description",
        "long_description",
        "event_datetime",
        "event_format",
        "location",
        "schedule",
        "participant_requirements",
        "price_type",
        "price_value",
    }

    changed_fields = set()

    for field_name in fields_to_check:
        old_value = getattr(event, field_name)
        new_value = data.get(field_name)

        if old_value != new_value:
            changed_fields.add(field_name)

    return changed_fields


def update_event(user: User, event_id: int, data: dict) -> Event:
    event = get_organizer_event(user, event_id)

    if event.status == "archived":
        raise EventError("Архивное мероприятие нельзя редактировать.", status_code=400)

    changed_fields = get_changed_fields(event, data)

    event.title = data["title"]
    event.short_description = data["short_description"]
    event.long_description = data["long_description"]
    event.event_datetime = data["event_datetime"]
    event.event_format = data["event_format"]
    event.location = data["location"]
    event.schedule = data.get("schedule")
    event.participant_requirements = data.get("participant_requirements")
    event.price_type = data["price_type"]
    event.price_value = data.get("price_value")

    set_event_tags(event, data.get("tags", []))

    if event.status == "blocked" and data.get("send_to_admin"):
        event.status = "on_review"
        event.organizer_complaint_comment = data.get("organizer_complaint_comment")

        from app.complaints.services import mark_blocked_event_sent_to_admin

        mark_blocked_event_sent_to_admin(event)

        create_notification(
            user_id=user.id,
            event_id=event.id,
            organizer_id=event.organizer_id,
            title="Карточка отправлена на рассмотрение администратору",
            message=f"Карточка мероприятия «{event.title}» передана администратору для проверки.",
            notification_type="event_sent_to_admin_review",
            action_url=f"/organizer/events/{event.id}/edit",
            commit=False,
        )

    elif event.status == "published" and changed_fields:
        create_event_change_notifications(event, changed_fields)

    db.session.commit()

    return event


def archive_finished_events() -> int:
    now = datetime.now(timezone.utc)

    events = (
        Event.query
        .filter(
            Event.status == "published",
            Event.event_datetime < now,
        )
        .all()
    )

    archived_count = 0

    for event in events:
        event.status = "archived"
        archived_count += 1

        create_notification_once(
            user_id=event.organizer_id,
            event_id=event.id,
            organizer_id=event.organizer_id,
            title="Мероприятие перенесено в архив",
            message=f"Мероприятие «{event.title}» завершилось и перенесено в архив.",
            notification_type="event_archived_for_organizer",
            action_url="/organizer/events/archive",
        )

        registered_user_ids = [
            registration.user_id
            for registration in EventRegistration.query
            .filter(
                EventRegistration.event_id == event.id,
                EventRegistration.status == "registered",
            )
            .all()
        ]

        for user_id in registered_user_ids:
            create_notification_once(
                user_id=user_id,
                event_id=event.id,
                organizer_id=event.organizer_id,
                title="Оставьте отзыв о прошедшем мероприятии",
                message=f"Мероприятие «{event.title}» завершилось. Вы можете оставить отзыв.",
                notification_type="event_review_request",
                action_url=f"/events/{event.id}",
            )

    if archived_count > 0:
        db.session.commit()

    return archived_count