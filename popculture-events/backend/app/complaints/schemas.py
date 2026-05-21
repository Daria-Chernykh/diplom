from app.common.validators import validate_required_string
from app.models import EventComplaint, ReviewComplaint


EVENT_COMPLAINT_TYPES = {
    "misinformation",
    "fraud",
    "prohibited_content",
    "duplicate",
    "other",
}


def event_complaint_to_dict(complaint: EventComplaint) -> dict:
    event = complaint.event
    reporter = complaint.reporter
    complaint_date = complaint.last_changed_at

    return {
        "id": complaint.id,
        "event_id": complaint.event_id,
        "reporter_id": complaint.reporter_id,
        "complainant_id": complaint.reporter_id,
        "complaint_type": complaint.complaint_type,
        "comment": complaint.comment,
        "complaint_text": complaint.comment,
        "organizer_comment": complaint.organizer_comment,
        "last_changed_at": complaint_date.isoformat() if complaint_date else None,
        "changed_at": complaint_date.isoformat() if complaint_date else None,
        "event": {
            "id": event.id,
            "title": event.title,
            "status": event.status,
            "registration_type": event.registration_type,
            "event_datetime": event.event_datetime.isoformat() if event.event_datetime else None,
            "organizer_id": event.organizer_id,
            "organizer_name": event.organizer.full_name if event.organizer else None,
            "organization_name": event.organizer.organization_name if event.organizer else None,
        }
        if event
        else None,
        "reporter": {
            "id": reporter.id,
            "full_name": reporter.full_name,
            "email": reporter.email,
            "is_blocked": reporter.is_blocked,
        }
        if reporter
        else None,
        "complainant": {
            "id": reporter.id,
            "full_name": reporter.full_name,
            "email": reporter.email,
            "is_blocked": reporter.is_blocked,
        }
        if reporter
        else None,
    }


def review_complaint_to_dict(complaint: ReviewComplaint) -> dict:
    review = complaint.review
    event = review.event if review else None
    review_author = review.user if review else None
    reporter = complaint.reporter
    complaint_date = complaint.last_changed_at

    return {
        "id": complaint.id,
        "review_id": complaint.review_id,
        "reporter_id": complaint.reporter_id,
        "complainant_id": complaint.reporter_id,
        "created_at": complaint_date.isoformat() if complaint_date else None,
        "last_changed_at": complaint_date.isoformat() if complaint_date else None,
        "review": {
            "id": review.id,
            "rating": review.rating,
            "comment": review.comment,
            "created_at": review.created_at.isoformat() if review.created_at else None,
            "author": {
                "id": review_author.id,
                "full_name": review_author.full_name,
                "email": review_author.email,
                "is_blocked": review_author.is_blocked,
            }
            if review_author
            else None,
        }
        if review
        else None,
        "event": {
            "id": event.id,
            "title": event.title,
            "status": event.status,
            "event_datetime": event.event_datetime.isoformat() if event.event_datetime else None,
        }
        if event
        else None,
        "reporter": {
            "id": reporter.id,
            "full_name": reporter.full_name,
            "email": reporter.email,
        }
        if reporter
        else None,
        "complainant": {
            "id": reporter.id,
            "full_name": reporter.full_name,
            "email": reporter.email,
        }
        if reporter
        else None,
    }


def validate_event_complaint_payload(data: dict) -> dict:
    errors = {}

    complaint_type = validate_required_string(
        data,
        "complaint_type",
        "Тип жалобы",
        errors,
        max_length=255,
    )

    comment = str(data.get("comment") or data.get("complaint_text") or "").strip()

    if not comment:
        errors["complaint_text"] = "Описание жалобы обязательно для заполнения."
        errors["comment"] = "Описание жалобы обязательно для заполнения."

    if len(comment) > 2000:
        errors["complaint_text"] = "Описание жалобы не должно превышать 2000 символов."
        errors["comment"] = "Описание жалобы не должно превышать 2000 символов."

    if complaint_type and complaint_type not in EVENT_COMPLAINT_TYPES:
        errors["complaint_type"] = "Недопустимый тип жалобы."

    if errors:
        raise ValueError(errors)

    return {
        "complaint_type": complaint_type,
        "comment": comment,
    }