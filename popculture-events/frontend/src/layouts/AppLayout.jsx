import { NavLink, Outlet } from "react-router-dom";

import { useAuth } from "../store/AuthContext.jsx";

export function AppLayout() {
  const { user, isAuthenticated, logout } = useAuth();

  return (
    <>
      <header className="header">
        <div className="header-inner">
          <NavLink className="brand" to="/">
            <div>PopCulture Events</div>
          </NavLink>

          <nav className="nav">
            <NavLink to="/">Главная</NavLink>
            <NavLink to="/events">Каталог</NavLink>
            <NavLink to="/legal-documents">Документы</NavLink>

            {user?.role === "admin" && <NavLink to="/admin">Администратор</NavLink>}

            {user?.role === "organizer" && <NavLink to="/organizer">Организатор</NavLink>}

            {user?.role === "user" && <NavLink to="/user">Личный кабинет</NavLink>}
          </nav>

          <div className="actions">
            {!isAuthenticated && (
              <>
                <NavLink className="btn btn-outline" to="/login">
                  Войти
                </NavLink>

                <NavLink className="btn btn-primary" to="/register">
                  Зарегистрироваться
                </NavLink>
              </>
            )}

            {isAuthenticated && (
              <>
                <span className="status primary">{user.full_name}</span>

                <button className="btn btn-outline" type="button" onClick={logout}>
                  Выйти
                </button>
              </>
            )}
          </div>
        </div>
      </header>

      <Outlet />

      <footer className="footer">
        <div className="footer-inner">
          <NavLink to="/legal-documents">Правовые документы</NavLink>
          <NavLink to="/legal-documents">Пользовательское соглашение</NavLink>
          <NavLink to="/legal-documents">Персональные данные</NavLink>
        </div>
      </footer>
    </>
  );
}