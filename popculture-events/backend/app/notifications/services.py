from app.extensions import db
from app.models import Event, EventRegistration, Favorite, Notification, User


class NotificationError(Exception):
    def __init__(self, message: str, status_code: int = 400, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details


def create_notification(
    user_id: int,
    title: str,
    message: str,
    notification_type: str,
    event_id: int | None = None,
    organizer_id: int | None = None,
    action_url: str | None = None,
    commit: bool = False,
) -> Notification:
    notification = Notification(
        user_id=user_id,
        event_id=event_id,
        organizer_id=organizer_id,
        title=title,
        message=message,
        notification_type=notification_type,
        action_url=action_url,
    )

    db.session.add(notification)

    if commit:
        db.session.commit()

    return notification


def create_notifications(
    user_ids: list[int],
    title: str,
    message: str,
    notification_type: str,
    event_id: int | None = None,
    organizer_id: int | None = None,
    action_url: str | None = None,
    commit: bool = False,
) -> list[Notification]:
    unique_user_ids = list(dict.fromkeys(user_ids))
    notifications = []

    for user_id in unique_user_ids:
        notifications.append(
            create_notification(
                user_id=user_id,
                event_id=event_id,
                organizer_id=organizer_id,
                title=title,
                message=message,
                notification_type=notification_type,
                action_url=action_url,
                commit=False,
            )
        )

    if commit:
        db.session.commit()

    return notifications


def notification_exists(
    user_id: int,
    notification_type: str,
    event_id: int | None = None,
) -> bool:
    query = Notification.query.filter(
        Notification.user_id == user_id,
        Notification.notification_type == notification_type,
    )

    if event_id is None:
        query = query.filter(Notification.event_id.is_(None))
    else:
        query = query.filter(Notification.event_id == event_id)

    return query.first() is not None


def create_notification_once(
    user_id: int,
    title: str,
    message: str,
    notification_type: str,
    event_id: int | None = None,
    organizer_id: int | None = None,
    action_url: str | None = None,
) -> Notification | None:
    if notification_exists(user_id, notification_type, event_id):
        return None

    return create_notification(
        user_id=user_id,
        event_id=event_id,
        organizer_id=organizer_id,
        title=title,
        message=message,
        notification_type=notification_type,
        action_url=action_url,
        commit=False,
    )


def get_registered_user_ids(event_id: int) -> list[int]:
    rows = (
        EventRegistration.query
        .with_entities(EventRegistration.user_id)
        .filter(EventRegistration.event_id == event_id)
        .filter(EventRegistration.status.in_(["pending", "registered"]))
        .all()
    )

    return [row.user_id for row in rows]


def get_favorite_user_ids(event_id: int) -> list[int]:
    rows = (
        Favorite.query
        .with_entities(Favorite.user_id)
        .filter(Favorite.event_id == event_id)
        .all()
    )

    return [row.user_id for row in rows]


def get_related_user_ids(event_id: int) -> list[int]:
    return list(
        dict.fromkeys(
            get_registered_user_ids(event_id) + get_favorite_user_ids(event_id)
        )
    )


def create_event_change_notifications(event: Event, changed_fields: set[str]) -> None:
    user_ids = get_related_user_ids(event.id)

    if not user_ids:
        return

    if "event_datetime" in changed_fields:
        create_notifications(
            user_ids=user_ids,
            event_id=event.id,
            organizer_id=event.organizer_id,
            title="Изменена дата или время мероприятия",
            message="Организатор изменил дату или время проведения мероприятия.",
            notification_type="event_datetime_changed",
            action_url=f"/events/{event.id}",
        )

    if "location" in changed_fields or "event_format" in changed_fields:
        create_notifications(
            user_ids=user_ids,
            event_id=event.id,
            organizer_id=event.organizer_id,
            title="Изменено место проведения",
            message="Организатор изменил адрес, площадку или формат проведения мероприятия.",
            notification_type="event_location_changed",
            action_url=f"/events/{event.id}",
        )

    if (
        "short_description" in changed_fields
        or "long_description" in changed_fields
        or "schedule" in changed_fields
    ):
        create_notifications(
            user_ids=user_ids,
            event_id=event.id,
            organizer_id=event.organizer_id,
            title="Обновлено описание мероприятия",
            message="Организатор изменил программу, расписание или другую важную информацию.",
            notification_type="event_description_changed",
            action_url=f"/events/{event.id}",
        )

    if "participant_requirements" in changed_fields:
        create_notifications(
            user_ids=user_ids,
            event_id=event.id,
            organizer_id=event.organizer_id,
            title="Изменены требования к участникам",
            message="Организатор изменил условия входа, правила участия или требования к участникам.",
            notification_type="event_requirements_changed",
            action_url=f"/events/{event.id}",
        )

    if "price_type" in changed_fields or "price_value" in changed_fields:
        create_notifications(
            user_ids=user_ids,
            event_id=event.id,
            organizer_id=event.organizer_id,
            title="Изменена стоимость участия",
            message="Организатор изменил информацию о стоимости участия.",
            notification_type="event_price_changed",
            action_url=f"/events/{event.id}",
        )

    if "external_registration_url" in changed_fields:
        create_notifications(
            user_ids=user_ids,
            event_id=event.id,
            organizer_id=event.organizer_id,
            title="Изменена ссылка на внешнюю регистрацию",
            message="Организатор изменил ссылку на регистрацию на стороннем ресурсе.",
            notification_type="event_external_registration_url_changed",
            action_url=f"/events/{event.id}",
        )


def create_event_blocked_notifications(event: Event) -> None:
    user_ids = get_related_user_ids(event.id)

    create_notifications(
        user_ids=user_ids,
        event_id=event.id,
        organizer_id=event.organizer_id,
        title="Мероприятие временно заблокировано",
        message=f"Карточка мероприятия «{event.title}» временно скрыта из-за проверки.",
        notification_type="event_temporarily_blocked",
        action_url=None,
    )


def create_event_restored_notifications(event: Event) -> None:
    user_ids = get_related_user_ids(event.id)

    create_notifications(
        user_ids=user_ids,
        event_id=event.id,
        organizer_id=event.organizer_id,
        title="Мероприятие восстановлено",
        message=f"Мероприятие «{event.title}» снова доступно.",
        notification_type="event_restored",
        action_url=f"/events/{event.id}",
    )


def get_user_notifications(user: User, only_unread: bool = False) -> list[Notification]:
    query = Notification.query.filter(Notification.user_id == user.id)

    if only_unread:
        query = query.filter(Notification.is_read.is_(False))

    return query.order_by(Notification.created_at.desc()).all()


def get_unread_count(user: User) -> int:
    return (
        Notification.query
        .filter(
            Notification.user_id == user.id,
            Notification.is_read.is_(False),
        )
        .count()
    )


def get_notification_for_user(user: User, notification_id: int) -> Notification:
    notification = (
        Notification.query
        .filter(
            Notification.id == notification_id,
            Notification.user_id == user.id,
        )
        .first()
    )

    if notification is None:
        raise NotificationError("Уведомление не найдено.", status_code=404)

    return notification


def mark_notification_read(user: User, notification_id: int) -> Notification:
    notification = get_notification_for_user(user, notification_id)

    notification.is_read = True
    db.session.commit()

    return notification


def mark_all_notifications_read(user: User) -> int:
    count = (
        Notification.query
        .filter(
            Notification.user_id == user.id,
            Notification.is_read.is_(False),
        )
        .update({"is_read": True}, synchronize_session=False)
    )

    db.session.commit()

    return count


def delete_notification(user: User, notification_id: int) -> None:
    notification = get_notification_for_user(user, notification_id)

    db.session.delete(notification)
    db.session.commit()


def delete_all_notifications(user: User) -> int:
    notifications = Notification.query.filter(Notification.user_id == user.id).all()
    count = len(notifications)

    for notification in notifications:
        db.session.delete(notification)

    db.session.commit()

    return count