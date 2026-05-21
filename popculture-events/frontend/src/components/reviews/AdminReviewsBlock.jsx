import { useEffect, useState } from "react";

import {
  blockAuthorAndDeleteReviewAfterComplaint,
  keepReviewAfterComplaint
} from "../../api/complaintsApi.js";
import { buildFileUrl } from "../../api/filesApi.js";
import { getEventReviewsForAdmin } from "../../api/reviewsApi.js";

function getRatingText(rating) {
  return `${rating} из 5`;
}

export function AdminReviewsBlock({ event, highlightedReviewId, complaintId }) {
  const [reviews, setReviews] = useState([]);
  const [ratingInfo, setRatingInfo] = useState(event.event_rating || null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  async function loadReviews() {
    setIsLoading(true);
    setError("");

    try {
      const response = await getEventReviewsForAdmin(event.id, {
        highlighted_review_id: highlightedReviewId
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
    loadReviews();
  }, [event.id, highlightedReviewId]);

  async function runAction(action, successMessage) {
    setError("");
    setMessage("");

    try {
      await action();
      await loadReviews();
      setMessage(successMessage);
    } catch (requestError) {
      setError(requestError.message || "Не удалось выполнить действие.");
    }
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
      </div>

      {error && <div className="error-box">{error}</div>}
      {message && <div className="success-box">{message}</div>}

      {isLoading && <div className="loading-screen">Загрузка отзывов...</div>}

      {!isLoading && (
        <div className="reviews-list">
          {reviews.length === 0 && (
            <div className="note">Отзывов пока нет.</div>
          )}

          {reviews.map((review) => (
            <article
              className={review.is_highlighted ? "review-card admin-highlighted-review" : "review-card"}
              key={review.id}
              id={`review-${review.id}`}
            >
              <div className="review-card-head">
                <div>
                  <h3>{review.user?.full_name || "Пользователь"}</h3>
                  <p className="muted">
                    {review.created_at
                      ? new Date(review.created_at).toLocaleString("ru-RU")
                      : "Дата не указана"}
                  </p>
                </div>

                <div className="review-rating">
                  <span>★</span>
                  {getRatingText(review.rating)}
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

              {review.is_highlighted && complaintId && (
                <div className="admin-review-actions">
                  <div className="warning-note">
                    На этот отзыв подана жалоба. Необходимо принять решение по результатам проверки.
                  </div>

                  <div className="actions-row">
                    <button
                      className="btn btn-outline"
                      type="button"
                      onClick={() =>
                        runAction(
                          () => keepReviewAfterComplaint(complaintId),
                          "Отзыв оставлен. Жалоба удалена."
                        )
                      }
                    >
                      Оставить отзыв
                    </button>

                    <button
                      className="btn btn-danger"
                      type="button"
                      onClick={() =>
                        runAction(
                          () => blockAuthorAndDeleteReviewAfterComplaint(complaintId),
                          "Пользователь заблокирован, отзыв удален."
                        )
                      }
                    >
                      Заблокировать пользователя и удалить отзыв
                    </button>
                  </div>
                </div>
              )}
            </article>
          ))}
        </div>
      )}
    </section>
  );
}