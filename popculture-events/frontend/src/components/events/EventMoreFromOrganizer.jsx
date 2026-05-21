import { Link } from "react-router-dom";

export function EventMoreFromOrganizer({ event }) {
  const organizerName =
    event.organizer?.organization_name || event.organizer?.full_name || "организатора";

  return (
    <section className="more-events">
      <div className="section-head">
        <h2>Ещё события от {organizerName}</h2>
        <Link className="btn btn-outline" to={`/organizers/${event.organizer_id}`}>
          Открыть страницу организатора
        </Link>
      </div>

      <p className="muted">
        Блок со списком других мероприятий организатора будет подключен после реализации расширенного
        каталога по организатору.
      </p>
    </section>
  );
}