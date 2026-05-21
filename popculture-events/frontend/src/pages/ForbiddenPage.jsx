import { Link } from "react-router-dom";

import { useAuth } from "../store/AuthContext.jsx";

export function ForbiddenPage() {
  const { user, logout } = useAuth();

  return (
    <main className="page">
      <section className="card">
        <h1>Доступ запрещен</h1>

        {user?.is_blocked ? (
          <p className="muted">
            Учетная запись заблокирована. Доступ к функциям системы недоступен.
          </p>
        ) : (
          <p className="muted">
            У учетной записи недостаточно прав для открытия этой страницы.
          </p>
        )}

        <div className="form-actions">
          <Link className="btn btn-outline" to="/">
            На главную
          </Link>

          <button className="btn btn-primary" type="button" onClick={logout}>
            Выйти
          </button>
        </div>
      </section>
    </main>
  );
}