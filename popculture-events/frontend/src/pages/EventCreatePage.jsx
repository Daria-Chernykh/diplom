import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { createEvent } from "../api/eventsApi.js";
import { FieldError } from "../components/ui/FieldError.jsx";
import {
  getBackendFieldErrors,
  hasErrors,
  isUrl,
  validateFutureDateTime
} from "../utils/validation.js";

const EMPTY_FIELD = {
  field_name: "",
  field_type: "text",
  is_required: true
};

function parseTags(value) {
  return value
    .split(",")
    .map((tag) => tag.trim())
    .filter(Boolean);
}

function validateForm(form, registrationFields) {
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

  if (!form.registration_type) {
    errors.registration_type = "Выберите тип регистрации.";
  }

  if (form.registration_type === "internal" && !form.registration_confirmation) {
    errors.registration_confirmation = "Выберите режим подтверждения регистрации.";
  }

  if (form.registration_type === "internal" && registrationFields.length === 0) {
    errors.registration_fields = "Для внутренней регистрации необходимо добавить хотя бы одно поле формы.";
  }

  if (form.registration_type === "external") {
    if (!form.external_registration_url.trim()) {
      errors.external_registration_url = "Ссылка внешней регистрации обязательна для заполнения.";
    } else if (!isUrl(form.external_registration_url)) {
      errors.external_registration_url = "Введите корректную ссылку внешней регистрации.";
    }
  }

  if (!form.price_type) {
    errors.price_type = "Выберите тип стоимости.";
  }

  if (form.price_type !== "free" && !form.price_value.trim()) {
    errors.price_value = "Укажите значение стоимости.";
  }

  if (!form.legal_confirmed) {
    errors.legal_confirmed = "Необходимо подтвердить достоверность информации.";
  }

  return errors;
}

export function EventCreatePage() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    title: "",
    short_description: "",
    long_description: "",
    event_datetime: "",
    event_format: "offline",
    location: "",
    schedule: "",
    participant_requirements: "",
    registration_type: "internal",
    registration_confirmation: "manual",
    external_registration_url: "",
    price_type: "free",
    price_value: "",
    tags: "",
    legal_confirmed: false
  });

  const [newField, setNewField] = useState(EMPTY_FIELD);
  const [registrationFields, setRegistrationFields] = useState([
    {
      field_name: "Имя",
      field_type: "text",
      is_required: true
    },
    {
      field_name: "Электронная почта",
      field_type: "email",
      is_required: true
    },
    {
      field_name: "Телефон",
      field_type: "phone",
      is_required: true
    }
  ]);

  const [fieldErrors, setFieldErrors] = useState({});
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  function clearFieldError(name) {
    setFieldErrors((current) => ({
      ...current,
      [name]: ""
    }));
  }

  function handleChange(event) {
    const { name, value, type, checked } = event.target;

    setForm((current) => ({
      ...current,
      [name]: type === "checkbox" ? checked : value
    }));

    clearFieldError(name);
  }

  function handleNewFieldChange(event) {
    const { name, value, type, checked } = event.target;

    setNewField((current) => ({
      ...current,
      [name]: type === "checkbox" ? checked : value
    }));

    clearFieldError("registration_fields");
  }

  function addRegistrationField() {
    if (!newField.field_name.trim()) {
      setFieldErrors((current) => ({
        ...current,
        registration_fields: "Введите название добавляемого поля."
      }));
      return;
    }

    setRegistrationFields((current) => [
      ...current,
      {
        field_name: newField.field_name.trim(),
        field_type: newField.field_type,
        is_required: newField.is_required
      }
    ]);

    setNewField(EMPTY_FIELD);
    clearFieldError("registration_fields");
  }

  function removeRegistrationField(index) {
    setRegistrationFields((current) => current.filter((_, currentIndex) => currentIndex !== index));
  }

  async function handleSubmit(event) {
    event.preventDefault();

    const errors = validateForm(form, registrationFields);
    setFieldErrors(errors);

    if (hasErrors(errors)) {
      setError("Проверьте заполнение формы мероприятия.");
      return;
    }

    setIsSubmitting(true);
    setError("");

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
        registration_type: form.registration_type,
        registration_confirmation:
          form.registration_type === "internal" ? form.registration_confirmation : null,
        external_registration_url:
          form.registration_type === "external" ? form.external_registration_url : null,
        price_type: form.price_type,
        price_value: form.price_type === "free" ? "" : form.price_value,
        tags: parseTags(form.tags),
        registration_fields:
          form.registration_type === "internal" ? registrationFields : []
      };

      const response = await createEvent(payload);

      navigate(`/events/${response.event.id}`, { replace: true });
    } catch (requestError) {
      setFieldErrors(getBackendFieldErrors(requestError));
      setError(requestError.message || "Не удалось создать мероприятие.");
    } finally {
      setIsSubmitting(false);
    }
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
              <h2>Создание мероприятия</h2>
              <p className="muted">
                После публикации карточка будет доступна пользователям в каталоге.
              </p>
            </div>
          </div>

          {error && <div className="error-box">{error}</div>}

          <form className="form" onSubmit={handleSubmit} noValidate>
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
                  placeholder="Введите название мероприятия"
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
                  placeholder="Краткое описание для каталога"
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
                  placeholder="Подробное описание программы, условий участия и другой важной информации"
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
                  placeholder="Адрес, площадка или ссылка для онлайн-формата"
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
                  placeholder="Например: 18:00 — открытие входа"
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
                  placeholder="Возрастные ограничения, условия входа, правила участия"
                />
                <FieldError message={fieldErrors.participant_requirements} />
              </div>
            </section>

            <section className="form-section">
              <h3>Теги</h3>

              <div className="field">
                <label htmlFor="tags">Теги</label>
                <input
                  id="tags"
                  name="tags"
                  type="text"
                  value={form.tags}
                  onChange={handleChange}
                  placeholder="Например: K-pop, Dance, Meetup"
                />
                <span className="field-hint">Теги указываются через запятую.</span>
              </div>
            </section>

            <section className="form-section">
              <h3>Регистрация</h3>

              <div>
                <label className="field-label">Тип регистрации</label>

                <div className="choice-group">
                  <label className="choice-label">
                    <input
                      type="radio"
                      name="registration_type"
                      value="internal"
                      checked={form.registration_type === "internal"}
                      onChange={handleChange}
                    />
                    Внутренняя регистрация
                  </label>

                  <label className="choice-label">
                    <input
                      type="radio"
                      name="registration_type"
                      value="external"
                      checked={form.registration_type === "external"}
                      onChange={handleChange}
                    />
                    Внешняя регистрация
                  </label>

                  <label className="choice-label">
                    <input
                      type="radio"
                      name="registration_type"
                      value="none"
                      checked={form.registration_type === "none"}
                      onChange={handleChange}
                    />
                    Без регистрации
                  </label>
                </div>

                <FieldError message={fieldErrors.registration_type} />
              </div>

              {form.registration_type === "external" && (
                <div className="field">
                  <label htmlFor="external_registration_url">Ссылка на регистрацию</label>
                  <input
                    className={fieldErrors.external_registration_url ? "invalid" : ""}
                    id="external_registration_url"
                    name="external_registration_url"
                    type="url"
                    value={form.external_registration_url}
                    onChange={handleChange}
                    placeholder="https://example.com/register"
                  />
                  <FieldError message={fieldErrors.external_registration_url} />
                </div>
              )}

              {form.registration_type === "internal" && (
                <div className="builder">
                  <div className="note">
                    Внутренняя регистрация выполняется через форму на сайте. Организатор
                    может добавить поля, которые пользователь должен заполнить.
                  </div>

                  <div className="builder-controls">
                    <div className="field">
                      <label htmlFor="field_name">Название поля</label>
                      <input
                        id="field_name"
                        name="field_name"
                        type="text"
                        value={newField.field_name}
                        onChange={handleNewFieldChange}
                        placeholder="Например: Имя, Телефон, Комментарий"
                      />
                    </div>

                    <div className="field">
                      <label htmlFor="field_type">Тип поля</label>
                      <select
                        id="field_type"
                        name="field_type"
                        value={newField.field_type}
                        onChange={handleNewFieldChange}
                      >
                        <option value="text">Текстовое поле</option>
                        <option value="email">Электронная почта</option>
                        <option value="phone">Телефон</option>
                        <option value="number">Число</option>
                        <option value="date">Дата</option>
                        <option value="select">Выпадающий список</option>
                        <option value="textarea">Многострочный текст</option>
                        <option value="checkbox">Флажок</option>
                      </select>
                    </div>

                    <button className="btn btn-outline" type="button" onClick={addRegistrationField}>
                      Добавить поле
                    </button>
                  </div>

                  <label className="required-check">
                    <input
                      type="checkbox"
                      name="is_required"
                      checked={newField.is_required}
                      onChange={handleNewFieldChange}
                    />
                    Сделать добавляемое поле обязательным
                  </label>

                  <FieldError message={fieldErrors.registration_fields} />

                  <div className="form-fields-list">
                    {registrationFields.map((field, index) => (
                      <div className="form-field-preview" key={`${field.field_name}-${index}`}>
                        <div className="preview-title">
                          <strong>{field.field_name}</strong>
                          <span>{field.is_required ? "Обязательное поле" : "Необязательное поле"}</span>
                        </div>

                        <div className="field-type">{field.field_type}</div>

                        <button
                          className="btn btn-danger"
                          type="button"
                          onClick={() => removeRegistrationField(index)}
                        >
                          Удалить
                        </button>
                      </div>
                    ))}
                  </div>

                  <div>
                    <label className="field-label">Подтверждение регистрации</label>

                    <div className="choice-group">
                      <label className="choice-label">
                        <input
                          type="radio"
                          name="registration_confirmation"
                          value="manual"
                          checked={form.registration_confirmation === "manual"}
                          onChange={handleChange}
                        />
                        Регистрация с подтверждением
                      </label>

                      <label className="choice-label">
                        <input
                          type="radio"
                          name="registration_confirmation"
                          value="automatic"
                          checked={form.registration_confirmation === "automatic"}
                          onChange={handleChange}
                        />
                        Регистрация без подтверждения
                      </label>
                    </div>

                    <FieldError message={fieldErrors.registration_confirmation} />
                  </div>
                </div>
              )}

              {form.registration_type === "none" && (
                <div className="note">
                  Для этого мероприятия регистрация не требуется. Пользователь сможет просматривать
                  карточку мероприятия и добавлять ее в избранное.
                </div>
              )}
            </section>

            <section className="form-section">
              <h3>Стоимость участия</h3>

              <div>
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
            </section>

            <label className="legal-check">
              <input
                type="checkbox"
                name="legal_confirmed"
                checked={form.legal_confirmed}
                onChange={handleChange}
              />
              <span>
                Я подтверждаю, что информация о мероприятии достоверна, не нарушает права
                третьих лиц, соответствует <Link to="/legal-documents">Пользовательскому соглашению</Link> и
                может быть опубликована на платформе.
              </span>
            </label>

            <FieldError message={fieldErrors.legal_confirmed} />

            <div className="form-actions">
              <Link className="btn btn-outline" to="/organizer/events">
                Отмена
              </Link>

              <button className="btn btn-primary" type="submit" disabled={isSubmitting}>
                {isSubmitting ? "Публикация..." : "Опубликовать мероприятие"}
              </button>
            </div>
          </form>
        </section>
      </section>
    </main>
  );
}