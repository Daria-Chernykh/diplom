from flask import Blueprint, jsonify, request

from app.auth.decorators import admin_required, legal_documents_required
from app.complaints.schemas import (
    event_complaint_to_dict,
    review_complaint_to_dict,
    validate_event_complaint_payload,
)
from app.complaints.services import (
    ComplaintError,
    block_event_organizer,
    block_false_event_complainant,
    create_event_complaint,
    create_review_complaint,
    delete_review_and_block_author,
    get_event_complaints,
    get_review_complaints,
    keep_event_blocked,
    keep_review_after_complaint,
    reject_event_complaint,
    restore_event_after_complaint,
)

complaints_bp = Blueprint("complaints", __name__)


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


@complaints_bp.get("/health")
def complaints_health():
    return success_response(
        {
            "module": "complaints",
            "message": "Модуль жалоб подключен.",
        }
    )


@complaints_bp.post("/events/<int:event_id>")
@legal_documents_required
def create_event_complaint_route(user, event_id: int):
    data = request.get_json(silent=True) or {}

    try:
        payload = validate_event_complaint_payload(data)
        complaint = create_event_complaint(user, event_id, payload)
    except ValueError as error:
        return error_response(
            400,
            "Ошибка заполнения жалобы.",
            error.args[0] if error.args else None,
        )
    except ComplaintError as error:
        return error_response(error.status_code, error.message, error.details)

    return success_response(
        {
            "message": "Жалоба отправлена.",
            "complaint": event_complaint_to_dict(complaint),
        },
        status_code=201,
    )


@complaints_bp.post("/reviews/<int:review_id>")
@legal_documents_required
def create_review_complaint_route(user, review_id: int):
    try:
        complaint = create_review_complaint(user, review_id)
    except ComplaintError as error:
        return error_response(error.status_code, error.message, error.details)

    return success_response(
        {
            "message": "Жалоба на отзыв отправлена.",
            "complaint": review_complaint_to_dict(complaint),
        },
        status_code=201,
    )


@complaints_bp.get("/admin/events")
@admin_required
def admin_list_event_complaints_route(user):
    status = request.args.get("status", "").strip()

    if status not in {"", "blocked", "review", "published", "archived"}:
        status = ""

    complaints = get_event_complaints(status=status or None)

    return success_response(
        {
            "complaints": [event_complaint_to_dict(complaint) for complaint in complaints],
        }
    )


@complaints_bp.get("/admin/reviews")
@admin_required
def admin_list_review_complaints_route(user):
    complaints = get_review_complaints()

    return success_response(
        {
            "complaints": [review_complaint_to_dict(complaint) for complaint in complaints],
        }
    )


@complaints_bp.post("/admin/events/<int:complaint_id>/restore")
@admin_required
def admin_restore_event_route(user, complaint_id: int):
    try:
        event = restore_event_after_complaint(complaint_id)
    except ComplaintError as error:
        return error_response(error.status_code, error.message, error.details)

    return success_response(
        {
            "message": "Карточка мероприятия восстановлена.",
            "event_id": event.id,
        }
    )


@complaints_bp.post("/admin/events/<int:complaint_id>/reject")
@admin_required
def admin_reject_event_complaint_route(user, complaint_id: int):
    try:
        event = reject_event_complaint(complaint_id)
    except ComplaintError as error:
        return error_response(error.status_code, error.message, error.details)

    return success_response(
        {
            "message": "Жалоба отклонена, карточка опубликована.",
            "event_id": event.id,
        }
    )


@complaints_bp.post("/admin/events/<int:complaint_id>/keep-blocked")
@admin_required
def admin_keep_event_blocked_route(user, complaint_id: int):
    try:
        event = keep_event_blocked(complaint_id)
    except ComplaintError as error:
        return error_response(error.status_code, error.message, error.details)

    return success_response(
        {
            "message": "Карточка оставлена заблокированной.",
            "event_id": event.id,
        }
    )


@complaints_bp.post("/admin/events/<int:complaint_id>/block-organizer")
@admin_required
def admin_block_event_organizer_route(user, complaint_id: int):
    try:
        event = block_event_organizer(complaint_id)
    except ComplaintError as error:
        return error_response(error.status_code, error.message, error.details)

    return success_response(
        {
            "message": "Организатор заблокирован.",
            "event_id": event.id,
        }
    )


@complaints_bp.post("/admin/events/<int:complaint_id>/block-complainant")
@admin_required
def admin_block_false_event_complainant_route(user, complaint_id: int):
    try:
        event = block_false_event_complainant(complaint_id)
    except ComplaintError as error:
        return error_response(error.status_code, error.message, error.details)

    return success_response(
        {
            "message": "Пользователь, подавший ложную жалобу, заблокирован.",
            "event_id": event.id,
        }
    )


@complaints_bp.post("/admin/reviews/<int:complaint_id>/keep")
@admin_required
def admin_keep_review_route(user, complaint_id: int):
    try:
        review = keep_review_after_complaint(complaint_id)
    except ComplaintError as error:
        return error_response(error.status_code, error.message, error.details)

    return success_response(
        {
            "message": "Отзыв оставлен после проверки.",
            "review_id": review.id,
        }
    )


@complaints_bp.post("/admin/reviews/<int:complaint_id>/delete-and-block")
@admin_required
def admin_delete_review_and_block_author_route(user, complaint_id: int):
    try:
        delete_review_and_block_author(complaint_id)
    except ComplaintError as error:
        return error_response(error.status_code, error.message, error.details)

    return success_response(
        {
            "message": "Отзыв удален, автор отзыва заблокирован.",
        }
    )