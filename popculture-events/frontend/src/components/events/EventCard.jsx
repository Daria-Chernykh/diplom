import { Link } from "react-router-dom";

function getStatusLabel(status) {
  if (status === "published") {
    return "Опубликовано";
  }

  if (status === "blocked") {
    return "Заблокировано";
  }

  if (status === "on_review") {
    return "На рассмотрении";
  }

  if (status === "archived") {
    return "Архив";
  }

  return status || "Не указан";
}

function getRegistrationLabel(registrationType) {
  if (registrationType === "internal") {
    return "Внутренняя регистрация";
  }

  if (registrationType === "external") {
    return "Внешняя регистрация";
  }

  if (registrationType === "none") {
    return "Без регистрации";
  }

  return "Тип не указан";
}

function getPriceLabel(event) {
  if (event.price_type === "free") {
    return "Бесплатно";
  }

  if (event.price_type === "fixed") {
    return event.price_value || "Фиксированная цена";
  }

  if (event.price_type === "from") {
    return event.price_value || "Цена от";
  }

  return "Стоимость не указана";
}

function getOrganizerRating(event) {
  if (
    event.organizer_rating &&
    event.organizer_rating.average_rating !== null &&
    event.organizer_rating.average_rating !== undefined
  ) {
    return `★ ${event.organizer_rating.average_rating}`;
  }

  if (
    event.organizer &&
    event.organizer.organizer_rating &&
    event.organizer.organizer_rating.average_rating !== null &&
    event.organizer.organizer_rating.average_rating !== undefined
  ) {
    return `★ ${event.organizer.organizer_rating.average_rating}`;
  }

  return "рейтинг не сформирован";
}

export function EventCard({ event }) {
  return (
    <article className="event-card">
      {event.image && (
        <img
          className="event-card-image"
          src={event.image.file_url}
          alt={event.title}
        />
      )}

      <div className="event-card-body">
        <div className="event-card-head">
          <h3>{event.title}</h3>
          <span className="status-badge">{getStatusLabel(event.status)}</span>
        </div>

        <p>{event.short_description}</p>

        <div className="event-meta">
          <span>{event.event_datetime ? new Date(event.event_datetime).toLocaleString("ru-RU") : "Дата не указана"}</span>
          <span>{event.event_format === "online" ? "Онлайн" : "Офлайн"}</span>
          <span>{getRegistrationLabel(event.registration_type)}</span>
          <span>{getPriceLabel(event)}</span>
        </div>

        {event.organizer && (
          <p className="muted">
            Организатор: {event.organizer.organization_name || event.organizer.full_name}.{" "}
            Рейтинг: {getOrganizerRating(event)}
          </p>
        )}

        {event.event_rating && event.event_rating.average_rating !== null && (
          <p className="muted">
            Рейтинг мероприятия: ★ {event.event_rating.average_rating}
          </p>
        )}

        {event.tags?.length > 0 && (
          <div className="tags-list">
            {event.tags.map((tag) => (
              <span className="tag" key={tag.id || tag.name}>
                {tag.name}
              </span>
            ))}
          </div>
        )}

        <div className="form-actions">
          <Link className="btn btn-primary" to={`/events/${event.id}`}>
            Подробнее
          </Link>
        </div>
      </div>
    </article>
  );
}