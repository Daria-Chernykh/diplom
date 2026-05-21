import { API_BASE_URL, apiRequestWithRefresh } from "./httpClient.js";

export function getMyRegistrations() {
  return apiRequestWithRefresh("/registrations/user", {
    method: "GET"
  });
}

export function getMyRegistrationArchive() {
  return apiRequestWithRefresh("/registrations/user/archive", {
    method: "GET"
  });
}

export function getEventRegistrationFields(eventId) {
  return apiRequestWithRefresh(`/registrations/events/${eventId}/fields`, {
    method: "GET"
  });
}

export function getEventRegistrationForm(eventId) {
  return getEventRegistrationFields(eventId);
}

export function getUserEventRegistration(eventId) {
  return apiRequestWithRefresh(`/registrations/events/${eventId}/status`, {
    method: "GET"
  });
}

export function createInternalRegistration(eventId, payload) {
  return apiRequestWithRefresh(`/registrations/events/${eventId}/internal`, {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function submitEventRegistration(eventId, answers) {
  return createInternalRegistration(eventId, { answers });
}

export function confirmExternalRegistration(eventId) {
  return apiRequestWithRefresh(`/registrations/events/${eventId}/external`, {
    method: "POST"
  });
}

export function cancelRegistration(registrationId) {
  return apiRequestWithRefresh(`/registrations/${registrationId}/cancel`, {
    method: "PATCH"
  });
}

export function approveRegistration(registrationId) {
  return apiRequestWithRefresh(`/registrations/${registrationId}/approve`, {
    method: "PATCH"
  });
}

export function rejectRegistration(registrationId) {
  return apiRequestWithRefresh(`/registrations/${registrationId}/reject`, {
    method: "PATCH"
  });
}

export function getEventParticipants(eventId) {
  return apiRequestWithRefresh(`/registrations/events/${eventId}/participants`, {
    method: "GET"
  });
}

export function getEventParticipantsExportUrl(eventId) {
  return `${API_BASE_URL}/api/registrations/events/${eventId}/participants/export`;
}