import { useState } from "react";

import { createEventComplaint } from "../../api/complaintsApi.js";
import { FieldError } from "../ui/FieldError.jsx";
import { Modal } from "../ui/Modal.jsx";
import { getBackendFieldErrors, hasErrors } from "../../utils/validation.js";

function validateForm(form) {
  const errors = {};

  if (!form.complaint_type.trim()) {
    errors.complaint_type = "Выберите тип жалобы.";
  }

  if (!form.complaint_text.trim()) {
    errors.complaint_text = "Описание жалобы обязательно для заполнения.";
  }

  if (form.complaint_text.trim().length > 2000) {
    errors.complaint_text = "Описание жалобы не должно превышать 2000 символов.";
  }

  return errors;
}

export function EventComplaintModal({ eventId, onClose, onCreated }) {
  const [form, setForm] = useState({
    complaint_type: "",
    complaint_text: ""
  });

  const [fieldErrors, setFieldErrors] = useState({});
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  function handleChange(event) {
    const { name, value } = event.target;

    setForm((current) => ({
      ...current,
      [name]: value
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
      setError("Проверьте заполнение жалобы.");
      return;
    }

    setIsSubmitting(true);
    setError("");

    try {
      const response = await createEventComplaint(eventId, {
        complaint_type: form.complaint_type,
        comment: form.complaint_text
      });

      if (onCreated) {
        onCreated(response.complaint);
      }

      onClose();
    } catch (requestError) {
      setFieldErrors(getBackendFieldErrors(requestError));
      setError(requestError.message || "Не удалось отправить жалобу.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <Modal
      title="Жалоба на карточку мероприятия"
      onClose={onClose}
      actions={
        <>
          <button className="btn btn-outline" type="button" onClick={onClose}>
            Отмена
          </button>

          <button
            className="btn btn-danger"
            type="button"
            disabled={isSubmitting}
            onClick={handleSubmit}
          >
            {isSubmitting ? "Отправка..." : "Отправить жалобу"}
          </button>
        </>
      }
    >
      {error && <div className="error-box">{error}</div>}

      <form className="form" onSubmit={handleSubmit} noValidate>
        <div className="field">
          <label htmlFor="complaint_type">Тип жалобы</label>
          <select
            className={fieldErrors.complaint_type ? "invalid" : ""}
            id="complaint_type"
            name="complaint_type"
            value={form.complaint_type}
            onChange={handleChange}
          >
            <option value="">Выберите тип жалобы</option>
            <option value="misinformation">Недостоверная информация</option>
            <option value="fraud">Мошенничество или подозрительная информация</option>
            <option value="prohibited_content">Неприемлемый контент</option>
            <option value="duplicate">Дублирующая карточка</option>
            <option value="other">Другое</option>
          </select>
          <FieldError message={fieldErrors.complaint_type} />
        </div>

        <div className="field">
          <label htmlFor="complaint_text">Описание жалобы</label>
          <textarea
            className={fieldErrors.complaint_text ? "invalid" : ""}
            id="complaint_text"
            name="complaint_text"
            value={form.complaint_text}
            onChange={handleChange}
            placeholder="Опишите причину жалобы"
          />
          <FieldError message={fieldErrors.complaint_text} />
        </div>
      </form>
    </Modal>
  );
}