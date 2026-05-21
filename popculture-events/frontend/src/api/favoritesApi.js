import { apiRequestWithRefresh } from "./httpClient.js";

export function getFavoriteEvents() {
  return apiRequestWithRefresh("/favorites", {
    method: "GET"
  });
}

export function getFavoriteStatus(eventId) {
  return apiRequestWithRefresh(`/favorites/${eventId}/status`, {
    method: "GET"
  });
}

export function addFavorite(eventId) {
  return apiRequestWithRefresh(`/favorites/${eventId}`, {
    method: "POST"
  });
}

export function removeFavorite(eventId) {
  return apiRequestWithRefresh(`/favorites/${eventId}`, {
    method: "DELETE"
  });
}