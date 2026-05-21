def favorite_to_dict(favorite) -> dict:
    return {
        "user_id": favorite.user_id,
        "event_id": favorite.event_id,
        "event": {
            "id": favorite.event.id,
            "title": favorite.event.title,
            "short_description": favorite.event.short_description,
            "event_datetime": favorite.event.event_datetime.isoformat()
            if favorite.event.event_datetime
            else None,
            "event_format": favorite.event.event_format,
            "registration_type": favorite.event.registration_type,
            "status": favorite.event.status,
        }
        if favorite.event
        else None,
    }