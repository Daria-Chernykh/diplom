from app.extensions import db
from app.models import Event, Favorite, User


class FavoriteError(Exception):
    def __init__(self, message: str, status_code: int = 400, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details


def get_available_event_or_404(event_id: int) -> Event:
    event = (
        Event.query.join(User, User.id == Event.organizer_id)
        .filter(Event.id == event_id)
        .filter(Event.status == "published")
        .filter(User.is_blocked.is_(False))
        .first()
    )

    if event is None:
        raise FavoriteError("Мероприятие не найдено или недоступно.", status_code=404)

    return event


def get_user_favorites(user: User) -> list[Event]:
    return (
        Event.query.join(Favorite, Favorite.event_id == Event.id)
        .join(User, User.id == Event.organizer_id)
        .filter(Favorite.user_id == user.id)
        .filter(Event.status == "published")
        .filter(User.is_blocked.is_(False))
        .order_by(Event.event_datetime.asc(), Event.id.desc())
        .all()
    )


def is_event_in_favorites(user: User, event_id: int) -> bool:
    return (
        Favorite.query.filter(
            Favorite.user_id == user.id,
            Favorite.event_id == event_id,
        ).first()
        is not None
    )


def add_event_to_favorites(user: User, event_id: int) -> Favorite:
    event = get_available_event_or_404(event_id)

    existing_favorite = Favorite.query.filter(
        Favorite.user_id == user.id,
        Favorite.event_id == event.id,
    ).first()

    if existing_favorite is not None:
        return existing_favorite

    favorite = Favorite(
        user_id=user.id,
        event_id=event.id,
    )

    db.session.add(favorite)
    db.session.commit()

    return favorite


def remove_event_from_favorites(user: User, event_id: int) -> None:
    favorite = Favorite.query.filter(
        Favorite.user_id == user.id,
        Favorite.event_id == event_id,
    ).first()

    if favorite is None:
        raise FavoriteError("Мероприятие не найдено в избранном.", status_code=404)

    db.session.delete(favorite)
    db.session.commit()