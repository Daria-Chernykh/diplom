import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import {
  blockOrganizer,
  getAdminOrganizers,
  unblockOrganizer
} from "../../api/organizersApi.js";

function getDate(value) {
  if (!value) {
    return "Дата не указана";
  }

  return new Date(value).toLocaleDateString("ru-RU");
}

function getRatingText(organizer) {
  const rating = organizer.organizer_rating?.average_rating;

  if (rating === null || rating === undefined) {
    return "Нет оценок";
  }

  return `★ ${rating}`;
}

export function AdminOrganizersPage() {
  const [organizers, setOrganizers] = useState([]);
  const [query, setQuery] = useState("");
  const [appliedQuery, setAppliedQuery] = useState("");

  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  async function loadOrganizers(searchQuery = appliedQuery) {
    setIsLoading(true);
    setError("");

    try {
      const response = await getAdminOrganizers({
        query: searchQuery
      });

      setOrganizers(response.organizers || []);
    } catch (requestError) {
      setError(requestError.message || "Не удалось загрузить организаторов.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    loadOrganizers(appliedQuery);
  }, [appliedQuery]);

  function handleSearch(event) {
    event.preventDefault();
    setAppliedQuery(query.trim());
  }

  async function handleBlock(organizerId) {
    setError("");
    setMessage("");

    try {
      const response = await blockOrganizer(organizerId);
      setMessage(response.message || "Организатор заблокирован.");
      await loadOrganizers(appliedQuery);
    } catch (requestError) {
      setError(requestError.message || "Не удалось заблокировать организатора.");
    }
  }

  async function handleUnblock(organizerId) {
    setError("");
    setMessage("");

    try {
      const response = await unblockOrganizer(organizerId);
      setMessage(response.message || "Организатор разблокирован.");
      await loadOrganizers(appliedQuery);
    } catch (requestError) {
      setError(requestError.message || "Не удалось разблокировать организатора.");
    }
  }

  return (
    <main className="page">
      <section className="title-box">
        <h1>Личный кабинет администратора</h1>
      </section>

      <section className="main">
        <aside className="sidebar">
          <h2>Разделы</h2>

          <div className="menu">
            <Link className="menu-item" to="/admin">
              <div>Жалобы</div>
            </Link>

            <Link className="menu-item active" to="/admin/organizers">
              <div>Организаторы</div>
            </Link>

            <Link className="menu-item" to="/admin/users">
              <div>Пользователи</div>
            </Link>
          </div>
        </aside>

        <section className="content">
          <div className="section-head">
            <div>
              <h2>Организаторы</h2>
              <p className="muted">
                Поиск, просмотр рейтинга, блокировка и разблокировка организаторов.
              </p>
            </div>
          </div>

          {error && <div className="error-box">{error}</div>}
          {message && <div className="success-box">{message}</div>}

          <form className="admin-search" onSubmit={handleSearch}>
            <div className="field">
              <label htmlFor="organizers-query">Поиск</label>
              <input
                id="organizers-query"
                type="text"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Название организации, имя или email"
              />
            </div>

            <button className="btn btn-primary" type="submit">
              Найти
            </button>

            <button
              className="btn btn-outline"
              type="button"
              onClick={() => {
                setQuery("");
                setAppliedQuery("");
              }}
            >
              Сбросить
            </button>
          </form>

          {isLoading && <div className="loading-screen">Загрузка организаторов...</div>}

          {!isLoading && organizers.length === 0 && (
            <div className="note">Организаторы не найдены.</div>
          )}

          {!isLoading && organizers.length > 0 && (
            <div className="admin-table-wrapper">
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>Организатор</th>
                    <th>Email</th>
                    <th>Организация</th>
                    <th>Рейтинг</th>
                    <th>Дата регистрации</th>
                    <th>Статус</th>
                    <th>Действия</th>
                  </tr>
                </thead>

                <tbody>
                  {organizers.map((organizer) => (
                    <tr key={organizer.id}>
                      <td>{organizer.full_name}</td>
                      <td>{organizer.email}</td>
                      <td>{organizer.organization_name || "Не указана"}</td>
                      <td>{getRatingText(organizer)}</td>
                      <td>{getDate(organizer.created_at)}</td>
                      <td>
                        <span className={organizer.is_blocked ? "status danger" : "status success"}>
                          {organizer.is_blocked ? "Заблокирован" : "Активен"}
                        </span>
                      </td>
                      <td>
                        <div className="table-actions">
                          <Link
                            className="btn btn-outline"
                            to={`/organizers/${organizer.id}`}
                          >
                            Страница
                          </Link>

                          {organizer.is_blocked ? (
                            <button
                              className="btn btn-outline"
                              type="button"
                              onClick={() => handleUnblock(organizer.id)}
                            >
                              Разблокировать
                            </button>
                          ) : (
                            <button
                              className="btn btn-danger"
                              type="button"
                              onClick={() => handleBlock(organizer.id)}
                            >
                              Заблокировать
                            </button>
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
      </section>
    </main>
  );
}