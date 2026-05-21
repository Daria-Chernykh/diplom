import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { getMyEvents } from "../../api/eventsApi.js";

function getRegistrationTypeLabel(value) {
  if (value === "internal") {
    return "Внутренняя регистрация";
  }

  if (value === "external") {
    return "Внешняя регистрация";
  }

  return "Без регистрации";
}

function getParticipantsText(event) {
  if (event.registration_type === "none") {
    return null;
  }

  if (typeof event.participants_count === "number") {
    return `Участников: ${event.participants_count}`;
  }

  return "Участники: —";
}

function getEventRatingText(event) {
  const rating = event.event_rating;

  if (!rating || rating.average_rating === null || rating.average_rating === undefined) {
    return null;
  }

  return `Рейтинг мероприятия: ★ ${rating.average_rating}`;
}

function getOrganizerRatingText(event) {
  if (event.organizer_rating === null || event.organizer_rating === undefined) {
    return null;
  }

  return `Рейтинг организатора: ★ ${event.organizer_rating}`;
}

export function OrganizerEventsArchivePage() {
  const [events, setEvents] = useState([]);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadArchiveEvents() {
      setIsLoading(true);
      setError("");

      try {
        const response = await getMyEvents({
          status: "archived"
        });

        setEvents(response.events || []);
      } catch (requestError) {
        setError(requestError.message || "Не удалось загрузить архив мероприятий.");
      } finally {
        setIsLoading(false);
      }
    }

    loadArchiveEvents();
  }, []);

  return (
    <main className="page">
      <section className="title-box">
        <h1>Личный кабинет организатора</h1>
      </section>

      <section className="main">
        <aside className="sidebar">
          <h2>Разделы</h2>

          <div className="menu">
            <Link className="menu-item" to="/organizer">
              <div>Профиль</div>
            </Link>

            <Link className="menu-item" to="/organizer/events">
              <div>Мои мероприятия</div>
            </Link>

            <Link className="menu-item" to="/organizer/notifications">
              <div>Уведомления</div>
            </Link>

            <Link className="menu-item active" to="/organizer/events/archive">
              <div>Архив мероприятий</div>
            </Link>
          </div>
        </aside>

        <section className="content">
          <div className="section-head">
            <h2>Архив мероприятий</h2>
          </div>

          {error && <div className="error-box">{error}</div>}

          {isLoading && <div className="loading-screen">Загрузка архива...</div>}

          {!isLoading && (
            <div className="event-list">
              {events.length === 0 && (
                <div className="card">
                  <p className="muted">Архивных мероприятий пока нет.</p>
                </div>
              )}

              {events.map((event) => {
                const participantsText = getParticipantsText(event);
                const eventRatingText = getEventRatingText(event);
                const organizerRatingText = getOrganizerRatingText(event);

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
                          {event.event_format === "online" ? "Онлайн" : "Офлайн"}
                        </div>

                        <div className="meta-item">
                          {event.event_datetime
                            ? new Date(event.event_datetime).toLocaleDateString("ru-RU")
                            : "Дата не указана"}
                        </div>

                        <div className="meta-item">
                          {getRegistrationTypeLabel(event.registration_type)}
                        </div>

                        {participantsText && <div className="meta-item">{participantsText}</div>}
                        {eventRatingText && <div className="meta-item">{eventRatingText}</div>}
                        {organizerRatingText && <div className="meta-item">{organizerRatingText}</div>}
                      </div>

                      <div className="footer-row">
                        <span className="badge">
                          {event.tags.map((tag) => tag.name).join(" · ") || "Без тегов"}
                        </span>

                        <div className="actions-row">
                          <Link className="btn btn-outline" to={`/events/${event.id}`}>
                            Открыть
                          </Link>
                        </div>
                      </div>
                    </div>
                  </article>
                );
              })}
            </div>
          )}
        </section>
      </section>
    </main>
  );
}