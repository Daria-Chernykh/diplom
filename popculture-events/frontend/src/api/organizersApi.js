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

export function getPublicOrganizers(params = {}) {
  return apiRequestWithRefresh(`/organizers${buildQuery(params)}`, {
    method: "GET"
  });
}

export function getOrganizers(params = {}) {
  return getPublicOrganizers(params);
}

export function getOrganizerById(organizerId) {
  return apiRequestWithRefresh(`/organizers/${organizerId}`, {
    method: "GET"
  });
}

export async function getOrganizerArchive(organizerId) {
  const response = await getOrganizerById(organizerId);

  return {
    success: response.success,
    events: response.archived_events || []
  };
}

export function getAdminOrganizers(params = {}) {
  return apiRequestWithRefresh(`/organizers/admin${buildQuery(params)}`, {
    method: "GET"
  });
}

export function blockOrganizer(organizerId) {
  return apiRequestWithRefresh(`/organizers/admin/${organizerId}/block`, {
    method: "PATCH"
  });
}

export function unblockOrganizer(organizerId) {
  return apiRequestWithRefresh(`/organizers/admin/${organizerId}/unblock`, {
    method: "PATCH"
  });
}

export function setOrganizerRating(organizerId, rating) {
  return apiRequestWithRefresh(`/reviews/organizers/${organizerId}/rating`, {
    method: "PUT",
    body: JSON.stringify({ rating })
  });
}

export function deleteOrganizerRating(organizerId) {
  return apiRequestWithRefresh(`/reviews/organizers/${organizerId}/rating`, {
    method: "DELETE"
  });
}

export function getOwnOrganizerRating(organizerId) {
  return apiRequestWithRefresh(`/reviews/organizers/${organizerId}/rating`, {
    method: "GET"
  });
}