import { apiRequestWithRefresh } from "./httpClient.js";

function buildQuery(params = {}) {
  const searchParams = new URLSearchParams();

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      searchParams.set(key, value);
    }
  });

  const query = searchParams.toString();

  return query ? `?${query}` : "";
}

export function getCurrentUserProfile() {
  return apiRequestWithRefresh("/users/profile", {
    method: "GET"
  });
}

export function updateCurrentUserProfile(payload) {
  return apiRequestWithRefresh("/users/profile", {
    method: "PUT",
    body: JSON.stringify(payload)
  });
}

export function changeCurrentUserPassword(payload) {
  return apiRequestWithRefresh("/users/password", {
    method: "PUT",
    body: JSON.stringify(payload)
  });
}

export function getAdminUsers(params = {}) {
  return apiRequestWithRefresh(`/users${buildQuery(params)}`, {
    method: "GET"
  });
}

export function blockUser(userId) {
  return apiRequestWithRefresh(`/users/${userId}/block`, {
    method: "PATCH"
  });
}

export function unblockUser(userId) {
  return apiRequestWithRefresh(`/users/${userId}/unblock`, {
    method: "PATCH"
  });
}