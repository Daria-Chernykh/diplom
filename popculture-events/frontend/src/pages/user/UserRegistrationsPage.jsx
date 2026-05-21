import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { cancelRegistration, getMyRegistrations } from "../../api/registrationsApi.js";

function getStatusLabel(status) {
  if (status === "pending") {
    return "Ожидает подтверждения";
  }

  if (status === "registered") {
    return "Зарегистрирован";
  }

  if (status === "rejected") {
    return "Отклонено";
  }

  if (status === "canceled") {
    return "Отменено";
  }

  return status;
}

function getRegistrationTypeLabel(value) {
  if (value === "internal") {
    return "Внутренняя регистрация";
  }

  if (value === "external") {
    return "Внешняя регистрация";
  }

  return "Без регистрации";
}

export function UserRegistrationsPage() {
  const [registrations, setRegistrations] = useState([]);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  async function loadRegistrations() {
    setIsLoading(true);
    setError("");

    try {
      const response = await getMyRegistrations();
      setRegistrations(response.registrations || []);
    } catch (requestError) {
      setError(requestError.message || "Не удалось загрузить регистрации.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    loadRegistrations();
  }, []);

  async function handleCancel(registrationId) {
    setError("");
    setMessage("");

    try {
      await cancelRegistration(registrationId);
      await loadRegistrations();
      setMessage("Регистрация отменена.");
    } catch (requestError) {
      setError(requestError.message || "Не удалось отменить регистрацию.");
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

            <Link className="menu-item active" to="/user/registrations">
              <div>Мои регистрации</div>
            </Link>

            <Link className="menu-item" to="/user/favorites">
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
            <h2>Мои регистрации</h2>
          </div>

          {error && <div className="error-box">{error}</div>}
          {message && <div className="success-box">{message}</div>}

          {isLoading && <div className="loading-screen">Загрузка регистраций...</div>}

          {!isLoading && (
            <div className="event-list">
              {registrations.length === 0 && (
                <div className="card">
                  <p className="muted">Регистраций пока нет.</p>
                </div>
              )}

              {registrations.map((registration) => (
                <article className="event-row-card" key={registration.id}>
                  <div className="event-row-image"></div>

                  <div className="event-row-body">
                    <div className="event-row-top">
                      <h3>{registration.event.title}</h3>
                      <span className="status active">{getStatusLabel(registration.status)}</span>
                    </div>

                    <p className="event-desc">{registration.event.short_description}</p>

                    <div className="meta">
                      <div className="meta-item">
                        {registration.event.event_datetime
                          ? new Date(registration.event.event_datetime).toLocaleString("ru-RU")
                          : "Дата не указана"}
                      </div>

                      <div className="meta-item">{registration.event.location}</div>

                      <div className="meta-item">
                        {getRegistrationTypeLabel(registration.event.registration_type)}
                      </div>

                      <div className="meta-item">
                        Отправлено:{" "}
                        {registration.submitted_at
                          ? new Date(registration.submitted_at).toLocaleString("ru-RU")
                          : "—"}
                      </div>
                    </div>

                    <div className="footer-row">
                      <span className="badge">
                        {registration.event.tags.map((tag) => tag.name).join(" · ") || "Без тегов"}
                      </span>

                      <div className="actions-row">
                        <Link className="btn btn-outline" to={`/events/${registration.event_id}`}>
                          Перейти к мероприятию
                        </Link>

                        {["pending", "registered"].includes(registration.status) && (
                          <button
                            className="btn btn-danger"
                            type="button"
                            onClick={() => handleCancel(registration.id)}
                          >
                            {registration.status === "pending"
                              ? "Отменить заявку"
                              : registration.event.registration_type === "external"
                                ? "Отменить подтверждение"
                                : "Отменить регистрацию"}
                          </button>
                        )}
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