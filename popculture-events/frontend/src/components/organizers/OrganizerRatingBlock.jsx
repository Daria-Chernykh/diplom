import { useState } from "react";

import {
  deleteOrganizerRating,
  setOrganizerRating
} from "../../api/organizersApi.js";

function getRatingText(ratingInfo) {
  if (!ratingInfo || ratingInfo.average_rating === null || ratingInfo.average_rating === undefined) {
    return "Рейтинг пока не сформирован";
  }

  return `★ ${ratingInfo.average_rating} · оценок: ${ratingInfo.total_sources_count}`;
}

export function OrganizerRatingBlock({ organizer, onChanged }) {
  const [selectedRating, setSelectedRating] = useState(organizer.own_rating?.rating ?? 5);
  const [fieldErrors, setFieldErrors] = useState({});
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [isSaving, setIsSaving] = useState(false);

  async function handleSave() {
    setError("");
    setMessage("");
    setFieldErrors({});
    setIsSaving(true);

    try {
      const response = await setOrganizerRating(organizer.id, selectedRating);
      setMessage(response.message || "Оценка организатора сохранена.");
      onChanged(response.organizer);
    } catch (requestError) {
      setError(requestError.message || "Не удалось сохранить оценку.");
      setFieldErrors(requestError.data?.error?.details || {});
    } finally {
      setIsSaving(false);
    }
  }

  async function handleDelete() {
    setError("");
    setMessage("");
    setFieldErrors({});
    setIsSaving(true);

    try {
      const response = await deleteOrganizerRating(organizer.id);
      setMessage(response.message || "Оценка организатора удалена.");
      onChanged(response.organizer);
    } catch (requestError) {
      setError(requestError.message || "Не удалось удалить оценку.");
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <section className="organizer-rating-block">
      <div>
        <h2>Оценка организатора</h2>
        <p className="muted">{getRatingText(organizer.organizer_rating)}</p>
      </div>

      <div className="rating-source-details">
        <span>Отзывы на мероприятия: {organizer.organizer_rating?.event_reviews_count || 0}</span>
        <span>Оценки страницы организатора: {organizer.organizer_rating?.direct_ratings_count || 0}</span>
      </div>

      <div className="organizer-rating-form">
        <div className="field">
          <label>Ваша оценка</label>

          <div className="star-rating-input" role="radiogroup" aria-label="Оценка организатора">
            {[0, 1, 2, 3, 4, 5].map((rating) => (
              <button
                className={rating <= selectedRating ? "star-button active" : "star-button"}
                type="button"
                key={rating}
                onClick={() => setSelectedRating(rating)}
                disabled={isSaving}
              >
                ★
                <span>{rating}</span>
              </button>
            ))}
          </div>

          {fieldErrors.rating && <span className="field-error">{fieldErrors.rating}</span>}
        </div>

        {error && <div className="error-box">{error}</div>}
        {message && <div className="success-box">{message}</div>}

        <div className="actions-row">
          <button className="btn btn-primary" type="button" onClick={handleSave} disabled={isSaving}>
            {organizer.own_rating ? "Изменить оценку" : "Поставить оценку"}
          </button>

          {organizer.own_rating && (
            <button className="btn btn-danger" type="button" onClick={handleDelete} disabled={isSaving}>
              Удалить оценку
            </button>
          )}
        </div>
      </div>
    </section>
  );
}