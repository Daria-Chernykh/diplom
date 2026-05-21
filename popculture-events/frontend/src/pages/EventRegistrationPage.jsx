import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import {
  createInternalRegistration,
  getEventRegistrationFields
} from "../api/registrationsApi.js";
import { getEventById } from "../api/eventsApi.js";
import { FieldError } from "../components/ui/FieldError.jsx";
import { getBackendFieldErrors, hasErrors } from "../utils/validation.js";

function validateAnswers(fields, answers) {
  const errors = {};

  fields.forEach((field) => {
    const key = String(field.id);
    const value = answers[key];

    if (field.is_required && (value === undefined || value === null || String(value).trim() === "")) {
      errors[key] = `Поле «${field.field_name}» обязательно для заполнения.`;
    }

    if (field.field_type === "email" && value) {
      const stringValue = String(value).trim();

      if (!stringValue.includes("@") || !stringValue.includes(".")) {
        errors[key] = `Поле «${field.field_name}» должно содержать корректную электронную почту.`;
      }
    }

    if (field.field_type === "number" && value && Number.isNaN(Number(value))) {
      errors[key] = `Поле «${field.field_name}» должно содержать число.`;
    }
  });

  return errors;
}

function getInputType(fieldType) {
  if (fieldType === "email") {
    return "email";
  }

  if (fieldType === "phone") {
    return "tel";
  }

  if (fieldType === "number") {
    return "number";
  }

  if (fieldType === "date") {
    return "date";
  }

  return "text";
}

export function EventRegistrationPage() {
  const { eventId } = useParams();
  const navigate = useNavigate();

  const [event, setEvent] = useState(null);
  const [fields, setFields] = useState([]);
  const [answers, setAnswers] = useState({});
  const [fieldErrors, setFieldErrors] = useState({});

  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    async function loadData() {
      setIsLoading(true);
      setError("");

      try {
        const eventResponse = await getEventById(eventId);
        const fieldsResponse = await getEventRegistrationFields(eventId);

        setEvent(eventResponse.event);
        setFields(fieldsResponse.fields || []);

        const initialAnswers = {};

        (fieldsResponse.fields || []).forEach((field) => {
          initialAnswers[String(field.id)] = field.field_type === "checkbox" ? false : "";
        });

        setAnswers(initialAnswers);
      } catch (requestError) {
        setError(requestError.message || "Не удалось загрузить форму регистрации.");
      } finally {
        setIsLoading(false);
      }
    }

    loadData();
  }, [eventId]);

  function handleAnswerChange(field, value) {
    const key = String(field.id);

    setAnswers((current) => ({
      ...current,
      [key]: value
    }));

    setFieldErrors((current) => ({
      ...current,
      [key]: ""
    }));
  }

  async function handleSubmit(submitEvent) {
    submitEvent.preventDefault();

    const errors = validateAnswers(fields, answers);
    setFieldErrors(errors);

    if (hasErrors(errors)) {
      setError("Проверьте заполнение регистрационной формы.");
      return;
    }

    setIsSubmitting(true);
    setError("");
    setMessage("");

    try {
      const response = await createInternalRegistration(eventId, {
        answers
      });

      setMessage(response.message || "Регистрация отправлена.");
      navigate(`/events/${eventId}`, { replace: true });
    } catch (requestError) {
      setFieldErrors(getBackendFieldErrors(requestError));
      setError(requestError.message || "Не удалось отправить регистрацию.");
    } finally {
      setIsSubmitting(false);
    }
  }

  if (isLoading) {
    return <div className="loading-screen">Загрузка формы регистрации...</div>;
  }

  if (error && !event) {
    return (
      <main className="page">
        <section className="card">
          <h1>Регистрация недоступна</h1>
          <div className="error-box">{error}</div>
          <Link className="btn btn-outline" to="/events">
            Вернуться к каталогу
          </Link>
        </section>
      </main>
    );
  }

  return (
    <main className="page">
      <section className="title-box">
        <h1>Регистрация на мероприятие</h1>
        {event && <p className="muted">{event.title}</p>}
      </section>

      <section className="content single-content">
        {error && <div className="error-box">{error}</div>}
        {message && <div className="success-box">{message}</div>}

        {fields.length === 0 && (
          <div className="note">
            Для этого мероприятия регистрационная форма не настроена.
          </div>
        )}

        {fields.length > 0 && (
          <form className="form" onSubmit={handleSubmit} noValidate>
            <section className="form-section">
              <h3>Данные участника</h3>

              {fields.map((field) => {
                const key = String(field.id);

                if (field.field_type === "textarea") {
                  return (
                    <div className="field" key={field.id}>
                      <label htmlFor={key}>
                        {field.field_name}
                        {field.is_required ? " *" : ""}
                      </label>

                      <textarea
                        className={fieldErrors[key] ? "invalid" : ""}
                        id={key}
                        value={answers[key] || ""}
                        onChange={(event) => handleAnswerChange(field, event.target.value)}
                      />

                      <FieldError message={fieldErrors[key]} />
                    </div>
                  );
                }

                if (field.field_type === "checkbox") {
                  return (
                    <div key={field.id}>
                      <label className="required-check">
                        <input
                          id={key}
                          type="checkbox"
                          checked={Boolean(answers[key])}
                          onChange={(event) => handleAnswerChange(field, event.target.checked)}
                        />
                        {field.field_name}
                        {field.is_required ? " *" : ""}
                      </label>

                      <FieldError message={fieldErrors[key]} />
                    </div>
                  );
                }

                return (
                  <div className="field" key={field.id}>
                    <label htmlFor={key}>
                      {field.field_name}
                      {field.is_required ? " *" : ""}
                    </label>

                    <input
                      className={fieldErrors[key] ? "invalid" : ""}
                      id={key}
                      type={getInputType(field.field_type)}
                      value={answers[key] || ""}
                      onChange={(event) => handleAnswerChange(field, event.target.value)}
                    />

                    <FieldError message={fieldErrors[key]} />
                  </div>
                );
              })}
            </section>

            <div className="form-actions">
              <Link className="btn btn-outline" to={`/events/${eventId}`}>
                Отмена
              </Link>

              <button className="btn btn-primary" type="submit" disabled={isSubmitting}>
                {isSubmitting ? "Отправка..." : "Отправить регистрацию"}
              </button>
            </div>
          </form>
        )}
      </section>
    </main>
  );
}