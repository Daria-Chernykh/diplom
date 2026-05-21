import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { getEventById } from "../../api/eventsApi.js";
import { addFavorite, removeFavorite } from "../../api/favoritesApi.js";
import { buildFileUrl } from "../../api/filesApi.js";
import { EventComplaintModal } from "../../components/complaints/EventComplaintModal.jsx";
import { useAuth } from "../../store/AuthContext.jsx";

function formatDate(value) {
  if (!value) {
    return "Дата не указана";
  }

  return new Date(value).toLocaleString("ru-RU", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit"
  });
}

function getPriceText(event) {
  if (!event || event.price_type === "free") {
    return "Бесплатно";
  }

  if (event.price_type === "fixed") {
    return event.price_value || "Фиксированная стоимость";
  }

  if (event.price_type === "from") {
    return event.price_value ? `от ${event.price_value}` : "Цена от";
  }

  return "Стоимость не указана";
}

export function EventWithoutRegistrationPage() {
  const { eventId } = useParams();
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();

  const [event, setEvent] = useState(null);
  const [isFavorite, setIsFavorite] = useState(false);
  const [isComplaintModalOpen, setIsComplaintModalOpen] = useState(false);

  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isFavoriteLoading, setIsFavoriteLoading] = useState(false);

  async function loadEvent() {
    setIsLoading(true);
    setError("");

    try {
      const response = await getEventById(eventId);

      setEvent(response.event);
      setIsFavorite(Boolean(response.event.is_favorite));
    } catch (requestError) {
      setError(requestError.message || "Не удалось загрузить мероприятие.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    loadEvent();
  }, [eventId]);

  async function handleFavoriteClick() {
    if (!isAuthenticated) {
      navigate("/login");
      return;
    }

    setIsFavoriteLoading(true);
    setMessage("");
    setError("");

    try {
      if (isFavorite) {
        await removeFavorite(event.id);
        setIsFavorite(false);
        setMessage("Мероприятие удалено из избранного.");
      } else {
        await addFavorite(event.id);
        setIsFavorite(true);
        setMessage("Мероприятие добавлено в избранное.");
      }
    } catch (requestError) {
      setError(requestError.message || "Не удалось изменить избранное.");
    } finally {
      setIsFavoriteLoading(false);
    }
  }

  function handleComplaintClick() {
    if (!isAuthenticated) {
      navigate("/login");
      return;
    }

    setIsComplaintModalOpen(true);
  }

  if (isLoading) {
    return <div className="loading-screen">Загрузка мероприятия...</div>;
  }

  if (error && !event) {
    return (
      <main className="page">
        <section className="card">
          <h1>Мероприятие недоступно</h1>
          <div className="error-box">{error}</div>

          <div className="form-actions">
            <Link className="btn btn-outline" to="/events">
              Вернуться в каталог
            </Link>
          </div>
        </section>
      </main>
    );
  }

  if (!event) {
    return null;
  }

  const imageUrl = event.image?.file_url ? buildFileUrl(event.image.file_url) : "";
  const isOwnEvent = user && user.id === event.organizer_id;

  return (
    <main className="page">
      <section className="title-box">
        <h1>{event.title}</h1>
        <p className="muted">
          {event.organizer?.organization_name || event.organizer?.full_name || "Организатор не указан"}
        </p>
      </section>

      {message && <div className="success-box">{message}</div>}
      {error && <div className="error-box">{error}</div>}

      <section className="event-detail">
        <div className="content">
          <div className="event-cover-large">
            {imageUrl ? (
              <img src={imageUrl} alt={event.title} />
            ) : (
              <span>Изображение мероприятия</span>
            )}
          </div>

          <section className="card">
            <h2>Описание</h2>
            <p>{event.long_description}</p>
          </section>

          <section className="card">
            <h2>Расписание</h2>
            <p>{event.schedule}</p>
          </section>

          <section className="card">
            <h2>Требования к участникам</h2>
            <p>{event.participant_requirements}</p>
          </section>
        </div>

        <aside className="card">
          <h2>Информация</h2>

          <div className="info-list">
            <div className="info-row">
              <strong>Дата и время</strong>
              <span>{formatDate(event.event_datetime)}</span>
            </div>

            <div className="info-row">
              <strong>Формат</strong>
              <span>{event.event_format === "online" ? "Онлайн" : "Офлайн"}</span>
            </div>

            <div className="info-row">
              <strong>Место проведения</strong>
              <span>{event.location}</span>
            </div>

            <div className="info-row">
              <strong>Стоимость</strong>
              <span>{getPriceText(event)}</span>
            </div>

            <div className="info-row">
              <strong>Регистрация</strong>
              <span>Для мероприятия регистрация не требуется</span>
            </div>

            {event.organizer_rating !== null && event.organizer_rating !== undefined && (
              <div className="info-row">
                <strong>Рейтинг организатора</strong>
                <span>★ {event.organizer_rating}</span>
              </div>
            )}
          </div>

          {event.tags?.length > 0 && (
            <div className="tags-list">
              {event.tags.map((tag) => (
                <span className="tag" key={tag.id || tag.name}>
                  {tag.name}
                </span>
              ))}
            </div>
          )}

          <div className="note">
            Предварительная регистрация на это мероприятие не требуется. Платформа не формирует заявку на участие и не ведет список участников.
          </div>

          <div className="form-actions">
            <button
              className="btn btn-outline"
              type="button"
              disabled={isFavoriteLoading}
              onClick={handleFavoriteClick}
            >
              {isFavorite ? "Удалить из избранного" : "Добавить в избранное"}
            </button>

            {!isOwnEvent && (
              <button className="btn btn-danger" type="button" onClick={handleComplaintClick}>
                Пожаловаться
              </button>
            )}
          </div>
        </aside>
      </section>

      {isComplaintModalOpen && (
        <EventComplaintModal
          eventId={event.id}
          onClose={() => setIsComplaintModalOpen(false)}
          onCreated={() => {
            setMessage("Жалоба отправлена. Карточка временно скрыта до проверки.");
            setIsComplaintModalOpen(false);
          }}
        />
      )}
    </main>
  );
}