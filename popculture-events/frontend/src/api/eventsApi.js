import { apiRequest, apiRequestWithRefresh } from "./httpClient.js";

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

export function getEvents(params = {}) {
  return apiRequest(`/events${buildQuery(params)}`, {
    method: "GET"
  });
}

export function getCatalogEvents(params = {}) {
  return getEvents(params);
}

export function getEventById(eventId) {
  return apiRequestWithRefresh(`/events/${eventId}`, {
    method: "GET"
  });
}

export function getMyEvents(params = {}) {
  return apiRequestWithRefresh(`/events/organizer${buildQuery(params)}`, {
    method: "GET"
  });
}

export function getOrganizerEvents(params = {}) {
  return getMyEvents(params);
}

export function createEvent(payload) {
  return apiRequestWithRefresh("/events", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function getEventForEdit(eventId) {
  return apiRequestWithRefresh(`/events/organizer/${eventId}`, {
    method: "GET"
  });
}

export function getOrganizerEventById(eventId) {
  return getEventForEdit(eventId);
}

export function updateEvent(eventId, payload) {
  return apiRequestWithRefresh(`/events/organizer/${eventId}`, {
    method: "PUT",
    body: JSON.stringify(payload)
  });
}