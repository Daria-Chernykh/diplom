from app.common.validators import validate_rating
from app.models import EventReview, File, OrganizerRating


def file_to_dict(file: File | None) -> dict | None:
    if file is None:
        return None

    return {
        "id": file.id,
        "file_url": f"/api/files/view/{file.file_path}",
        "original_filename": file.original_filename,
        "mime_type": file.mime_type,
    }


def get_review_photos(review: EventReview) -> list[File]:
    return (
        File.query
        .filter(
            File.entity_type == "review",
            File.entity_id == review.id,
        )
        .order_by(File.id.asc())
        .all()
    )


def review_to_dict(review: EventReview, current_user=None, include_hidden: bool = False) -> dict:
    user = review.user
    photos = get_review_photos(review)

    return {
        "id": review.id,
        "event_id": review.event_id,
        "user_id": review.user_id,
        "rating": review.rating,
        "comment": review.comment,
        "is_hidden": review.is_hidden,
        "created_at": review.created_at.isoformat() if review.created_at else None,
        "is_own": current_user is not None and review.user_id == current_user.id,
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
        }
        if user
        else None,
        "photos": [file_to_dict(file) for file in photos],
    }


def organizer_rating_to_dict(rating: OrganizerRating | None) -> dict | None:
    if rating is None:
        return None

    return {
        "id": rating.id,
        "organizer_id": rating.organizer_id,
        "user_id": rating.user_id,
        "rating": rating.rating,
    }


def validate_review_payload(data: dict) -> dict:
    errors = {}

    rating = validate_rating(data, "rating", errors)

    comment = str(data.get("comment") or "").strip()

    if len(comment) > 3000:
        errors["comment"] = "Комментарий не должен превышать 3000 символов."

    if errors:
        raise ValueError(errors)

    return {
        "rating": rating,
        "comment": comment if comment else None,
    }


def validate_organizer_rating_payload(data: dict) -> dict:
    errors = {}

    rating = validate_rating(data, "rating", errors)

    if errors:
        raise ValueError(errors)

    return {
        "rating": rating,
    }