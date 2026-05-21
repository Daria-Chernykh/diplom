import { Link } from "react-router-dom";

export function AdminCabinetPage() {
  return (
    <main className="page">
      <section className="title-box">
        <h1>Личный кабинет администратора</h1>
      </section>

      <section className="main">
        <aside className="sidebar">
          <h2>Разделы</h2>

          <div className="menu">
            <Link className="menu-item active" to="/admin">
              <div>Панель администратора</div>
            </Link>

            <Link className="menu-item" to="/admin/complaints">
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
              <h2>Административная панель</h2>
              <p className="muted">
                В этом разделе выполняется модерация жалоб, просмотр пользователей
                и управление организаторами.
              </p>
            </div>
          </div>

          <div className="cards-grid">
            <article className="card">
              <h3>Жалобы</h3>
              <p>
                Просмотр жалоб на карточки мероприятий и отзывов. Карточки могут
                иметь состояния: опубликована, заблокирована, на рассмотрении
                администратора и архивная.
              </p>

              <Link className="btn btn-primary" to="/admin/complaints">
                Перейти к жалобам
              </Link>
            </article>

            <article className="card">
              <h3>Пользователи</h3>
              <p>
                Просмотр списка пользователей, поиск, блокировка и разблокировка
                учетных записей.
              </p>

              <Link className="btn btn-primary" to="/admin/users">
                Перейти к пользователям
              </Link>
            </article>

            <article className="card">
              <h3>Организаторы</h3>
              <p>
                Просмотр организаторов, рейтингов, статусов и блокировка учетных
                записей организаторов.
              </p>

              <Link className="btn btn-primary" to="/admin/organizers">
                Перейти к организаторам
              </Link>
            </article>
          </div>
        </section>
      </section>
    </main>
  );
}