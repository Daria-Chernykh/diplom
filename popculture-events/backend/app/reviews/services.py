from pathlib import Path
from uuid import uuid4

from flask import current_app
from sqlalchemy import func
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import Event, EventRegistration, EventReview, File, Notification, OrganizerRating, User


ALLOWED_REVIEW_PHOTO_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}


class ReviewError(Exception):
    def __init__(self, message: str, status_code: int = 400, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details


def get_event_or_404(event_id: int) -> Event:
    event = Event.query.filter(Event.id == event_id).first()

    if event is None:
        raise ReviewError("Мероприятие не найдено.", status_code=404)

    return event


def get_user_or_404(user_id: int) -> User:
    user = User.query.filter(User.id == user_id).first()

    if user is None:
        raise ReviewError("Пользователь не найден.", status_code=404)

    return user


def check_event_is_archived(event: Event) -> None:
    if event.status != "archived":
        raise ReviewError(
            "Отзывы доступны только для прошедших мероприятий.",
            status_code=400,
            details={"event": "Мероприятие еще не находится в архиве."},
        )


def check_user_can_review_event(user: User, event: Event) -> None:
    if user.is_blocked:
        raise ReviewError("Учетная запись заблокирована.", status_code=403)

    if user.id == event.organizer_id:
        raise ReviewError(
            "Организатор не может оставить отзыв на собственное мероприятие.",
            status_code=403,
        )

    registration = (
        EventRegistration.query
        .filter(
            EventRegistration.event_id == event.id,
            EventRegistration.user_id == user.id,
            EventRegistration.status == "registered",
        )
        .first()
    )

    if registration is None:
        raise ReviewError(
            "Оставить отзыв может только зарегистрированный участник мероприятия.",
            status_code=403,
        )


def check_user_has_no_review(user: User, event: Event) -> None:
    existing_review = (
        EventReview.query
        .filter(
            EventReview.event_id == event.id,
            EventReview.user_id == user.id,
        )
        .first()
    )

    if existing_review is not None:
        raise ReviewError(
            "Пользователь уже оставил отзыв на это мероприятие.",
            status_code=409,
            details={"review": "Повторный отзыв можно оставить только после удаления текущего."},
        )


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


def get_review_photo_upload_dir() -> Path:
    upload_folder = current_app.config.get("UPLOAD_FOLDER", "uploads")
    upload_dir = Path(upload_folder) / "review_photos"
    upload_dir.mkdir(parents=True, exist_ok=True)

    return upload_dir


def save_review_photos(user: User, review: EventReview, photos: list) -> None:
    max_review_photos = int(current_app.config.get("MAX_REVIEW_PHOTOS", 5))

    if len(photos) > max_review_photos:
        raise ReviewError(
            f"К отзыву можно прикрепить не более {max_review_photos} фотографий.",
            status_code=400,
            details={"photos": f"Максимальное количество фотографий: {max_review_photos}."},
        )

    upload_dir = get_review_photo_upload_dir()

    for photo in photos:
        if not photo or not photo.filename:
            continue

        if photo.mimetype not in ALLOWED_REVIEW_PHOTO_MIME_TYPES:
            raise ReviewError(
                "Недопустимый формат фотографии.",
                status_code=400,
                details={"photos": "Разрешены только изображения JPEG, PNG и WEBP."},
            )

        original_filename = secure_filename(photo.filename)
        extension = Path(original_filename).suffix.lower()
        stored_filename = f"{uuid4().hex}{extension}"
        stored_path = upload_dir / stored_filename

        photo.save(stored_path)

        relative_path = str(Path("review_photos") / stored_filename).replace("\\", "/")

        file = File(
            uploader_id=user.id,
            entity_type="review",
            entity_id=review.id,
            file_path=relative_path,
            original_filename=original_filename,
            mime_type=photo.mimetype,
        )

        db.session.add(file)


def get_event_rating(event_id: int, include_hidden: bool = False) -> dict:
    query = EventReview.query.filter(EventReview.event_id == event_id)

    if not include_hidden:
        query = query.filter(EventReview.is_hidden.is_(False))

    result = (
        query.with_entities(
            func.avg(EventReview.rating),
            func.count(EventReview.id),
        )
        .first()
    )

    average_rating = result[0] if result and result[0] is not None else None
    reviews_count = result[1] if result and result[1] is not None else 0

    return {
        "average_rating": round(float(average_rating), 1) if average_rating is not None else None,
        "reviews_count": int(reviews_count),
    }


def get_event_reviews(
    user: User | None,
    event_id: int,
    sort: str = "new",
    include_hidden: bool = False,
) -> list[EventReview]:
    event = get_event_or_404(event_id)
    check_event_is_archived(event)

    query = (
        EventReview.query
        .filter(EventReview.event_id == event.id)
        .join(User, User.id == EventReview.user_id)
        .filter(User.is_blocked.is_(False))
    )

    if not include_hidden:
        query = query.filter(EventReview.is_hidden.is_(False))

    if sort == "positive":
        reviews = query.order_by(EventReview.rating.desc(), EventReview.created_at.desc()).all()
    elif sort == "negative":
        reviews = query.order_by(EventReview.rating.asc(), EventReview.created_at.desc()).all()
    else:
        reviews = query.order_by(EventReview.created_at.desc()).all()

    if user is None:
        return reviews

    own_reviews = [review for review in reviews if review.user_id == user.id]
    other_reviews = [review for review in reviews if review.user_id != user.id]

    return own_reviews + other_reviews


def create_event_review(user: User, event_id: int, payload: dict, photos: list | None = None) -> EventReview:
    event = get_event_or_404(event_id)
    check_event_is_archived(event)
    check_user_can_review_event(user, event)
    check_user_has_no_review(user, event)

    review = EventReview(
        event_id=event.id,
        user_id=user.id,
        rating=payload["rating"],
        comment=payload.get("comment"),
        is_hidden=False,
    )

    db.session.add(review)
    db.session.flush()

    save_review_photos(user, review, photos or [])

    create_notification(
        user_id=event.organizer_id,
        event_id=event.id,
        organizer_id=event.organizer_id,
        notification_type="new_event_review",
        title="Новый отзыв о мероприятии",
        message=f"Пользователь оставил отзыв о мероприятии «{event.title}».",
        action_url=f"/events/{event.id}",
    )

    create_notification(
        user_id=user.id,
        event_id=event.id,
        organizer_id=event.organizer_id,
        notification_type="review_created",
        title="Отзыв опубликован",
        message=f"Ваш отзыв о мероприятии «{event.title}» опубликован.",
        action_url=f"/events/{event.id}",
    )

    db.session.commit()

    return review


def delete_review_files(review_id: int) -> None:
    files = (
        File.query
        .filter(
            File.entity_type == "review",
            File.entity_id == review_id,
        )
        .all()
    )

    upload_folder = Path(current_app.config.get("UPLOAD_FOLDER", "uploads"))

    for file in files:
        file_path = upload_folder / file.file_path

        if file_path.exists() and file_path.is_file():
            file_path.unlink()

        db.session.delete(file)


def delete_event_review(user: User, review_id: int) -> None:
    review = EventReview.query.filter(EventReview.id == review_id).first()

    if review is None:
        raise ReviewError("Отзыв не найден.", status_code=404)

    if review.user_id != user.id and user.role != "admin":
        raise ReviewError("Нельзя удалить чужой отзыв.", status_code=403)

    event = review.event

    delete_review_files(review.id)
    db.session.delete(review)

    if event is not None:
        create_notification(
            user_id=user.id,
            event_id=event.id,
            organizer_id=event.organizer_id,
            notification_type="review_deleted",
            title="Отзыв удален",
            message=f"Отзыв о мероприятии «{event.title}» удален.",
            action_url=f"/events/{event.id}",
        )

        if event.organizer_id != user.id:
            create_notification(
                user_id=event.organizer_id,
                event_id=event.id,
                organizer_id=event.organizer_id,
                notification_type="event_review_deleted",
                title="Пользователь удалил отзыв",
                message=f"Пользователь удалил отзыв о мероприятии «{event.title}».",
                action_url=f"/events/{event.id}",
            )

    db.session.commit()


def hide_review_after_complaint(review: EventReview) -> None:
    review.is_hidden = True


def restore_review_after_complaint(review: EventReview) -> None:
    review.is_hidden = False


def delete_review_by_admin(review_id: int, admin_user: User | None = None) -> None:
    review = EventReview.query.filter(EventReview.id == review_id).first()

    if review is None:
        raise ReviewError("Отзыв не найден.", status_code=404)

    event = review.event
    review_author = review.user

    delete_review_files(review.id)

    if event is not None and review_author is not None:
        create_notification(
            user_id=review_author.id,
            event_id=event.id,
            organizer_id=event.organizer_id,
            notification_type="review_deleted_after_check",
            title="Отзыв удален после проверки",
            message=f"Администратор удалил ваш отзыв о мероприятии «{event.title}» после проверки жалобы.",
            action_url=None,
        )

        create_notification(
            user_id=event.organizer_id,
            event_id=event.id,
            organizer_id=event.organizer_id,
            notification_type="event_review_deleted_after_check",
            title="Отзыв к мероприятию удален после проверки",
            message=f"Администратор удалил отзыв к мероприятию «{event.title}». Оценка исключена из рейтинга.",
            action_url=f"/events/{event.id}",
        )

    db.session.delete(review)


def set_organizer_rating(user: User, organizer_id: int, rating: int) -> OrganizerRating:
    organizer = get_user_or_404(organizer_id)

    if organizer.role not in {"organizer", "admin"}:
        raise ReviewError("Указанный пользователь не является организатором.", status_code=400)

    if user.id == organizer.id:
        raise ReviewError("Нельзя поставить оценку самому себе.", status_code=400)

    if user.is_blocked:
        raise ReviewError("Учетная запись заблокирована.", status_code=403)

    organizer_rating = (
        OrganizerRating.query
        .filter(
            OrganizerRating.organizer_id == organizer.id,
            OrganizerRating.user_id == user.id,
        )
        .first()
    )

    is_new_rating = organizer_rating is None

    if organizer_rating is None:
        organizer_rating = OrganizerRating(
            organizer_id=organizer.id,
            user_id=user.id,
            rating=rating,
        )
        db.session.add(organizer_rating)
    else:
        organizer_rating.rating = rating

    create_notification(
        user_id=organizer.id,
        organizer_id=organizer.id,
        notification_type="organizer_rating_created" if is_new_rating else "organizer_rating_updated",
        title="Новая оценка организатора" if is_new_rating else "Оценка организатора изменена",
        message=(
            "Пользователь поставил оценку вашей странице организатора."
            if is_new_rating
            else "Пользователь изменил ранее поставленную оценку вашей странице организатора."
        ),
        action_url=f"/organizers/{organizer.id}",
    )

    create_notification(
        user_id=user.id,
        organizer_id=organizer.id,
        notification_type="organizer_rating_saved",
        title="Оценка организатора сохранена",
        message=f"Оценка организатора «{organizer.organization_name or organizer.full_name}» сохранена.",
        action_url=f"/organizers/{organizer.id}",
    )

    db.session.commit()

    return organizer_rating


def get_organizer_rating(user: User, organizer_id: int) -> OrganizerRating | None:
    return (
        OrganizerRating.query
        .filter(
            OrganizerRating.organizer_id == organizer_id,
            OrganizerRating.user_id == user.id,
        )
        .first()
    )


def delete_organizer_rating(user: User, organizer_id: int) -> None:
    organizer_rating = get_organizer_rating(user, organizer_id)

    if organizer_rating is None:
        raise ReviewError("Оценка организатора не найдена.", status_code=404)

    organizer = get_user_or_404(organizer_id)

    db.session.delete(organizer_rating)

    create_notification(
        user_id=organizer.id,
        organizer_id=organizer.id,
        notification_type="organizer_rating_deleted",
        title="Оценка организатора удалена",
        message="Пользователь удалил ранее поставленную оценку вашей странице организатора.",
        action_url=f"/organizers/{organizer.id}",
    )

    create_notification(
        user_id=user.id,
        organizer_id=organizer.id,
        notification_type="organizer_rating_deleted_by_user",
        title="Оценка организатора удалена",
        message=f"Оценка организатора «{organizer.organization_name or organizer.full_name}» удалена.",
        action_url=f"/organizers/{organizer.id}",
    )

    db.session.commit()