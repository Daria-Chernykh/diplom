from datetime import datetime, timezone

from openpyxl import Workbook

from app.extensions import db
from app.models import Event, EventRegistration, EventRegistrationField, Notification, User


class RegistrationError(Exception):
    def __init__(self, message: str, status_code: int = 400, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details


def get_event_or_404(event_id: int) -> Event:
    event = Event.query.filter(Event.id == event_id).first()

    if event is None:
        raise RegistrationError("Мероприятие не найдено.", status_code=404)

    return event


def get_registration_or_404(registration_id: int) -> EventRegistration:
    registration = EventRegistration.query.filter(EventRegistration.id == registration_id).first()

    if registration is None:
        raise RegistrationError("Регистрация не найдена.", status_code=404)

    return registration


def create_notification(
    user_id: int,
    notification_type: str,
    title: str,
    message: str,
    event_id: int | None = None,
    organizer_id: int | None = None,
    action_url: str | None = None,
) -> Notification:
    notification = Notification(
        user_id=user_id,
        event_id=event_id,
        organizer_id=organizer_id,
        notification_type=notification_type,
        title=title,
        message=message,
        action_url=action_url,
    )

    db.session.add(notification)

    return notification


def get_event_registration_fields(event_id: int) -> list[EventRegistrationField]:
    event = get_event_or_404(event_id)

    if event.registration_type != "internal":
        return []

    return (
        EventRegistrationField.query
        .filter(EventRegistrationField.event_id == event.id)
        .order_by(EventRegistrationField.sort_order.asc())
        .all()
    )


def get_user_event_registration(user: User, event_id: int) -> EventRegistration | None:
    return (
        EventRegistration.query
        .filter(
            EventRegistration.event_id == event_id,
            EventRegistration.user_id == user.id,
        )
        .first()
    )


def ensure_registration_allowed(user: User, event: Event, expected_type: str) -> None:
    if user.is_blocked:
        raise RegistrationError("Учетная запись заблокирована.", status_code=403)

    if event.status != "published":
        raise RegistrationError("Регистрация доступна только на опубликованное мероприятие.", status_code=400)

    if event.registration_type != expected_type:
        raise RegistrationError("Для мероприятия выбран другой тип регистрации.", status_code=400)

    if event.organizer_id == user.id:
        raise RegistrationError("Организатор не может зарегистрироваться на собственное мероприятие.", status_code=403)


def create_internal_registration(user: User, event_id: int, answers: dict) -> EventRegistration:
    event = get_event_or_404(event_id)
    ensure_registration_allowed(user, event, "internal")

    registration = get_user_event_registration(user, event.id)

    if registration is not None and registration.status in {"pending", "registered"}:
        raise RegistrationError("Вы уже подали заявку или зарегистрированы на мероприятие.", status_code=409)

    status = "pending" if event.registration_confirmation == "manual" else "registered"

    if registration is None:
        registration = EventRegistration(
            event_id=event.id,
            user_id=user.id,
            status=status,
            answers=answers,
            submitted_at=datetime.now(timezone.utc),
        )
        db.session.add(registration)
    else:
        registration.status = status
        registration.answers = answers
        registration.submitted_at = datetime.now(timezone.utc)

    if status == "pending":
        create_notification(
            user_id=user.id,
            event_id=event.id,
            organizer_id=event.organizer_id,
            notification_type="registration_request_sent",
            title="Заявка отправлена",
            message=f"Заявка на мероприятие «{event.title}» отправлена организатору.",
            action_url=f"/events/{event.id}",
        )

        create_notification(
            user_id=event.organizer_id,
            event_id=event.id,
            organizer_id=event.organizer_id,
            notification_type="organizer_new_registration_request",
            title="Новая заявка на регистрацию",
            message=f"Пользователь отправил заявку на мероприятие «{event.title}».",
            action_url=f"/organizer/events/{event.id}/participants",
        )
    else:
        create_notification(
            user_id=user.id,
            event_id=event.id,
            organizer_id=event.organizer_id,
            notification_type="registration_created",
            title="Регистрация оформлена",
            message=f"Вы зарегистрированы на мероприятие «{event.title}».",
            action_url=f"/events/{event.id}",
        )

        create_notification(
            user_id=event.organizer_id,
            event_id=event.id,
            organizer_id=event.organizer_id,
            notification_type="organizer_new_registration",
            title="Новая регистрация на мероприятие",
            message=f"Пользователь зарегистрировался на мероприятие «{event.title}».",
            action_url=f"/organizer/events/{event.id}/participants",
        )

    db.session.commit()

    return registration


def confirm_external_registration(user: User, event_id: int) -> EventRegistration:
    event = get_event_or_404(event_id)
    ensure_registration_allowed(user, event, "external")

    registration = get_user_event_registration(user, event.id)

    if registration is not None and registration.status == "registered":
        raise RegistrationError("Внешняя регистрация уже подтверждена.", status_code=409)

    if registration is None:
        registration = EventRegistration(
            event_id=event.id,
            user_id=user.id,
            status="registered",
            answers={},
            submitted_at=datetime.now(timezone.utc),
        )
        db.session.add(registration)
    else:
        registration.status = "registered"
        registration.answers = {}
        registration.submitted_at = datetime.now(timezone.utc)

    create_notification(
        user_id=event.organizer_id,
        event_id=event.id,
        organizer_id=event.organizer_id,
        notification_type="organizer_external_registration_confirmed",
        title="Пользователь подтвердил внешнюю регистрацию",
        message=f"Пользователь отметил регистрацию на мероприятие «{event.title}».",
        action_url=f"/organizer/events/{event.id}/participants",
    )

    db.session.commit()

    return registration


def cancel_registration(user: User, registration_id: int) -> EventRegistration:
    registration = get_registration_or_404(registration_id)

    if registration.user_id != user.id:
        raise RegistrationError("Нельзя отменить чужую регистрацию.", status_code=403)

    if registration.status not in {"pending", "registered"}:
        raise RegistrationError("Эту регистрацию нельзя отменить.", status_code=400)

    previous_status = registration.status
    registration.status = "canceled"

    event = registration.event

    create_notification(
        user_id=user.id,
        event_id=event.id,
        organizer_id=event.organizer_id,
        notification_type="registration_canceled_by_user",
        title="Регистрация отменена пользователем",
        message=f"Вы отменили регистрацию на мероприятие «{event.title}».",
        action_url=f"/events/{event.id}",
    )

    create_notification(
        user_id=event.organizer_id,
        event_id=event.id,
        organizer_id=event.organizer_id,
        notification_type="organizer_registration_canceled_by_user",
        title="Пользователь отменил регистрацию",
        message=(
            f"Пользователь отменил заявку на мероприятие «{event.title}»."
            if previous_status == "pending"
            else f"Пользователь отменил регистрацию на мероприятие «{event.title}»."
        ),
        action_url=f"/organizer/events/{event.id}/participants",
    )

    db.session.commit()

    return registration


def approve_registration(organizer: User, registration_id: int) -> EventRegistration:
    registration = get_registration_or_404(registration_id)
    event = registration.event

    if event.organizer_id != organizer.id and organizer.role != "admin":
        raise RegistrationError("Нельзя подтверждать заявки на чужое мероприятие.", status_code=403)

    if registration.status != "pending":
        raise RegistrationError("Подтвердить можно только заявку в ожидании.", status_code=400)

    registration.status = "registered"

    create_notification(
        user_id=registration.user_id,
        event_id=event.id,
        organizer_id=event.organizer_id,
        notification_type="registration_approved",
        title="Регистрация подтверждена",
        message=f"Организатор подтвердил регистрацию на мероприятие «{event.title}».",
        action_url=f"/events/{event.id}",
    )

    db.session.commit()

    return registration


def reject_registration(organizer: User, registration_id: int) -> EventRegistration:
    registration = get_registration_or_404(registration_id)
    event = registration.event

    if event.organizer_id != organizer.id and organizer.role != "admin":
        raise RegistrationError("Нельзя отклонять заявки на чужое мероприятие.", status_code=403)

    if registration.status != "pending":
        raise RegistrationError("Отклонить можно только заявку в ожидании.", status_code=400)

    registration.status = "rejected"

    create_notification(
        user_id=registration.user_id,
        event_id=event.id,
        organizer_id=event.organizer_id,
        notification_type="registration_rejected",
        title="Заявка отклонена",
        message=f"Организатор отклонил заявку на мероприятие «{event.title}».",
        action_url=f"/events/{event.id}",
    )

    db.session.commit()

    return registration


def get_user_registrations(user: User) -> list[EventRegistration]:
    return (
        EventRegistration.query
        .join(Event, Event.id == EventRegistration.event_id)
        .filter(
            EventRegistration.user_id == user.id,
            Event.status != "archived",
        )
        .order_by(Event.event_datetime.asc())
        .all()
    )


def get_user_registration_archive(user: User) -> list[EventRegistration]:
    return (
        EventRegistration.query
        .join(Event, Event.id == EventRegistration.event_id)
        .filter(
            EventRegistration.user_id == user.id,
            Event.status == "archived",
        )
        .order_by(Event.event_datetime.desc())
        .all()
    )


def get_event_participants(organizer: User, event_id: int) -> list[EventRegistration]:
    event = get_event_or_404(event_id)

    if event.organizer_id != organizer.id and organizer.role != "admin":
        raise RegistrationError("Нет доступа к списку участников.", status_code=403)

    if event.registration_type == "none":
        return []

    return (
        EventRegistration.query
        .filter(EventRegistration.event_id == event.id)
        .order_by(EventRegistration.submitted_at.desc())
        .all()
    )


def build_participants_workbook(organizer: User, event_id: int) -> Workbook:
    event = get_event_or_404(event_id)

    if event.organizer_id != organizer.id and organizer.role != "admin":
        raise RegistrationError("Нет доступа к экспорту участников.", status_code=403)

    if event.registration_type == "none":
        raise RegistrationError("Для мероприятия без регистрации список участников не формируется.", status_code=400)

    participants = get_event_participants(organizer, event_id)

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Участники"

    fields = (
        EventRegistrationField.query
        .filter(EventRegistrationField.event_id == event.id)
        .order_by(EventRegistrationField.sort_order.asc())
        .all()
    )

    headers = ["ID", "ФИО", "Email", "Телефон", "Статус", "Дата подачи"]

    if event.registration_type == "internal":
        headers.extend([field.field_name for field in fields])

    sheet.append(headers)

    for registration in participants:
        user = registration.user

        row = [
            registration.id,
            user.full_name if user else "",
            user.email if user else "",
            user.phone if user else "",
            registration.status,
            registration.submitted_at.strftime("%d.%m.%Y %H:%M") if registration.submitted_at else "",
        ]

        if event.registration_type == "internal":
            answers = registration.answers or {}
            row.extend([answers.get(str(field.id), "") for field in fields])

        sheet.append(row)

    for column_cells in sheet.columns:
        max_length = 0
        column = column_cells[0].column_letter

        for cell in column_cells:
            value = str(cell.value or "")
            if len(value) > max_length:
                max_length = len(value)

        sheet.column_dimensions[column].width = min(max_length + 2, 50)

    return workbook