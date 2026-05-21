from flask import Blueprint, jsonify, request

from app.auth.decorators import admin_required, legal_documents_required
from app.reviews.schemas import (
    organizer_rating_to_dict,
    review_to_dict,
    validate_organizer_rating_payload,
    validate_review_payload,
)
from app.reviews.services import (
    ReviewError,
    create_event_review,
    delete_event_review,
    delete_organizer_rating,
    get_event_rating,
    get_event_reviews,
    get_organizer_rating,
    set_organizer_rating,
)


reviews_bp = Blueprint("reviews", __name__)


def success_response(data: dict | None = None, status_code: int = 200):
    payload = {"success": True}

    if data is not None:
        payload.update(data)

    response = jsonify(payload)
    response.status_code = status_code

    return response


def error_response(status_code: int, message: str, details: dict | None = None):
    payload = {
        "success": False,
        "error": {
            "code": status_code,
            "message": message,
        },
    }

    if details is not None:
        payload["error"]["details"] = details

    response = jsonify(payload)
    response.status_code = status_code

    return response


@reviews_bp.get("/health")
def reviews_health():
    return success_response(
        {
            "module": "reviews",
            "message": "Модуль отзывов подключен.",
        }
    )


@reviews_bp.get("/events/<int:event_id>")
@legal_documents_required
def event_reviews_route(user, event_id: int):
    sort = request.args.get("sort", "new").strip()

    try:
        reviews = get_event_reviews(user, event_id, sort=sort, include_hidden=False)
        rating = get_event_rating(event_id, include_hidden=False)
    except ReviewError as error:
        return error_response(error.status_code, error.message, error.details)

    return success_response(
        {
            "reviews": [review_to_dict(review, user) for review in reviews],
            "rating": rating,
        }
    )


@reviews_bp.get("/admin/events/<int:event_id>")
@admin_required
def admin_event_reviews_route(user, event_id: int):
    sort = request.args.get("sort", "new").strip()

    try:
        reviews = get_event_reviews(user, event_id, sort=sort, include_hidden=True)
        rating = get_event_rating(event_id, include_hidden=True)
    except ReviewError as error:
        return error_response(error.status_code, error.message, error.details)

    return success_response(
        {
            "reviews": [review_to_dict(review, user, include_hidden=True) for review in reviews],
            "rating": rating,
        }
    )


@reviews_bp.post("/events/<int:event_id>")
@legal_documents_required
def create_event_review_route(user, event_id: int):
    if request.content_type and request.content_type.startswith("multipart/form-data"):
        data = {
            "rating": request.form.get("rating"),
            "comment": request.form.get("comment"),
        }
        photos = request.files.getlist("photos")
    else:
        data = request.get_json(silent=True) or {}
        photos = []

    try:
        payload = validate_review_payload(data)
        review = create_event_review(user, event_id, payload, photos)
    except ValueError as error:
        return error_response(400, "Ошибка заполнения формы отзыва.", error.args[0])
    except ReviewError as error:
        return error_response(error.status_code, error.message, error.details)

    return success_response(
        {
            "message": "Отзыв опубликован.",
            "review": review_to_dict(review, user),
            "rating": get_event_rating(event_id, include_hidden=False),
        },
        status_code=201,
    )


@reviews_bp.delete("/<int:review_id>")
@legal_documents_required
def delete_event_review_route(user, review_id: int):
    try:
        delete_event_review(user, review_id)
    except ReviewError as error:
        return error_response(error.status_code, error.message, error.details)

    return success_response(
        {
            "message": "Отзыв удален.",
        }
    )


@reviews_bp.get("/organizers/<int:organizer_id>/rating")
@legal_documents_required
def get_organizer_rating_route(user, organizer_id: int):
    rating = get_organizer_rating(user, organizer_id)

    return success_response(
        {
            "rating": organizer_rating_to_dict(rating),
        }
    )


@reviews_bp.put("/organizers/<int:organizer_id>/rating")
@legal_documents_required
def set_organizer_rating_route(user, organizer_id: int):
    data = request.get_json(silent=True) or {}

    try:
        payload = validate_organizer_rating_payload(data)
        rating = set_organizer_rating(user, organizer_id, payload["rating"])
    except ValueError as error:
        return error_response(400, "Ошибка заполнения оценки организатора.", error.args[0])
    except ReviewError as error:
        return error_response(error.status_code, error.message, error.details)

    return success_response(
        {
            "message": "Оценка организатора сохранена.",
            "rating": organizer_rating_to_dict(rating),
        }
    )


@reviews_bp.delete("/organizers/<int:organizer_id>/rating")
@legal_documents_required
def delete_organizer_rating_route(user, organizer_id: int):
    try:
        delete_organizer_rating(user, organizer_id)
    except ReviewError as error:
        return error_response(error.status_code, error.message, error.details)

    return success_response(
        {
            "message": "Оценка организатора удалена.",
        }
    )