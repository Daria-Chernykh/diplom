import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import {
  blockUser,
  getAdminUsers,
  unblockUser
} from "../../api/usersApi.js";

function getRoleLabel(role) {
  if (role === "admin") {
    return "Администратор";
  }

  if (role === "organizer") {
    return "Организатор";
  }

  return "Пользователь";
}

function getDate(value) {
  if (!value) {
    return "Дата не указана";
  }

  return new Date(value).toLocaleDateString("ru-RU");
}

export function AdminUsersPage() {
  const [users, setUsers] = useState([]);
  const [query, setQuery] = useState("");
  const [appliedQuery, setAppliedQuery] = useState("");

  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  async function loadUsers(searchQuery = appliedQuery) {
    setIsLoading(true);
    setError("");

    try {
      const response = await getAdminUsers({
        query: searchQuery
      });

      setUsers(response.users || []);
    } catch (requestError) {
      setError(requestError.message || "Не удалось загрузить пользователей.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    loadUsers(appliedQuery);
  }, [appliedQuery]);

  function handleSearch(event) {
    event.preventDefault();
    setAppliedQuery(query.trim());
  }

  async function handleBlock(userId) {
    setError("");
    setMessage("");

    try {
      const response = await blockUser(userId);
      setMessage(response.message || "Пользователь заблокирован.");
      await loadUsers(appliedQuery);
    } catch (requestError) {
      setError(requestError.message || "Не удалось заблокировать пользователя.");
    }
  }

  async function handleUnblock(userId) {
    setError("");
    setMessage("");

    try {
      const response = await unblockUser(userId);
      setMessage(response.message || "Пользователь разблокирован.");
      await loadUsers(appliedQuery);
    } catch (requestError) {
      setError(requestError.message || "Не удалось разблокировать пользователя.");
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

            <Link className="menu-item" to="/admin/organizers">
              <div>Организаторы</div>
            </Link>

            <Link className="menu-item active" to="/admin/users">
              <div>Пользователи</div>
            </Link>
          </div>
        </aside>

        <section className="content">
          <div className="section-head">
            <div>
              <h2>Пользователи</h2>
              <p className="muted">
                Поиск, просмотр статуса, блокировка и разблокировка пользователей.
              </p>
            </div>
          </div>

          {error && <div className="error-box">{error}</div>}
          {message && <div className="success-box">{message}</div>}

          <form className="admin-search" onSubmit={handleSearch}>
            <div className="field">
              <label htmlFor="users-query">Поиск</label>
              <input
                id="users-query"
                type="text"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Имя, email или роль"
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

          {isLoading && <div className="loading-screen">Загрузка пользователей...</div>}

          {!isLoading && users.length === 0 && (
            <div className="note">Пользователи не найдены.</div>
          )}

          {!isLoading && users.length > 0 && (
            <div className="admin-table-wrapper">
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>Пользователь</th>
                    <th>Email</th>
                    <th>Роль</th>
                    <th>Дата регистрации</th>
                    <th>Документы</th>
                    <th>Статус</th>
                    <th>Действия</th>
                  </tr>
                </thead>

                <tbody>
                  {users.map((user) => (
                    <tr key={user.id}>
                      <td>{user.full_name}</td>
                      <td>{user.email}</td>
                      <td>{getRoleLabel(user.role)}</td>
                      <td>{getDate(user.created_at)}</td>
                      <td>
                        {user.legal_documents_accepted
                          ? "Приняты"
                          : "Не приняты"}
                      </td>
                      <td>
                        <span className={user.is_blocked ? "status danger" : "status success"}>
                          {user.is_blocked ? "Заблокирован" : "Активен"}
                        </span>
                      </td>
                      <td>
                        <div className="table-actions">
                          {user.is_blocked ? (
                            <button
                              className="btn btn-outline"
                              type="button"
                              onClick={() => handleUnblock(user.id)}
                            >
                              Разблокировать
                            </button>
                          ) : (
                            <button
                              className="btn btn-danger"
                              type="button"
                              onClick={() => handleBlock(user.id)}
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