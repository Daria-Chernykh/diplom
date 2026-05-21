from datetime import datetime, timezone

from app.extensions import db
from app.models import Event, EventComplaint, EventReview, Notification, ReviewComplaint, User
from app.reviews.services import (
    ReviewError,
    delete_review_by_admin,
    hide_review_after_complaint,
    restore_review_after_complaint,
)


class ComplaintError(Exception):
    def __init__(self, message: str, status_code: int = 400, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details


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


def get_event_complaint_or_404(complaint_id: int) -> EventComplaint:
    complaint = EventComplaint.query.filter(EventComplaint.id == complaint_id).first()

    if complaint is None:
        raise ComplaintError("Жалоба на мероприятие не найдена.", status_code=404)

    return complaint


def get_review_complaint_or_404(complaint_id: int) -> ReviewComplaint:
    complaint = ReviewComplaint.query.filter(ReviewComplaint.id == complaint_id).first()

    if complaint is None:
        raise ComplaintError("Жалоба на отзыв не найдена.", status_code=404)

    return complaint


def touch_event_complaint(complaint: EventComplaint) -> None:
    complaint.last_changed_at = datetime.now(timezone.utc)


def create_event_complaint(user: User, event_id: int, data: dict) -> EventComplaint:
    event = Event.query.filter(Event.id == event_id).first()

    if event is None:
        raise ComplaintError("Мероприятие не найдено.", status_code=404)

    if event.organizer_id == user.id:
        raise ComplaintError("Нельзя пожаловаться на собственное мероприятие.", status_code=403)

    if event.status not in {"published", "blocked", "on_review"}:
        raise ComplaintError("На это мероприятие нельзя подать жалобу.", status_code=400)

    existing_complaint = (
        EventComplaint.query
        .filter(
            EventComplaint.event_id == event.id,
            EventComplaint.reporter_id == user.id,
        )
        .first()
    )

    if existing_complaint is not None:
        raise ComplaintError("Вы уже подали жалобу на это мероприятие.", status_code=409)

    complaint = EventComplaint(
        event_id=event.id,
        reporter_id=user.id,
        complaint_type=data["complaint_type"],
        comment=data["comment"],
    )

    event.status = "blocked"

    db.session.add(complaint)

    create_notification(
        user_id=event.organizer_id,
        event_id=event.id,
        organizer_id=event.organizer_id,
        notification_type="organizer_event_complaint_received",
        title="Получена жалоба, карточка заблокирована",
        message=f"На мероприятие «{event.title}» поступила жалоба. Карточка временно скрыта.",
        action_url=f"/organizer/events/{event.id}/edit",
    )

    create_notification(
        user_id=user.id,
        event_id=event.id,
        organizer_id=event.organizer_id,
        notification_type="event_complaint_created",
        title="Жалоба отправлена",
        message=f"Система приняла жалобу на мероприятие «{event.title}».",
        action_url=None,
    )

    affected_user_ids = {
        registration.user_id
        for registration in event.registrations
        if registration.status == "registered"
    }

    affected_user_ids.update(
        favorite.user_id
        for favorite in event.favorites
    )

    for affected_user_id in affected_user_ids:
        if affected_user_id == user.id:
            continue

        create_notification(
            user_id=affected_user_id,
            event_id=event.id,
            organizer_id=event.organizer_id,
            notification_type="event_temporarily_blocked",
            title="Мероприятие временно заблокировано",
            message=f"Карточка мероприятия «{event.title}» временно скрыта из-за проверки.",
            action_url=None,
        )

    db.session.commit()

    return complaint


def get_admin_event_complaints(status: str | None = None) -> list[EventComplaint]:
    query = EventComplaint.query.join(Event, Event.id == EventComplaint.event_id)

    if status in {"published", "blocked", "on_review", "archived"}:
        query = query.filter(Event.status == status)

    return query.order_by(EventComplaint.last_changed_at.desc()).all()


def restore_event_complaint(complaint_id: int) -> Event:
    complaint = get_event_complaint_or_404(complaint_id)
    event = complaint.event

    event.status = "published"
    event.organizer_complaint_comment = None

    create_notification(
        user_id=event.organizer_id,
        event_id=event.id,
        organizer_id=event.organizer_id,
        notification_type="event_restored",
        title="Исправления приняты, карточка опубликована",
        message=f"Карточка мероприятия «{event.title}» снова опубликована.",
        action_url=f"/events/{event.id}",
    )

    for favorite in event.favorites:
        create_notification(
            user_id=favorite.user_id,
            event_id=event.id,
            organizer_id=event.organizer_id,
            notification_type="favorite_event_restored",
            title="Мероприятие восстановлено",
            message=f"Мероприятие «{event.title}» снова доступно.",
            action_url=f"/events/{event.id}",
        )

    db.session.delete(complaint)
    db.session.commit()

    return event


def reject_event_complaint(complaint_id: int) -> Event:
    complaint = get_event_complaint_or_404(complaint_id)
    event = complaint.event

    event.status = "published"
    event.organizer_complaint_comment = None

    create_notification(
        user_id=complaint.reporter_id,
        event_id=event.id,
        organizer_id=event.organizer_id,
        notification_type="event_complaint_rejected",
        title="Жалоба отклонена",
        message=f"Администратор не подтвердил нарушение по мероприятию «{event.title}».",
        action_url=f"/events/{event.id}",
    )

    create_notification(
        user_id=event.organizer_id,
        event_id=event.id,
        organizer_id=event.organizer_id,
        notification_type="organizer_event_complaint_rejected",
        title="Жалоба отклонена администратором",
        message=f"Карточка мероприятия «{event.title}» снова доступна.",
        action_url=f"/events/{event.id}",
    )

    db.session.delete(complaint)
    db.session.commit()

    return event


def keep_event_blocked(complaint_id: int) -> Event:
    complaint = get_event_complaint_or_404(complaint_id)
    event = complaint.event

    event.status = "blocked"
    touch_event_complaint(complaint)

    create_notification(
        user_id=event.organizer_id,
        event_id=event.id,
        organizer_id=event.organizer_id,
        notification_type="event_remains_blocked",
        title="Карточка оставлена заблокированной",
        message=f"Карточка мероприятия «{event.title}» остается заблокированной.",
        action_url=f"/organizer/events/{event.id}/edit",
    )

    db.session.commit()

    return event


def block_event_organizer(complaint_id: int) -> Event:
    complaint = get_event_complaint_or_404(complaint_id)
    event = complaint.event

    event.status = "blocked"
    event.organizer.is_blocked = True

    create_notification(
        user_id=event.organizer_id,
        event_id=event.id,
        organizer_id=event.organizer_id,
        notification_type="organizer_blocked_by_event_complaint",
        title="Учетная запись организатора заблокирована",
        message=f"Администратор заблокировал учетную запись по жалобе на мероприятие «{event.title}».",
        action_url=None,
    )

    db.session.delete(complaint)
    db.session.commit()

    return event


def block_false_event_complainant(complaint_id: int) -> Event:
    complaint = get_event_complaint_or_404(complaint_id)
    event = complaint.event

    event.status = "published"
    complaint.reporter.is_blocked = True
    complaint.reporter.refresh_token = None

    create_notification(
        user_id=event.organizer_id,
        event_id=event.id,
        organizer_id=event.organizer_id,
        notification_type="organizer_event_complaint_rejected_complainant_blocked",
        title="Жалоба отклонена",
        message=f"Карточка мероприятия «{event.title}» восстановлена, заявитель заблокирован.",
        action_url=f"/events/{event.id}",
    )

    db.session.delete(complaint)
    db.session.commit()

    return event


def mark_blocked_event_sent_to_admin(event: Event) -> None:
    complaint = (
        EventComplaint.query
        .filter(EventComplaint.event_id == event.id)
        .order_by(EventComplaint.last_changed_at.desc())
        .first()
    )

    if complaint is not None:
        touch_event_complaint(complaint)


def create_review_complaint(user: User, review_id: int) -> ReviewComplaint:
    review = EventReview.query.filter(EventReview.id == review_id).first()

    if review is None:
        raise ComplaintError("Отзыв не найден.", status_code=404)

    if review.user_id == user.id:
        raise ComplaintError("Нельзя пожаловаться на собственный отзыв.", status_code=403)

    if review.is_hidden:
        raise ComplaintError("На этот отзыв уже подана жалоба.", status_code=409)

    existing_complaint = (
        ReviewComplaint.query
        .filter(
            ReviewComplaint.review_id == review.id,
            ReviewComplaint.reporter_id == user.id,
        )
        .first()
    )

    if existing_complaint is not None:
        raise ComplaintError("Вы уже подали жалобу на этот отзыв.", status_code=409)

    complaint = ReviewComplaint(
        review_id=review.id,
        reporter_id=user.id,
    )

    hide_review_after_complaint(review)

    event = review.event

    db.session.add(complaint)

    create_notification(
        user_id=review.user_id,
        event_id=event.id if event else None,
        organizer_id=event.organizer_id if event else None,
        notification_type="review_temporarily_hidden",
        title="Ваш отзыв временно скрыт",
        message="На отзыв поступила жалоба. Отзыв временно скрыт до проверки администратором.",
        action_url=f"/events/{event.id}" if event else None,
    )

    if event is not None:
        create_notification(
            user_id=event.organizer_id,
            event_id=event.id,
            organizer_id=event.organizer_id,
            notification_type="event_review_temporarily_hidden",
            title="Отзыв к мероприятию временно скрыт",
            message=f"На отзыв к мероприятию «{event.title}» поступила жалоба.",
            action_url=f"/events/{event.id}",
        )

    db.session.commit()

    return complaint


def get_admin_review_complaints() -> list[ReviewComplaint]:
    return (
        ReviewComplaint.query
        .join(EventReview, EventReview.id == ReviewComplaint.review_id)
        .order_by(ReviewComplaint.last_changed_at.desc())
        .all()
    )


def keep_review_after_complaint(complaint_id: int) -> EventReview:
    complaint = get_review_complaint_or_404(complaint_id)
    review = complaint.review
    event = review.event

    restore_review_after_complaint(review)

    create_notification(
        user_id=review.user_id,
        event_id=event.id if event else None,
        organizer_id=event.organizer_id if event else None,
        notification_type="review_kept_after_check",
        title="Отзыв оставлен после проверки",
        message="Администратор проверил жалобу и оставил отзыв опубликованным.",
        action_url=f"/events/{event.id}" if event else None,
    )

    db.session.delete(complaint)
    db.session.commit()

    return review


def delete_review_and_block_author(complaint_id: int) -> None:
    complaint = get_review_complaint_or_404(complaint_id)
    review = complaint.review
    author = review.user

    if author is not None:
        author.is_blocked = True
        author.refresh_token = None

    delete_review_by_admin(review.id)

    db.session.delete(complaint)
    db.session.commit()

def get_event_complaints(status: str | None = None) -> list[EventComplaint]:
    return get_admin_event_complaints(status)


def get_review_complaints() -> list[ReviewComplaint]:
    return get_admin_review_complaints()


def restore_event_after_complaint(complaint_id: int) -> Event:
    return restore_event_complaint(complaint_id)


def keep_event_blocked_after_complaint(complaint_id: int) -> Event:
    return keep_event_blocked(complaint_id)


def block_organizer_after_event_complaint(complaint_id: int) -> Event:
    return block_event_organizer(complaint_id)


def block_false_complainant_after_event_complaint(complaint_id: int) -> Event:
    return block_false_event_complainant(complaint_id)


def delete_review_after_complaint(complaint_id: int) -> None:
    delete_review_and_block_author(complaint_id)


def block_author_and_delete_review_after_complaint(complaint_id: int) -> None:
    delete_review_and_block_author(complaint_id)