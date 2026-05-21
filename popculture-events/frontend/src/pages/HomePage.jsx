import { Link } from "react-router-dom";

import { useAuth } from "../store/AuthContext.jsx";

export function HomePage() {
  const { user, isAuthenticated } = useAuth();

  return (
    <main className="page">
      <section className="card">
        <h1>PopCulture Events</h1>

        <p className="muted">
          Веб-ориентированная информационная система для управления мероприятиями
          в сфере популярной культуры.
        </p>

        {!isAuthenticated && (
          <div className="form-actions">
            <Link className="btn btn-outline" to="/login">
              Войти
            </Link>

            <Link className="btn btn-primary" to="/register">
              Зарегистрироваться
            </Link>
          </div>
        )}

        {isAuthenticated && (
          <p className="muted">
            Вы вошли как: <strong>{user.email}</strong>. Роль:{" "}
            <strong>{user.role}</strong>.
          </p>
        )}

        <div className="form-actions">
          <Link className="btn btn-outline" to="/events">
            Перейти к каталогу мероприятий
          </Link>

          <Link className="btn btn-outline" to="/organizers">
            Посмотреть организаторов
          </Link>
        </div>
      </section>
    </main>
  );
}