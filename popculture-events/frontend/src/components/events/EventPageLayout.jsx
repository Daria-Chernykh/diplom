import { Link } from "react-router-dom";

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

function getEventRatingLabel(event) {
  const rating = event.event_rating;

  if (!rating || rating.average_rating === null || rating.average_rating === undefined) {
    return null;
  }

  return `★ ${rating.average_rating} · отзывов: ${rating.reviews_count}`;
}

function getOrganizerRatingLabel(event) {
  if (event.organizer_rating === null || event.organizer_rating === undefined) {
    return null;
  }

  return `★ ${event.organizer_rating}`;
}

export function EventPageLayout({ event, warning, actions, children }) {
  const eventRatingLabel = getEventRatingLabel(event);
  const organizerRatingLabel = getOrganizerRatingLabel(event);

  return (
    <main className="event-page">
      <section className="event-hero">
        <div className="event-cover"></div>

        <div className="event-main-info">
          <div className="event-status-row">
            <span className="status active">
              {event.status === "archived" ? "Проведено" : "Опубликовано"}
            </span>

            <span className="status">{event.event_format === "online" ? "Онлайн" : "Офлайн"}</span>
          </div>

          <h1>{event.title}</h1>

          <p>{event.short_description}</p>

          <div className="event-meta-grid">
            <div className="event-meta-card">
              <strong>Дата и время</strong>
              <span>
                {event.event_datetime
                  ? new Date(event.event_datetime).toLocaleString("ru-RU")
                  : "Дата не указана"}
              </span>
            </div>

            <div className="event-meta-card">
              <strong>Место проведения</strong>
              <span>{event.location}</span>
            </div>

            <div className="event-meta-card">
              <strong>Стоимость</strong>
              <span>{getPriceLabel(event)}</span>
            </div>

            <div className="event-meta-card">
              <strong>Организатор</strong>
              <span>
                <Link to={`/organizers/${event.organizer_id}`}>
                  {event.organizer?.organization_name || event.organizer?.full_name || "Организатор"}
                </Link>
                {organizerRatingLabel && (
                  <span className="inline-rating"> {organizerRatingLabel}</span>
                )}
              </span>
            </div>

            {eventRatingLabel && (
              <div className="event-meta-card">
                <strong>Рейтинг мероприятия</strong>
                <span>{eventRatingLabel}</span>
              </div>
            )}
          </div>

          <div className="tags-list">
            {event.tags.map((tag) => (
              <span className="tag" key={tag.id}>
                {tag.name}
              </span>
            ))}
          </div>

          {warning}

          {actions && <div className="event-actions">{actions}</div>}
        </div>
      </section>

      <section className="event-details-grid">
        <article className="event-details-card">
          <h2>Описание</h2>
          <p>{event.long_description}</p>
        </article>

        <article className="event-details-card">
          <h2>Расписание</h2>
          <p>{event.schedule || "Расписание не указано."}</p>
        </article>

        <article className="event-details-card">
          <h2>Требования к участникам</h2>
          <p>{event.participant_requirements || "Требования не указаны."}</p>
        </article>
      </section>

      {children}
    </main>
  );
}