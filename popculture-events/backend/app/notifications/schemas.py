from app.models import Notification


def notification_to_dict(notification: Notification) -> dict:
    return {
        "id": notification.id,
        "user_id": notification.user_id,
        "event_id": notification.event_id,
        "organizer_id": notification.organizer_id,
        "notification_type": notification.notification_type,
        "title": notification.title,
        "message": notification.message,
        "action_url": notification.action_url,
        "is_read": notification.is_read,
        "created_at": notification.created_at.isoformat() if notification.created_at else None,
    }