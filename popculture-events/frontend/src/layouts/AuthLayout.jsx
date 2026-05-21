import { NavLink, Outlet } from "react-router-dom";

export function AuthLayout() {
  return (
    <div className="auth-page">
      <header className="header">
        <div className="header-inner">
          <NavLink className="brand" to="/">
            <div>PopCulture Events</div>
          </NavLink>

          <nav className="nav">
            <NavLink to="/">Главная</NavLink>
            <NavLink to="/events">Каталог</NavLink>
            <NavLink to="/legal-documents">Документы</NavLink>
          </nav>
        </div>
      </header>

      <main className="auth-main">
        <Outlet />
      </main>
    </div>
  );
}