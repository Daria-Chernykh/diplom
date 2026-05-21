from app.events.schemas import event_to_dict
from app.models import OrganizerRating, User
from app.organizers.services import calculate_organizer_rating, organizer_to_dict


def validate_organizer_rating_payload(data: dict) -> dict:
    errors = {}

    raw_rating = data.get("rating")

    if raw_rating is None or str(raw_rating).strip() == "":
        errors["rating"] = "Выберите оценку организатора от 0 до 5."
        rating = None
    else:
        try:
            rating = int(raw_rating)
        except ValueError:
            rating = None
            errors["rating"] = "Оценка должна быть целым числом от 0 до 5."

    if rating is not None and rating not in {0, 1, 2, 3, 4, 5}:
        errors["rating"] = "Оценка должна быть от 0 до 5."

    if errors:
        raise ValueError(errors)

    return {
        "rating": rating,
    }


def organizer_rating_to_dict(rating: OrganizerRating) -> dict:
    return {
        "id": rating.id,
        "organizer_id": rating.organizer_id,
        "user_id": rating.user_id,
        "rating": rating.rating,
    }


def organizer_page_to_dict(organizer: User, events: list, current_user: User | None = None) -> dict:
    return {
        "organizer": organizer_to_dict(organizer, current_user),
        "events": [
            event_to_dict(
                event,
                calculate_organizer_rating(event.organizer_id),
            )
            for event in events
        ],
    }