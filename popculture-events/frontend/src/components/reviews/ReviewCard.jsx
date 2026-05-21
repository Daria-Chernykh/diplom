import { buildFileUrl } from "../../api/filesApi.js";

function formatDate(value) {
  if (!value) {
    return "Дата не указана";
  }

  return new Date(value).toLocaleString("ru-RU");
}

export function ReviewCard({ review, actions, highlighted = false }) {
  const photos = review.photos || [];

  return (
    <article className={`review-card ${review.is_own ? "own-review" : ""} ${highlighted ? "review-highlighted" : ""}`}>
      <div className="review-card-head">
        <div>
          <h3>{review.user?.full_name || "Пользователь"}</h3>
          <p className="muted">{formatDate(review.created_at)}</p>
        </div>

        <div className="review-rating">★ {review.rating}</div>
      </div>

      {review.comment && <p className="review-comment">{review.comment}</p>}

      {photos.length > 0 && (
        <div className="review-photos">
          {photos.map((photo) => (
            <img
              key={photo.id}
              src={buildFileUrl(photo.file_url)}
              alt="Фотография к отзыву"
            />
          ))}
        </div>
      )}

      {actions && <div className="review-actions">{actions}</div>}
    </article>
  );
}