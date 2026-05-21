import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import {
  getEventComplaints,
  getReviewComplaints,
  resolveEventComplaint,
  keepReviewAfterComplaint,
  deleteReviewAfterComplaint
} from "../../api/complaintsApi.js";

function formatDate(value) {
  if (!value) {
    return "Дата не указана";
  }

  return new Date(value).toLocaleString("ru-RU");
}

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

export function AdminComplaintsPage() {
  const [complaintType, setComplaintType] = useState("events");
  const [eventStatusFilter, setEventStatusFilter] = useState("blocked");

  const [eventComplaints, setEventComplaints] = useState([]);
  const [reviewComplaints, setReviewComplaints] = useState([]);

  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  async function loadComplaints() {
    setIsLoading(true);
    setError("");

    try {
      if (complaintType === "events") {
        const response = await getEventComplaints({
          status: eventStatusFilter
        });

        setEventComplaints(response.complaints || []);
      } else {
        const response = await getReviewComplaints();
        setReviewComplaints(response.complaints || []);
      }
    } catch (requestError) {
      setError(requestError.message || "Не удалось загрузить жалобы.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    loadComplaints();
  }, [complaintType, eventStatusFilter]);

  async function executeAction(action, successMessage) {
    setError("");
    setMessage("");

    try {
      const response = await action();
      setMessage(response.message || successMessage);
      await loadComplaints();
    } catch (requestError) {
      setError(requestError.message || "Не удалось выполнить действие.");
    }
  }

  return (
    <main className="page">
      <section className="title-box">
        <h1>Кабинет администратора</h1>
      </section>

      <section className="main">
        <aside className="sidebar">
          <h2>Разделы</h2>

          <div className="menu">
            <Link className="menu-item active" to="/admin/complaints">
              <div>Жалобы</div>
            </Link>

            <Link className="menu-item" to="/admin/users">
              <div>Пользователи</div>
            </Link>

            <Link className="menu-item" to="/admin/organizers">
              <div>Организаторы</div>
            </Link>
          </div>
        </aside>

        <section className="content">
          <div className="section-head">
            <div>
              <h2>Жалобы</h2>
              <p className="muted">
                Администратор рассматривает жалобы на карточки мероприятий и отзывы.
              </p>
            </div>
          </div>

          {error && <div className="error-box">{error}</div>}
          {message && <div className="success-box">{message}</div>}

          <div className="tabs">
            <button
              className={`tab-button ${complaintType === "events" ? "active" : ""}`}
              type="button"
              onClick={() => setComplaintType("events")}
            >
              Жалобы на карточки мероприятий
            </button>

            <button
              className={`tab-button ${complaintType === "reviews" ? "active" : ""}`}
              type="button"
              onClick={() => setComplaintType("reviews")}
            >
              Жалобы на отзывы
            </button>
          </div>

          {complaintType === "events" && (
            <div className="toolbar">
              <div className="field">
                <label htmlFor="event-status-filter">Статус карточки</label>
                <select
                  id="event-status-filter"
                  value={eventStatusFilter}
                  onChange={(event) => setEventStatusFilter(event.target.value)}
                >
                  <option value="blocked">Заблокирована</option>
                  <option value="on_review">На рассмотрении администратора</option>
                  <option value="published">Опубликована</option>
                  <option value="archived">Архивная</option>
                </select>
              </div>
            </div>
          )}

          {isLoading && <div className="loading-screen">Загрузка жалоб...</div>}

          {!isLoading && complaintType === "events" && eventComplaints.length === 0 && (
            <div className="empty-state">
              <h3>Жалоб на карточки нет</h3>
              <p>Жалобы выбранного типа отсутствуют.</p>
            </div>
          )}

          {!isLoading && complaintType === "events" && eventComplaints.length > 0 && (
            <div className="table-wrapper">
              <table className="table">
                <thead>
                  <tr>
                    <th>Мероприятие</th>
                    <th>Тип жалобы</th>
                    <th>Статус карточки</th>
                    <th>Дата изменения</th>
                    <th>Действия</th>
                  </tr>
                </thead>

                <tbody>
                  {eventComplaints.map((complaint) => (
                    <tr key={complaint.id}>
                      <td>{complaint.event?.title || "Без названия"}</td>
                      <td>{complaint.complaint_type}</td>
                      <td>{getStatusLabel(complaint.event?.status)}</td>
                      <td>{formatDate(complaint.changed_at || complaint.last_changed_at)}</td>
                      <td>
                        <div className="table-actions">
                          {complaint.event?.id && (
                            <Link
                              className="btn btn-outline"
                              to={`/admin/events/${complaint.event.id}`}
                            >
                              Открыть карточку
                            </Link>
                          )}

                          <button
                            className="btn btn-outline"
                            type="button"
                            onClick={() =>
                              executeAction(
                                () => resolveEventComplaint(complaint.id, "restore_event"),
                                "Карточка восстановлена."
                              )
                            }
                          >
                            Восстановить
                          </button>

                          <button
                            className="btn btn-outline"
                            type="button"
                            onClick={() =>
                              executeAction(
                                () => resolveEventComplaint(complaint.id, "keep_blocked"),
                                "Карточка оставлена заблокированной."
                              )
                            }
                          >
                            Оставить заблокированной
                          </button>

                          <button
                            className="btn btn-danger"
                            type="button"
                            onClick={() =>
                              executeAction(
                                () => resolveEventComplaint(complaint.id, "block_organizer"),
                                "Организатор заблокирован."
                              )
                            }
                          >
                            Заблокировать организатора
                          </button>

                          <button
                            className="btn btn-danger"
                            type="button"
                            onClick={() =>
                              executeAction(
                                () => resolveEventComplaint(complaint.id, "block_false_reporter"),
                                "Пользователь заблокирован за ложную жалобу."
                              )
                            }
                          >
                            Заблокировать заявителя
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {!isLoading && complaintType === "reviews" && reviewComplaints.length === 0 && (
            <div className="empty-state">
              <h3>Жалоб на отзывы нет</h3>
              <p>На текущий момент спорных отзывов нет.</p>
            </div>
          )}

          {!isLoading && complaintType === "reviews" && reviewComplaints.length > 0 && (
            <div className="table-wrapper">
              <table className="table">
                <thead>
                  <tr>
                    <th>Мероприятие</th>
                    <th>Автор отзыва</th>
                    <th>Оценка</th>
                    <th>Дата жалобы</th>
                    <th>Действия</th>
                  </tr>
                </thead>

                <tbody>
                  {reviewComplaints.map((complaint) => (
                    <tr key={complaint.id}>
                      <td>{complaint.event?.title || "Без названия"}</td>
                      <td>{complaint.review?.author?.full_name || "Пользователь"}</td>
                      <td>{complaint.review?.rating}</td>
                      <td>{formatDate(complaint.created_at || complaint.last_changed_at)}</td>
                      <td>
                        <div className="table-actions">
                          {complaint.event?.id && complaint.review?.id && (
                            <Link
                              className="btn btn-outline"
                              to={`/admin/events/${complaint.event.id}/past?review=${complaint.review.id}`}
                            >
                              Перейти к отзыву
                            </Link>
                          )}

                          <button
                            className="btn btn-outline"
                            type="button"
                            onClick={() =>
                              executeAction(
                                () => keepReviewAfterComplaint(complaint.id),
                                "Отзыв оставлен после проверки."
                              )
                            }
                          >
                            Оставить отзыв
                          </button>

                          <button
                            className="btn btn-danger"
                            type="button"
                            onClick={() =>
                              executeAction(
                                () => deleteReviewAfterComplaint(complaint.id),
                                "Отзыв удален, пользователь заблокирован."
                              )
                            }
                          >
                            Удалить отзыв и заблокировать пользователя
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </section>
    </main>
  );
}