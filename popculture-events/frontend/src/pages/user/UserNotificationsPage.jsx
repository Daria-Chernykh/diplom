import { useEffect, useState } from "react";

import {
  deleteAllNotifications,
  deleteNotification,
  getNotifications,
  markAllNotificationsRead,
  markNotificationRead
} from "../../api/notificationsApi.js";
import { NotificationsList } from "../../components/notifications/NotificationsList.jsx";

export function UserNotificationsPage() {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [onlyUnread, setOnlyUnread] = useState(false);

  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  async function loadNotifications() {
    setIsLoading(true);
    setError("");

    try {
      const response = await getNotifications({
        unread: onlyUnread ? "true" : ""
      });

      setNotifications(response.notifications || []);
      setUnreadCount(response.unread_count || 0);
    } catch (requestError) {
      setError(requestError.message || "Не удалось загрузить уведомления.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    loadNotifications();
  }, [onlyUnread]);

  async function handleMarkRead(notificationId) {
    setError("");
    setMessage("");

    try {
      const response = await markNotificationRead(notificationId);
      setMessage(response.message || "Уведомление отмечено как прочитанное.");
      await loadNotifications();
    } catch (requestError) {
      setError(requestError.message || "Не удалось отметить уведомление.");
    }
  }

  async function handleMarkAllRead() {
    setError("");
    setMessage("");

    try {
      const response = await markAllNotificationsRead();
      setMessage(response.message || "Все уведомления отмечены как прочитанные.");
      await loadNotifications();
    } catch (requestError) {
      setError(requestError.message || "Не удалось отметить уведомления.");
    }
  }

  async function handleDelete(notificationId) {
    setError("");
    setMessage("");

    try {
      const response = await deleteNotification(notificationId);
      setMessage(response.message || "Уведомление удалено.");
      await loadNotifications();
    } catch (requestError) {
      setError(requestError.message || "Не удалось удалить уведомление.");
    }
  }

  async function handleDeleteAll() {
    setError("");
    setMessage("");

    try {
      const response = await deleteAllNotifications();
      setMessage(response.message || "Уведомления удалены.");
      await loadNotifications();
    } catch (requestError) {
      setError(requestError.message || "Не удалось удалить уведомления.");
    }
  }

  return (
    <main className="page">
      <section className="title-box">
        <h1>Уведомления</h1>
        <p className="muted">Непрочитанные уведомления: {unreadCount}</p>
      </section>

      <section className="content single-content">
        {error && <div className="error-box">{error}</div>}
        {message && <div className="success-box">{message}</div>}

        <div className="toolbar">
          <label className="required-check">
            <input
              type="checkbox"
              checked={onlyUnread}
              onChange={(event) => setOnlyUnread(event.target.checked)}
            />
            Показать только непрочитанные
          </label>

          <button className="btn btn-outline" type="button" onClick={handleMarkAllRead}>
            Отметить все прочитанными
          </button>

          <button className="btn btn-danger" type="button" onClick={handleDeleteAll}>
            Удалить все
          </button>
        </div>

        {isLoading && <div className="loading-screen">Загрузка уведомлений...</div>}

        {!isLoading && (
          <NotificationsList
            notifications={notifications}
            onMarkRead={handleMarkRead}
            onDelete={handleDelete}
          />
        )}
      </section>
    </main>
  );
}