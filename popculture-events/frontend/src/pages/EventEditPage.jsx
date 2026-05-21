import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { getOrganizerEventById, updateEvent } from "../api/eventsApi.js";
import { uploadEventImage } from "../api/filesApi.js";
import { ImageUploader } from "../components/files/ImageUploader.jsx";
import { FieldError } from "../components/ui/FieldError.jsx";
import {
  getBackendFieldErrors,
  hasErrors,
  validateFutureDateTime
} from "../utils/validation.js";

function toInputDateTime(value) {
  if (!value) {
    return "";
  }

  return value.slice(0, 16);
}

function splitTags(tags) {
  if (!Array.isArray(tags)) {
    return "";
  }

  return tags.map((tag) => tag.name || tag).join(", ");
}

function parseTags(value) {
  return value
    .split(",")
    .map((tag) => tag.trim())
    .filter(Boolean);
}

function validateForm(form) {
  const errors = {};

  if (!form.title.trim()) {
    errors.title = "Название обязательно для заполнения.";
  }

  if (!form.short_description.trim()) {
    errors.short_description = "Краткое описание обязательно для заполнения.";
  }

  if (!form.long_description.trim()) {
    errors.long_description = "Расширенное описание обязательно для заполнения.";
  }

  const dateError = validateFutureDateTime(form.event_datetime);

  if (dateError) {
    errors.event_datetime = dateError;
  }

  if (!form.event_format) {
    errors.event_format = "Выберите формат мероприятия.";
  }

  if (!form.location.trim()) {
    errors.location = "Место проведения обязательно для заполнения.";
  }

  if (!form.schedule.trim()) {
    errors.schedule = "Расписание обязательно для заполнения.";
  }

  if (!form.participant_requirements.trim()) {
    errors.participant_requirements = "Требования к участникам обязательны для заполнения.";
  }

  if (!form.price_type) {
    errors.price_type = "Выберите тип стоимости.";
  }

  if (form.price_type !== "free" && !form.price_value.trim()) {
    errors.price_value = "Укажите значение стоимости.";
  }

  return errors;
}

export function EventEditPage() {
  const { eventId } = useParams();
  const navigate = useNavigate();

  const [event, setEvent] = useState(null);
  const [eventImage, setEventImage] = useState(null);

  const [form, setForm] = useState({
    title: "",
    short_description: "",
    long_description: "",
    event_datetime: "",
    event_format: "offline",
    location: "",
    schedule: "",
    participant_requirements: "",
    price_type: "free",
    price_value: "",
    tags: "",
    organizer_complaint_comment: "",
    send_to_admin: false
  });

  const [fieldErrors, setFieldErrors] = useState({});
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    async function loadEvent() {
      setIsLoading(true);
      setError("");

      try {
        const response = await getOrganizerEventById(eventId);
        const loadedEvent = response.event;

        setEvent(loadedEvent);
        setEventImage(loadedEvent.image || null);

        setForm({
          title: loadedEvent.title || "",
          short_description: loadedEvent.short_description || "",
          long_description: loadedEvent.long_description || "",
          event_datetime: toInputDateTime(loadedEvent.event_datetime),
          event_format: loadedEvent.event_format || "offline",
          location: loadedEvent.location || "",
          schedule: loadedEvent.schedule || "",
          participant_requirements: loadedEvent.participant_requirements || "",
          price_type: loadedEvent.price_type || "free",
          price_value: loadedEvent.price_value || "",
          tags: splitTags(loadedEvent.tags),
          organizer_complaint_comment: loadedEvent.organizer_complaint_comment || "",
          send_to_admin: false
        });
      } catch (requestError) {
        setError(requestError.message || "Не удалось загрузить мероприятие.");
      } finally {
        setIsLoading(false);
      }
    }

    loadEvent();
  }, [eventId]);

  function handleChange(event) {
    const { name, value, type, checked } = event.target;

    setForm((current) => ({
      ...current,
      [name]: type === "checkbox" ? checked : value
    }));

    setFieldErrors((current) => ({
      ...current,
      [name]: ""
    }));
  }

  async function handleSubmit(event) {
    event.preventDefault();

    const errors = validateForm(form);
    setFieldErrors(errors);

    if (hasErrors(errors)) {
      setError("Проверьте заполнение формы мероприятия.");
      return;
    }

    setIsSaving(true);
    setError("");
    setMessage("");

    try {
      const payload = {
        title: form.title,
        short_description: form.short_description,
        long_description: form.long_description,
        event_datetime: form.event_datetime,
        event_format: form.event_format,
        location: form.location,
        schedule: form.schedule,
        participant_requirements: form.participant_requirements,
        price_type: form.price_type,
        price_value: form.price_type === "free" ? "" : form.price_value,
        tags: parseTags(form.tags),
        organizer_complaint_comment: form.organizer_complaint_comment,
        send_to_admin: form.send_to_admin
      };

      const response = await updateEvent(eventId, payload);

      setEvent(response.event);
      setEventImage(response.event.image || eventImage);
      setMessage(response.message || "Изменения сохранены.");

      if (form.send_to_admin) {
        navigate("/organizer/events");
      }
    } catch (requestError) {
      setFieldErrors(getBackendFieldErrors(requestError));
      setError(requestError.message || "Не удалось сохранить изменения.");
    } finally {
      setIsSaving(false);
    }
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
          <Link className="btn btn-outline" to="/organizer/events">
            Назад к мероприятиям
          </Link>
        </section>
      </main>
    );
  }

  if (!event) {
    return (
      <main className="page">
        <section className="card">
          <h1>Мероприятие не найдено</h1>
        </section>
      </main>
    );
  }

  return (
    <main className="page">
      <section className="title-box">
        <h1>Личный кабинет организатора</h1>
      </section>

      <section className="main">
        <aside className="sidebar">
          <h2>Разделы</h2>

          <div className="menu">
            <Link className="menu-item" to="/organizer">
              <div>Профиль</div>
            </Link>

            <Link className="menu-item active" to="/organizer/events">
              <div>Мои мероприятия</div>
            </Link>

            <Link className="menu-item" to="/organizer/notifications">
              <div>Уведомления</div>
            </Link>

            <Link className="menu-item" to="/organizer/events/archive">
              <div>Архив мероприятий</div>
            </Link>
          </div>
        </aside>

        <section className="content">
          <div className="section-head">
            <div>
              <h2>Редактирование мероприятия</h2>
              <p className="muted">
                Тип регистрации и структура регистрационной формы не изменяются после создания карточки.
              </p>
            </div>
          </div>

          {error && <div className="error-box">{error}</div>}
          {message && <div className="success-box">{message}</div>}

          <ImageUploader
            title="Изображение мероприятия"
            currentFile={eventImage}
            uploadHandler={(file) => uploadEventImage(event.id, file)}
            onUploaded={(file) => setEventImage(file)}
            onDeleted={() => setEventImage(null)}
            buttonText="Загрузить изображение мероприятия"
          />

          <form className="form" onSubmit={handleSubmit} noValidate>
            {event.status === "blocked" && (
              <section className="form-section">
                <h3>Жалоба и отправка на проверку</h3>

                <div className="note">
                  Карточка заблокирована. Организатор может внести исправления и отправить
                  карточку на рассмотрение администратору.
                </div>

                <div className="field">
                  <label htmlFor="organizer_complaint_comment">
                    Комментарий организатора для администратора
                  </label>
                  <textarea
                    id="organizer_complaint_comment"
                    name="organizer_complaint_comment"
                    value={form.organizer_complaint_comment}
                    onChange={handleChange}
                    placeholder="Опишите, какие изменения были внесены"
                  />
                </div>

                <label className="required-check">
                  <input
                    type="checkbox"
                    name="send_to_admin"
                    checked={form.send_to_admin}
                    onChange={handleChange}
                  />
                  Отправить карточку на рассмотрение администратору после сохранения
                </label>
              </section>
            )}

            <section className="form-section">
              <h3>Основная информация</h3>

              <div className="field">
                <label htmlFor="title">Название</label>
                <input
                  className={fieldErrors.title ? "invalid" : ""}
                  id="title"
                  name="title"
                  type="text"
                  value={form.title}
                  onChange={handleChange}
                />
                <FieldError message={fieldErrors.title} />
              </div>

              <div className="field">
                <label htmlFor="short_description">Краткое описание</label>
                <textarea
                  className={fieldErrors.short_description ? "invalid" : ""}
                  id="short_description"
                  name="short_description"
                  value={form.short_description}
                  onChange={handleChange}
                />
                <FieldError message={fieldErrors.short_description} />
              </div>

              <div className="field">
                <label htmlFor="long_description">Расширенное описание</label>
                <textarea
                  className={fieldErrors.long_description ? "invalid" : ""}
                  id="long_description"
                  name="long_description"
                  value={form.long_description}
                  onChange={handleChange}
                />
                <FieldError message={fieldErrors.long_description} />
              </div>
            </section>

            <section className="form-section">
              <h3>Дата, формат и место проведения</h3>

              <div className="field">
                <label htmlFor="event_datetime">Дата и время</label>
                <input
                  className={fieldErrors.event_datetime ? "invalid" : ""}
                  id="event_datetime"
                  name="event_datetime"
                  type="datetime-local"
                  value={form.event_datetime}
                  onChange={handleChange}
                />
                <FieldError message={fieldErrors.event_datetime} />
              </div>

              <div>
                <label className="field-label">Формат мероприятия</label>

                <div className="choice-group">
                  <label className="choice-label">
                    <input
                      type="radio"
                      name="event_format"
                      value="offline"
                      checked={form.event_format === "offline"}
                      onChange={handleChange}
                    />
                    Офлайн
                  </label>

                  <label className="choice-label">
                    <input
                      type="radio"
                      name="event_format"
                      value="online"
                      checked={form.event_format === "online"}
                      onChange={handleChange}
                    />
                    Онлайн
                  </label>
                </div>

                <FieldError message={fieldErrors.event_format} />
              </div>

              <div className="field">
                <label htmlFor="location">Место проведения</label>
                <input
                  className={fieldErrors.location ? "invalid" : ""}
                  id="location"
                  name="location"
                  type="text"
                  value={form.location}
                  onChange={handleChange}
                />
                <FieldError message={fieldErrors.location} />
              </div>

              <div className="field">
                <label htmlFor="schedule">Расписание</label>
                <textarea
                  className={fieldErrors.schedule ? "invalid" : ""}
                  id="schedule"
                  name="schedule"
                  value={form.schedule}
                  onChange={handleChange}
                />
                <FieldError message={fieldErrors.schedule} />
              </div>

              <div className="field">
                <label htmlFor="participant_requirements">Требования к участникам</label>
                <textarea
                  className={fieldErrors.participant_requirements ? "invalid" : ""}
                  id="participant_requirements"
                  name="participant_requirements"
                  value={form.participant_requirements}
                  onChange={handleChange}
                />
                <FieldError message={fieldErrors.participant_requirements} />
              </div>
            </section>

            <section className="form-section">
              <h3>Стоимость и теги</h3>

              <div>
                <label className="field-label">Стоимость участия</label>

                <div className="choice-group">
                  <label className="choice-label">
                    <input
                      type="radio"
                      name="price_type"
                      value="free"
                      checked={form.price_type === "free"}
                      onChange={handleChange}
                    />
                    Бесплатно
                  </label>

                  <label className="choice-label">
                    <input
                      type="radio"
                      name="price_type"
                      value="fixed"
                      checked={form.price_type === "fixed"}
                      onChange={handleChange}
                    />
                    Фиксированная цена
                  </label>

                  <label className="choice-label">
                    <input
                      type="radio"
                      name="price_type"
                      value="from"
                      checked={form.price_type === "from"}
                      onChange={handleChange}
                    />
                    Цена от
                  </label>
                </div>

                <FieldError message={fieldErrors.price_type} />
              </div>

              {form.price_type !== "free" && (
                <div className="field">
                  <label htmlFor="price_value">Значение стоимости</label>
                  <input
                    className={fieldErrors.price_value ? "invalid" : ""}
                    id="price_value"
                    name="price_value"
                    type="text"
                    value={form.price_value}
                    onChange={handleChange}
                    placeholder="Например: 1200 ₽ или от 500 ₽"
                  />
                  <FieldError message={fieldErrors.price_value} />
                </div>
              )}

              <div className="field">
                <label htmlFor="tags">Теги</label>
                <input
                  id="tags"
                  name="tags"
                  type="text"
                  value={form.tags}
                  onChange={handleChange}
                  placeholder="Например: K-pop, Dance, Offline"
                />
                <span className="field-hint">Теги указываются через запятую.</span>
              </div>
            </section>

            <section className="form-section">
              <h3>Регистрация</h3>

              <div className="disabled-field">
                <strong>Тип регистрации:</strong>
                <br />
                {event.registration_type === "internal" && "Внутренняя регистрация"}
                {event.registration_type === "external" && "Внешняя регистрация"}
                {event.registration_type === "none" && "Без регистрации"}
              </div>

              {event.registration_type === "internal" && (
                <div className="disabled-field">
                  <strong>Подтверждение регистрации:</strong>
                  <br />
                  {event.registration_confirmation === "manual"
                    ? "Регистрация с подтверждением организатором"
                    : "Регистрация без подтверждения"}
                </div>
              )}

              {event.registration_type === "external" && (
                <div className="disabled-field">
                  <strong>Ссылка внешней регистрации:</strong>
                  <br />
                  {event.external_registration_url}
                </div>
              )}
            </section>

            <div className="form-actions">
              <Link className="btn btn-outline" to="/organizer/events">
                Отмена
              </Link>

              <button className="btn btn-primary" type="submit" disabled={isSaving}>
                {isSaving ? "Сохранение..." : "Сохранить изменения"}
              </button>
            </div>
          </form>
        </section>
      </section>
    </main>
  );
}