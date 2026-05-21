import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { getOrganizerArchive, getOrganizerById } from "../../api/organizersApi.js";
import { OrganizerRatingBlock } from "../../components/organizers/OrganizerRatingBlock.jsx";

function getRatingLabel(ratingInfo) {
  if (!ratingInfo || ratingInfo.average_rating === null || ratingInfo.average_rating === undefined) {
    return "Рейтинг пока не сформирован";
  }

  return `★ ${ratingInfo.average_rating}`;
}

function getEventRatingLabel(event) {
  const rating = event.event_rating;

  if (!rating || rating.average_rating === null || rating.average_rating === undefined) {
    return null;
  }

  return `★ ${rating.average_rating} · отзывов: ${rating.reviews_count}`;
}

export function OrganizerPublicPage() {
  const { organizerId } = useParams();

  const [organizer, setOrganizer] = useState(null);
  const [events, setEvents] = useState([]);
  const [archiveEvents, setArchiveEvents] = useState([]);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadOrganizer() {
      setIsLoading(true);
      setError("");

      try {
        const [organizerResponse, archiveResponse] = await Promise.all([
          getOrganizerById(organizerId),
          getOrganizerArchive(organizerId)
        ]);

        setOrganizer(organizerResponse.organizer);
        setEvents(organizerResponse.events || []);
        setArchiveEvents(archiveResponse.events || []);
      } catch (requestError) {
        setError(requestError.message || "Не удалось загрузить страницу организатора.");
      } finally {
        setIsLoading(false);
      }
    }

    loadOrganizer();
  }, [organizerId]);

  if (isLoading) {
    return <div className="loading-screen">Загрузка организатора...</div>;
  }

  if (error) {
    return (
      <main className="page">
        <section className="card">
          <h1>Организатор недоступен</h1>
          <div className="error-box">{error}</div>
        </section>
      </main>
    );
  }

  if (!organizer) {
    return (
      <main className="page">
        <section className="card">
          <h1>Организатор не найден</h1>
        </section>
      </main>
    );
  }

  return (
    <main className="page">
      <section className="organizer-hero">
        <div>
          <h1>{organizer.organization_name || organizer.full_name}</h1>
          <p>{organizer.organization_description || "Описание организатора пока не заполнено."}</p>
        </div>

        <div className="organizer-rating-badge">
          {getRatingLabel(organizer.organizer_rating)}
        </div>
      </section>

      <OrganizerRatingBlock
        organizer={organizer}
        onChanged={(updatedOrganizer) => setOrganizer(updatedOrganizer)}
      />

      <section className="content single-column-content">
        <div className="section-head">
          <h2>Актуальные мероприятия</h2>
        </div>

        <div className="event-list">
          {events.length === 0 && (
            <div className="card">
              <p className="muted">Актуальных мероприятий пока нет.</p>
            </div>
          )}

          {events.map((event) => (
            <article className="event-row-card" key={event.id}>
              <div className="event-row-image"></div>

              <div className="event-row-body">
                <div className="event-row-top">
                  <h3>{event.title}</h3>
                  <span className="status active">Опубликовано</span>
                </div>

                <p className="event-desc">{event.short_description}</p>

                <div className="meta">
                  <div className="meta-item">
                    {event.event_datetime
                      ? new Date(event.event_datetime).toLocaleString("ru-RU")
                      : "Дата не указана"}
                  </div>

                  <div className="meta-item">{event.location}</div>

                  {event.organizer_rating !== null && event.organizer_rating !== undefined && (
                    <div className="meta-item">Рейтинг организатора: ★ {event.organizer_rating}</div>
                  )}
                </div>

                <div className="footer-row">
                  <span className="badge">
                    {event.tags.map((tag) => tag.name).join(" · ") || "Без тегов"}
                  </span>

                  <Link className="btn btn-outline" to={`/events/${event.id}`}>
                    Открыть
                  </Link>
                </div>
              </div>
            </article>
          ))}
        </div>
      </section>

      <section className="content single-column-content">
        <div className="section-head">
          <h2>Прошедшие мероприятия</h2>
        </div>

        <div className="event-list">
          {archiveEvents.length === 0 && (
            <div className="card">
              <p className="muted">Прошедших мероприятий пока нет.</p>
            </div>
          )}

          {archiveEvents.map((event) => {
            const eventRatingLabel = getEventRatingLabel(event);

            return (
              <article className="event-row-card" key={event.id}>
                <div className="event-row-image"></div>

                <div className="event-row-body">
                  <div className="event-row-top">
                    <h3>{event.title}</h3>
                    <span className="status">Проведено</span>
                  </div>

                  <p className="event-desc">{event.short_description}</p>

                  <div className="meta">
                    <div className="meta-item">
                      {event.event_datetime
                        ? new Date(event.event_datetime).toLocaleDateString("ru-RU")
                        : "Дата не указана"}
                    </div>

                    <div className="meta-item">{event.location}</div>

                    {eventRatingLabel && <div className="meta-item">{eventRatingLabel}</div>}
                  </div>

                  <div className="footer-row">
                    <span className="badge">
                      {event.tags.map((tag) => tag.name).join(" · ") || "Без тегов"}
                    </span>

                    <Link className="btn btn-outline" to={`/events/${event.id}`}>
                      Открыть
                    </Link>
                  </div>
                </div>
              </article>
            );
          })}
        </div>
      </section>
    </main>
  );
}