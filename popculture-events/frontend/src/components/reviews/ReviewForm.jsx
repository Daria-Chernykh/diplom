import { useState } from "react";

import { createEventReview } from "../../api/reviewsApi.js";
import { FieldError } from "../ui/FieldError.jsx";
import {
  getBackendFieldErrors,
  hasErrors,
  validateRatingValue
} from "../../utils/validation.js";

function validateForm(form, photos) {
  const errors = {};

  const ratingError = validateRatingValue(form.rating);

  if (ratingError) {
    errors.rating = ratingError;
  }

  if (form.comment.length > 3000) {
    errors.comment = "Текст отзыва не должен превышать 3000 символов.";
  }

  if (photos.length > 5) {
    errors.photos = "К отзыву можно прикрепить не более 5 фотографий.";
  }

  return errors;
}

export function ReviewForm({ eventId, onCreated }) {
  const [form, setForm] = useState({
    rating: "",
    comment: ""
  });

  const [photos, setPhotos] = useState([]);
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

  function handleRatingChange(value) {
    setForm((current) => ({
      ...current,
      rating: value
    }));

    setFieldErrors((current) => ({
      ...current,
      rating: ""
    }));
  }

  function handlePhotosChange(event) {
    const selectedFiles = Array.from(event.target.files || []);

    setPhotos(selectedFiles);

    setFieldErrors((current) => ({
      ...current,
      photos: ""
    }));
  }

  async function handleSubmit(event) {
    event.preventDefault();

    const errors = validateForm(form, photos);
    setFieldErrors(errors);

    if (hasErrors(errors)) {
      setError("Проверьте заполнение отзыва.");
      return;
    }

    setIsSubmitting(true);
    setError("");

    try {
      const response = await createEventReview(eventId, {
        rating: form.rating,
        comment: form.comment,
        photos
      });

      setForm({
        rating: "",
        comment: ""
      });
      setPhotos([]);
      setFieldErrors({});

      if (onCreated) {
        onCreated(response.review);
      }
    } catch (requestError) {
      setFieldErrors(getBackendFieldErrors(requestError));
      setError(requestError.message || "Не удалось опубликовать отзыв.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form className="form" onSubmit={handleSubmit} noValidate>
      <section className="form-section">
        <h3>Оставить отзыв</h3>

        {error && <div className="error-box">{error}</div>}

        <div>
          <label className="field-label">Оценка мероприятия</label>

          <div className="rating-select">
            {[0, 1, 2, 3, 4, 5].map((rating) => (
              <button
                className={`rating-option ${Number(form.rating) === rating ? "active" : ""}`}
                key={rating}
                type="button"
                onClick={() => handleRatingChange(String(rating))}
              >
                {rating}
              </button>
            ))}
          </div>

          <FieldError message={fieldErrors.rating} />
        </div>

        <div className="field">
          <label htmlFor="comment">Комментарий</label>
          <textarea
            className={fieldErrors.comment ? "invalid" : ""}
            id="comment"
            name="comment"
            value={form.comment}
            onChange={handleChange}
            placeholder="Комментарий необязателен"
          />
          <FieldError message={fieldErrors.comment} />
        </div>

        <div className="field">
          <label htmlFor="photos">Фотографии</label>
          <input
            className={fieldErrors.photos ? "invalid" : ""}
            id="photos"
            type="file"
            accept="image/jpeg,image/png,image/webp"
            multiple
            onChange={handlePhotosChange}
          />
          <span className="field-hint">Можно прикрепить до 5 фотографий.</span>
          <FieldError message={fieldErrors.photos} />
        </div>
      </section>

      <div className="form-actions">
        <button className="btn btn-primary" type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Публикация..." : "Опубликовать отзыв"}
        </button>
      </div>
    </form>
  );
}