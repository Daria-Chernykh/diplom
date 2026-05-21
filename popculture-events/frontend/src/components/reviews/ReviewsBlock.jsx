import { useEffect, useMemo, useState } from "react";

import { createReviewComplaint } from "../../api/complaintsApi.js";
import { buildFileUrl } from "../../api/filesApi.js";
import {
  deleteEventReview,
  getEventReviews
} from "../../api/reviewsApi.js";
import { ReviewForm } from "./ReviewForm.jsx";

function getSortLabel(value) {
  if (value === "positive") {
    return "Сначала положительные";
  }

  if (value === "negative") {
    return "Сначала отрицательные";
  }

  return "Сначала новые";
}

function getRatingText(rating) {
  return `${rating} из 5`;
}

export function ReviewsBlock({ event }) {
  const [reviews, setReviews] = useState([]);
  const [hiddenReviews, setHiddenReviews] = useState({});
  const [ratingInfo, setRatingInfo] = useState(event.event_rating || null);
  const [sort, setSort] = useState("new");
  const [openMenuReviewId, setOpenMenuReviewId] = useState(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  const ownReview = useMemo(
    () => reviews.find((review) => review.is_own),
    [reviews]
  );

  async function loadReviews(selectedSort = sort) {
    setIsLoading(true);
    setError("");

    try {
      const response = await getEventReviews(event.id, {
        sort: selectedSort
      });

      setReviews(response.reviews || []);
      setRatingInfo(response.rating || null);
    } catch (requestError) {
      setError(requestError.message || "Не удалось загрузить отзывы.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    loadReviews(sort);
  }, [event.id, sort]);

  async function handleDelete(reviewId) {
    setError("");
    setMessage("");

    try {
      await deleteEventReview(reviewId);
      await loadReviews(sort);
      setMessage("Отзыв удален.");
    } catch (requestError) {
      setError(requestError.message || "Не удалось удалить отзыв.");
    }
  }

  async function handleComplaint(reviewId) {
    setError("");
    setMessage("");
    setOpenMenuReviewId(null);

    try {
      await createReviewComplaint(reviewId);

      setHiddenReviews((current) => ({
        ...current,
        [reviewId]: true
      }));

      setMessage("Жалоба на отзыв отправлена.");
    } catch (requestError) {
      setError(requestError.message || "Не удалось отправить жалобу на отзыв.");
    }
  }

  function cancelLocalHide(reviewId) {
    setHiddenReviews((current) => {
      const next = { ...current };
      delete next[reviewId];
      return next;
    });
  }

  function handleCreated(response) {
    setMessage(response.message || "Отзыв опубликован.");
    loadReviews(sort);
  }

  return (
    <section className="reviews-section">
      <div className="reviews-head">
        <div>
          <h2>Отзывы о мероприятии</h2>

          <p className="muted">
            {ratingInfo?.reviews_count > 0
              ? `Средняя оценка: ${ratingInfo.average_rating} · отзывов: ${ratingInfo.reviews_count}`
              : "Отзывов пока нет."}
          </p>
        </div>

        <div className="field compact-field">
          <label htmlFor="review-sort">Сортировка</label>
          <select
            id="review-sort"
            value={sort}
            onChange={(event) => setSort(event.target.value)}
          >
            <option value="new">{getSortLabel("new")}</option>
            <option value="positive">{getSortLabel("positive")}</option>
            <option value="negative">{getSortLabel("negative")}</option>
          </select>
        </div>
      </div>

      {!ownReview && (
        <ReviewForm eventId={event.id} onCreated={handleCreated} />
      )}

      {ownReview && (
        <div className="own-review-note">
          Свой отзыв отображается первым. Повторно оставить отзыв можно только после удаления текущего.
        </div>
      )}

      {error && <div className="error-box">{error}</div>}
      {message && <div className="success-box">{message}</div>}

      {isLoading && <div className="loading-screen">Загрузка отзывов...</div>}

      {!isLoading && (
        <div className="reviews-list">
          {reviews.length === 0 && (
            <div className="note">Отзывов пока нет.</div>
          )}

          {reviews.map((review) => {
            if (hiddenReviews[review.id]) {
              return (
                <article className="review-hidden-card" key={review.id}>
                  <h3>Отзыв временно скрыт</h3>
                  <p>На отзыв отправлена жалоба, он ожидает проверки администратором.</p>

                  <button
                    className="btn btn-outline"
                    type="button"
                    onClick={() => cancelLocalHide(review.id)}
                  >
                    Отмена
                  </button>
                </article>
              );
            }

            return (
              <article className={review.is_own ? "review-card own-review" : "review-card"} key={review.id}>
                <div className="review-card-head">
                  <div>
                    <h3>{review.user?.full_name || "Пользователь"}</h3>
                    <p className="muted">
                      {review.created_at
                        ? new Date(review.created_at).toLocaleString("ru-RU")
                        : "Дата не указана"}
                    </p>
                  </div>

                  <div className="review-head-actions">
                    <div className="review-rating">
                      <span>★</span>
                      {getRatingText(review.rating)}
                    </div>

                    {!review.is_own && (
                      <div className="review-menu">
                        <button
                          className="review-menu-button"
                          type="button"
                          onClick={() =>
                            setOpenMenuReviewId(
                              openMenuReviewId === review.id ? null : review.id
                            )
                          }
                          aria-label="Открыть меню отзыва"
                        >
                          ⋯
                        </button>

                        {openMenuReviewId === review.id && (
                          <div className="review-menu-dropdown">
                            <button
                              type="button"
                              onClick={() => handleComplaint(review.id)}
                            >
                              Пометить как неприемлемый контент
                            </button>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>

                {review.comment && <p className="review-comment">{review.comment}</p>}

                {review.photos.length > 0 && (
                  <div className="review-photos">
                    {review.photos.map((photo) => (
                      <img
                        src={buildFileUrl(photo.file_url)}
                        alt={photo.original_filename}
                        key={photo.id}
                      />
                    ))}
                  </div>
                )}

                {review.is_own && (
                  <div className="actions-row">
                    <button
                      className="btn btn-danger"
                      type="button"
                      onClick={() => handleDelete(review.id)}
                    >
                      Удалить отзыв
                    </button>
                  </div>
                )}
              </article>
            );
          })}
        </div>
      )}
    </section>
  );
}