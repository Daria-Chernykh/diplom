import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { getFavoriteEvents, removeFavorite } from "../../api/favoritesApi.js";

function getRegistrationTypeLabel(value) {
  if (value === "internal") {
    return "Регистрация на сайте";
  }

  if (value === "external") {
    return "Внешняя регистрация";
  }

  return "Без регистрации";
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

export function UserFavoritesPage() {
  const [events, setEvents] = useState([]);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  async function loadFavorites() {
    setIsLoading(true);
    setError("");

    try {
      const response = await getFavoriteEvents();
      setEvents(response.events || []);
    } catch (requestError) {
      setError(requestError.message || "Не удалось загрузить избранное.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    loadFavorites();
  }, []);

  async function handleRemove(eventId) {
    setError("");
    setMessage("");

    try {
      await removeFavorite(eventId);
      setEvents((current) => current.filter((event) => event.id !== eventId));
      setMessage("Мероприятие удалено из избранного.");
    } catch (requestError) {
      setError(requestError.message || "Не удалось удалить мероприятие из избранного.");
    }
  }

  return (
    <main className="page">
      <section className="title-box">
        <h1>Личный кабинет пользователя</h1>
      </section>

      <section className="main">
        <aside className="sidebar">
          <h2>Разделы</h2>

          <div className="menu">
            <Link className="menu-item" to="/user">
              <div>Профиль</div>
            </Link>

            <Link className="menu-item" to="/user/registrations">
              <div>Мои регистрации</div>
            </Link>

            <Link className="menu-item active" to="/user/favorites">
              <div>Избранное</div>
            </Link>

            <Link className="menu-item" to="/user/notifications">
              <div>Уведомления</div>
            </Link>

            <Link className="menu-item" to="/user/registrations/archive">
              <div>Архив регистраций</div>
            </Link>
          </div>
        </aside>

        <section className="content">
          <div className="section-head">
            <h2>Избранное</h2>
          </div>

          {error && <div className="error-box">{error}</div>}
          {message && <div className="success-box">{message}</div>}

          {isLoading && <div className="loading-screen">Загрузка избранного...</div>}

          {!isLoading && (
            <div className="event-list">
              {events.length === 0 && (
                <div className="card">
                  <p className="muted">В избранном пока нет мероприятий.</p>
                </div>
              )}

              {events.map((event) => (
                <article className="event-row-card" key={event.id}>
                  <div className="event-row-image"></div>

                  <div className="event-row-body">
                    <div className="event-row-top">
                      <h3>{event.title}</h3>
                      <span className="status active">Опубликована</span>
                    </div>

                    <p className="event-desc">{event.short_description}</p>

                    <div className="meta">
                      <div className="meta-item">
                        {event.event_format === "online" ? "Онлайн" : "Офлайн"}
                      </div>

                      <div className="meta-item">
                        {event.event_datetime
                          ? new Date(event.event_datetime).toLocaleString("ru-RU")
                          : "Дата не указана"}
                      </div>

                      <div className="meta-item">
                        {getRegistrationTypeLabel(event.registration_type)}
                      </div>

                      <div className="meta-item">{getPriceLabel(event)}</div>
                    </div>

                    <div className="footer-row">
                      <span className="badge">
                        {event.tags.map((tag) => tag.name).join(" · ") || "Без тегов"}
                      </span>

                      <div className="actions-row">
                        <Link className="btn btn-outline" to={`/events/${event.id}`}>
                          Открыть
                        </Link>

                        <button
                          className="btn btn-danger"
                          type="button"
                          onClick={() => handleRemove(event.id)}
                        >
                          Удалить из избранного
                        </button>
                      </div>
                    </div>
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>
      </section>
    </main>
  );
}