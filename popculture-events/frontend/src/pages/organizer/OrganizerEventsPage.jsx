import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { getOrganizerEvents } from "../../api/eventsApi.js";

function getStatusLabel(status) {
  if (status === "published") {
    return "Опубликована";
  }

  if (status === "blocked") {
    return "Заблокирована";
  }

  if (status === "on_review") {
    return "На рассмотрении администратора";
  }

  if (status === "archived") {
    return "Архивная";
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

  return "Не указан";
}

export function OrganizerEventsPage() {
  const [events, setEvents] = useState([]);
  const [status, setStatus] = useState("");

  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  async function loadEvents() {
    setIsLoading(true);
    setError("");

    try {
      const response = await getOrganizerEvents({
        status
      });

      setEvents(response.events || []);
    } catch (requestError) {
      setError(requestError.message || "Не удалось загрузить мероприятия.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    loadEvents();
  }, [status]);

  return (
    <main className="page">
      <section className="title-box">
        <h1>Мои мероприятия</h1>
      </section>

      <section className="content single-content">
        <div className="section-head">
          <div>
            <h2>Список мероприятий</h2>
            <p className="muted">
              Управление опубликованными, заблокированными и находящимися на рассмотрении карточками.
            </p>
          </div>

          <Link className="btn btn-primary" to="/organizer/events/create">
            Создать мероприятие
          </Link>
        </div>

        <div className="toolbar">
          <div className="field">
            <label htmlFor="status-filter">Статус</label>
            <select
              id="status-filter"
              value={status}
              onChange={(event) => setStatus(event.target.value)}
            >
              <option value="">Все актуальные</option>
              <option value="published">Опубликована</option>
              <option value="blocked">Заблокирована</option>
              <option value="on_review">На рассмотрении администратора</option>
            </select>
          </div>
        </div>

        {error && <div className="error-box">{error}</div>}

        {isLoading && <div className="loading-screen">Загрузка мероприятий...</div>}

        {!isLoading && events.length === 0 && (
          <div className="empty-state">
            <h3>Мероприятий пока нет</h3>
            <p>Создайте первое мероприятие, чтобы оно появилось в этом разделе.</p>
          </div>
        )}

        {!isLoading && events.length > 0 && (
          <div className="table-wrapper">
            <table className="table">
              <thead>
                <tr>
                  <th>Название</th>
                  <th>Дата</th>
                  <th>Тип регистрации</th>
                  <th>Статус</th>
                  <th>Действия</th>
                </tr>
              </thead>

              <tbody>
                {events.map((event) => (
                  <tr key={event.id}>
                    <td>{event.title}</td>
                    <td>
                      {event.event_datetime
                        ? new Date(event.event_datetime).toLocaleString("ru-RU")
                        : "Дата не указана"}
                    </td>
                    <td>{getRegistrationLabel(event.registration_type)}</td>
                    <td>{getStatusLabel(event.status)}</td>
                    <td>
                      <div className="table-actions">
                        <Link className="btn btn-outline" to={`/events/${event.id}`}>
                          Открыть
                        </Link>

                        <Link className="btn btn-outline" to={`/organizer/events/${event.id}/edit`}>
                          Редактировать
                        </Link>

                        {event.registration_type !== "none" && (
                          <Link
                            className="btn btn-outline"
                            to={`/organizer/events/${event.id}/participants`}
                          >
                            Участники
                          </Link>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </main>
  );
}