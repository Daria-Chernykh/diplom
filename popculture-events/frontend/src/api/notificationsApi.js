import { apiRequestWithRefresh } from "./httpClient.js";

export function getNotifications(params = {}) {
  const searchParams = new URLSearchParams();

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      searchParams.set(key, value);
    }
  });

  const query = searchParams.toString();

  return apiRequestWithRefresh(`/notifications${query ? `?${query}` : ""}`, {
    method: "GET"
  });
}

export function markNotificationRead(notificationId) {
  return apiRequestWithRefresh(`/notifications/${notificationId}/read`, {
    method: "PATCH"
  });
}

export function markAllNotificationsRead() {
  return apiRequestWithRefresh("/notifications/read-all", {
    method: "PATCH"
  });
}

export function deleteNotification(notificationId) {
  return apiRequestWithRefresh(`/notifications/${notificationId}`, {
    method: "DELETE"
  });
}

export function deleteAllNotifications() {
  return apiRequestWithRefresh("/notifications", {
    method: "DELETE"
  });
}