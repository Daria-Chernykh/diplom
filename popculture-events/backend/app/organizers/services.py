from sqlalchemy import func

from app.extensions import db
from app.models import Event, EventReview, File, OrganizerRating, User


class OrganizerError(Exception):
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
        "file_url": f"/api/files/view/{file.file_path}",
        "original_filename": file.original_filename,
        "mime_type": file.mime_type,
    }


def get_organizer_image(organizer_id: int) -> dict | None:
    file = (
        File.query
        .filter(
            File.entity_type == "organizer_profile",
            File.entity_id == organizer_id,
        )
        .order_by(File.id.desc())
        .first()
    )

    return file_to_dict(file)


def calculate_organizer_rating(organizer_id: int) -> dict:
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


def organizer_to_dict(organizer: User) -> dict:
    rating = calculate_organizer_rating(organizer.id)

    return {
        "id": organizer.id,
        "email": organizer.email,
        "full_name": organizer.full_name,
        "phone": organizer.phone,
        "role": organizer.role,
        "is_blocked": organizer.is_blocked,
        "organization_name": organizer.organization_name,
        "organization_description": organizer.organization_description,
        "created_at": organizer.created_at.isoformat() if organizer.created_at else None,
        "organizer_image": get_organizer_image(organizer.id),
        "organizer_rating": rating,
        "average_rating": rating["average_rating"],
        "ratings_count": rating["ratings_count"],
    }


def get_public_organizers(query: str = "") -> list[User]:
    organizers_query = (
        User.query
        .filter(
            User.role.in_(["organizer", "admin"]),
            User.is_blocked.is_(False),
        )
    )

    if query:
        like_query = f"%{query.lower()}%"
        organizers_query = organizers_query.filter(
            db.or_(
                func.lower(User.full_name).like(like_query),
                func.lower(User.organization_name).like(like_query),
            )
        )

    return organizers_query.order_by(User.organization_name.asc(), User.full_name.asc()).all()


def get_organizers(query: str = "") -> list[User]:
    return get_public_organizers(query)


def get_organizer_by_id(organizer_id: int) -> User:
    organizer = (
        User.query
        .filter(
            User.id == organizer_id,
            User.role.in_(["organizer", "admin"]),
        )
        .first()
    )

    if organizer is None:
        raise OrganizerError("Организатор не найден.", status_code=404)

    if organizer.is_blocked:
        raise OrganizerError("Организатор заблокирован.", status_code=403)

    return organizer


def get_organizer(organizer_id: int) -> User:
    return get_organizer_by_id(organizer_id)


def get_admin_organizers(query: str = "", blocked: str = "") -> list[User]:
    organizers_query = User.query.filter(User.role.in_(["organizer", "admin"]))

    if query:
        like_query = f"%{query.lower()}%"
        organizers_query = organizers_query.filter(
            db.or_(
                func.lower(User.email).like(like_query),
                func.lower(User.full_name).like(like_query),
                func.lower(User.organization_name).like(like_query),
            )
        )

    if blocked == "true":
        organizers_query = organizers_query.filter(User.is_blocked.is_(True))

    if blocked == "false":
        organizers_query = organizers_query.filter(User.is_blocked.is_(False))

    return organizers_query.order_by(User.id.asc()).all()


def set_organizer_blocked(organizer_id: int, is_blocked: bool) -> User:
    organizer = (
        User.query
        .filter(
            User.id == organizer_id,
            User.role.in_(["organizer", "admin"]),
        )
        .first()
    )

    if organizer is None:
        raise OrganizerError("Организатор не найден.", status_code=404)

    if organizer.role == "admin":
        raise OrganizerError("Администратора нельзя заблокировать.", status_code=400)

    organizer.is_blocked = is_blocked

    if is_blocked:
        organizer.refresh_token = None

    db.session.commit()

    return organizer


def block_organizer(organizer_id: int) -> User:
    return set_organizer_blocked(organizer_id, True)


def unblock_organizer(organizer_id: int) -> User:
    return set_organizer_blocked(organizer_id, False)


def get_organizer_events(organizer_id: int) -> list[Event]:
    return (
        Event.query
        .filter(
            Event.organizer_id == organizer_id,
            Event.status == "published",
        )
        .order_by(Event.event_datetime.asc())
        .all()
    )


def get_organizer_archived_events(organizer_id: int) -> list[Event]:
    return (
        Event.query
        .filter(
            Event.organizer_id == organizer_id,
            Event.status == "archived",
        )
        .order_by(Event.event_datetime.desc())
        .all()
    )

def get_organizer_or_404(organizer_id: int) -> User:
    return get_organizer_by_id(organizer_id)