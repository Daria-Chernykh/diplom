import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { getOrganizers } from "../../api/organizersApi.js";

export function OrganizersListPage() {
  const [organizers, setOrganizers] = useState([]);
  const [query, setQuery] = useState("");

  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  async function loadOrganizers() {
    setIsLoading(true);
    setError("");

    try {
      const response = await getOrganizers({
        q: query
      });

      setOrganizers(response.organizers || []);
    } catch (requestError) {
      setError(requestError.message || "Не удалось загрузить список организаторов.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    loadOrganizers();
  }, []);

  function handleSubmit(event) {
    event.preventDefault();
    loadOrganizers();
  }

  function getOrganizerRating(organizer) {
    if (organizer.average_rating !== null && organizer.average_rating !== undefined) {
      return `★ ${organizer.average_rating}`;
    }

    if (
      organizer.organizer_rating &&
      organizer.organizer_rating.average_rating !== null &&
      organizer.organizer_rating.average_rating !== undefined
    ) {
      return `★ ${organizer.organizer_rating.average_rating}`;
    }

    return "пока не сформирован";
  }

  return (
    <main className="page">
      <section className="title-box">
        <h1>Организаторы</h1>
        <p className="muted">Список организаторов мероприятий на платформе.</p>
      </section>

      <section className="content single-content">
        <form className="toolbar" onSubmit={handleSubmit}>
          <div className="field">
            <label htmlFor="organizer-search">Поиск</label>
            <input
              id="organizer-search"
              type="text"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Название организации или имя организатора"
            />
          </div>

          <button className="btn btn-primary" type="submit">
            Найти
          </button>
        </form>

        {error && <div className="error-box">{error}</div>}

        {isLoading && <div className="loading-screen">Загрузка организаторов...</div>}

        {!isLoading && organizers.length === 0 && (
          <div className="empty-state">
            <h3>Организаторы не найдены</h3>
            <p>Измените поисковый запрос или вернитесь позже.</p>
          </div>
        )}

        {!isLoading && organizers.length > 0 && (
          <div className="cards-grid">
            {organizers.map((organizer) => (
              <article className="card" key={organizer.id}>
                <h2>{organizer.organization_name || organizer.full_name}</h2>

                {organizer.organization_description && (
                  <p>{organizer.organization_description}</p>
                )}

                <p className="muted">Рейтинг: {getOrganizerRating(organizer)}</p>

                <div className="form-actions">
                  <Link className="btn btn-primary" to={`/organizers/${organizer.id}`}>
                    Перейти к странице организатора
                  </Link>
                </div>
              </article>
            ))}
          </div>
        )}
      </section>
    </main>
  );
}