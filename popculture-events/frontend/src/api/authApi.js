import { apiRequest, apiRequestWithRefresh } from "./httpClient.js";

export function registerUser(payload) {
  return apiRequest("/auth/register", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function loginUser(payload) {
  return apiRequest("/auth/login", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function refreshAccessToken(refreshToken) {
  return apiRequest("/auth/refresh", {
    method: "POST",
    token: refreshToken
  });
}

export function logoutUser() {
  return apiRequestWithRefresh("/auth/logout", {
    method: "POST"
  });
}

export function getCurrentAuthUser() {
  return apiRequestWithRefresh("/auth/me", {
    method: "GET"
  });
}

export function acceptLegalDocuments(payload) {
  return apiRequestWithRefresh("/auth/accept-legal-documents", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}
