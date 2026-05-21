import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { getCatalogEvents } from "../../api/eventsApi.js";

function getRegistrationTypeLabel(value) {
  if (value === "internal") {
    return "Регистрация на сайте";
  }

  if (value === "external") {
    return "Внешняя регистрация";
  }

  return "Без регистрации";
}

function getFormatLabel(value) {
  return value === "online" ? "Онлайн" : "Офлайн";
}

function getPriceLabel(event) {
  if (event.price_type === "free") {
    return "Бесплатно";
  }

  if (event.price_type === "fixed") {
    return event.price_value || "Фиксированная цена";
  }

  if (event.price_type === "from") {
    return event.price_value || "Цена от";
  }

  return "Стоимость не указана";
}

function RatingView({ rating }) {
  if (!rating || rating.value === null) {
    return <span className="rating-muted">Рейтинг не сформирован</span>;
  }

  return <span className="rating-value">★ {rating.value}</span>;
}

export function EventCatalogPage() {
  const [filters, setFilters] = useState({
    q: "",
    event_format: "",
    registration_type: "",
    tag: ""
  });

  const [events, setEvents] = useState([]);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  async function loadEvents(params = filters) {
    setIsLoading(true);
    setError("");

    try {
      const response = await getCatalogEvents(params);
      setEvents(response.events || []);
    } catch (requestError) {
      setError(requestError.message || "Не удалось загрузить каталог мероприятий.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    loadEvents();
  }, []);

  function updateFilter(event) {
    const { name, value } = event.target;

    setFilters((current) => ({
      ...current,
      [name]: value
    }));
  }

  async function handleSearch(event) {
    event.preventDefault();
    await loadEvents(filters);
  }

  return (
    <main className="page">
      <section className="catalog-hero">
        <h1>Каталог мероприятий</h1>
        <p>
          На странице отображаются опубликованные мероприятия в сфере популярной культуры.
        </p>
      </section>

      <section className="catalog-toolbar">
        <form className="catalog-filter-form" onSubmit={handleSearch}>
          <div className="field">
            <label htmlFor="q">Поиск</label>
            <input
              id="q"
              name="q"
              type="text"
              placeholder="Название, описание или место"
              value={filters.q}
              onChange={updateFilter}
            />
          </div>

          <div className="field">
            <label htmlFor="event_format">Формат</label>
            <select
              id="event_format"
              name="event_format"
              value={filters.event_format}
              onChange={updateFilter}
            >
              <option value="">Любой</option>
              <option value="offline">Офлайн</option>
              <option value="online">Онлайн</option>
            </select>
          </div>

          <div className="field">
            <label htmlFor="registration_type">Регистрация</label>
            <select
              id="registration_type"
              name="registration_type"
              value={filters.registration_type}
              onChange={updateFilter}
            >
              <option value="">Любой тип</option>
              <option value="internal">На сайте</option>
              <option value="external">Внешняя</option>
              <option value="none">Без регистрации</option>
            </select>
          </div>

          <div className="field">
            <label htmlFor="tag">Тег</label>
            <input
              id="tag"
              name="tag"
              type="text"
              placeholder="Например: K-pop"
              value={filters.tag}
              onChange={updateFilter}
            />
          </div>

          <button className="btn btn-primary" type="submit">
            Найти
          </button>
        </form>
      </section>

      {error && <div className="error-box">{error}</div>}

      {isLoading && <div className="loading-screen">Загрузка каталога...</div>}

      {!isLoading && (
        <section className="catalog-grid">
          {events.length === 0 && (
            <article className="card">
              <p className="muted">Мероприятия не найдены.</p>
            </article>
          )}

          {events.map((event) => (
            <article className="catalog-card" key={event.id}>
              <div className="catalog-card-image"></div>

              <div className="catalog-card-body">
                <h2>{event.title}</h2>

                <p>{event.short_description}</p>

                <div className="catalog-meta">
                  <span>{getFormatLabel(event.event_format)}</span>
                  <span>
                    {event.event_datetime
                      ? new Date(event.event_datetime).toLocaleString("ru-RU")
                      : "Дата не указана"}
                  </span>
                  <span>{getPriceLabel(event)}</span>
                  <span>{getRegistrationTypeLabel(event.registration_type)}</span>
                </div>

                <Link className="organizer-mini-link" to={`/organizers/${event.organizer_id}`}>
                  <span>{event.organizer?.organization_name || event.organizer?.full_name || "Организатор"}</span>
                  <RatingView rating={event.organizer?.rating} />
                </Link>

                <div className="tags-list">
                  {event.tags.map((tag) => (
                    <span className="tag" key={tag.id}>
                      {tag.name}
                    </span>
                  ))}
                </div>

                <div className="catalog-card-footer">
                  <Link className="btn btn-outline" to={`/events/${event.id}`}>
                    Подробнее
                  </Link>
                </div>
              </div>
            </article>
          ))}
        </section>
      )}
    </main>
  );
}