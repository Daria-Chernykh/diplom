const ACCESS_TOKEN_KEY = "popculture_access_token";
const REFRESH_TOKEN_KEY = "popculture_refresh_token";

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:5000";

export function getAccessToken() {
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function getRefreshToken() {
  return localStorage.getItem(REFRESH_TOKEN_KEY);
}

export function setAuthTokens(accessToken, refreshToken) {
  if (accessToken) {
    localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
  }

  if (refreshToken) {
    localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
  }
}

export function removeAuthTokens() {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
}

function buildHeaders(options = {}) {
  const headers = new Headers(options.headers || {});

  if (!(options.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const token = options.token || getAccessToken();

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  return headers;
}

async function parseResponse(response) {
  let data = null;

  try {
    data = await response.json();
  } catch {
    data = null;
  }

  return data;
}

export async function apiRequest(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}/api${path}`, {
    ...options,
    headers: buildHeaders(options)
  });

  const data = await parseResponse(response);

  if (!response.ok) {
    const error = new Error(data?.error?.message || "Ошибка запроса.");
    error.status = response.status;
    error.details = data?.error?.details || null;
    throw error;
  }

  return data;
}

export async function apiRequestWithRefresh(path, options = {}) {
  try {
    return await apiRequest(path, options);
  } catch (error) {
    if (error.status !== 401) {
      throw error;
    }

    const refreshToken = getRefreshToken();

    if (!refreshToken) {
      removeAuthTokens();
      throw error;
    }

    try {
      const refreshResponse = await apiRequest("/auth/refresh", {
        method: "POST",
        token: refreshToken
      });

      setAuthTokens(refreshResponse.access_token, refreshResponse.refresh_token);

      return await apiRequest(path, options);
    } catch (refreshError) {
      removeAuthTokens();
      throw refreshError;
    }
  }
}