import { Link } from "react-router-dom";

function formatDate(value) {
  if (!value) {
    return "Дата не указана";
  }

  return new Date(value).toLocaleString("ru-RU");
}

export function NotificationsList({
  notifications = [],
  onMarkRead,
  onDelete
}) {
  if (notifications.length === 0) {
    return (
      <div className="empty-state">
        <h3>Уведомлений пока нет</h3>
        <p>Здесь будут отображаться уведомления о регистрациях, изменениях, жалобах и отзывах.</p>
      </div>
    );
  }

  return (
    <div className="notifications-list">
      {notifications.map((notification) => (
        <article
          className={`notification-card ${notification.is_read ? "" : "notification-unread"}`}
          key={notification.id}
        >
          <div className="notification-head">
            <div>
              <h3>{notification.title}</h3>
              <p className="muted">{formatDate(notification.created_at)}</p>
            </div>

            {!notification.is_read && (
              <span className="status-badge warning">Новое</span>
            )}
          </div>

          <p>{notification.message}</p>

          <div className="form-actions">
            {notification.action_url && (
              <Link className="btn btn-outline" to={notification.action_url}>
                Перейти
              </Link>
            )}

            {!notification.is_read && (
              <button
                className="btn btn-outline"
                type="button"
                onClick={() => onMarkRead(notification.id)}
              >
                Отметить прочитанным
              </button>
            )}

            <button
              className="btn btn-danger"
              type="button"
              onClick={() => onDelete(notification.id)}
            >
              Удалить
            </button>
          </div>
        </article>
      ))}
    </div>
  );
}