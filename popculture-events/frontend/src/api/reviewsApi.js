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

export function getEventReviews(eventId, params = {}) {
  return apiRequestWithRefresh(`/reviews/events/${eventId}${buildQuery(params)}`, {
    method: "GET"
  });
}

export function getEventReviewsForAdmin(eventId, params = {}) {
  return apiRequestWithRefresh(`/reviews/admin/events/${eventId}${buildQuery(params)}`, {
    method: "GET"
  });
}

export function createEventReview(eventId, payload) {
  const formData = new FormData();

  formData.append("rating", String(payload.rating));
  formData.append("comment", payload.comment || "");

  payload.photos.forEach((photo) => {
    formData.append("photos", photo);
  });

  return apiRequestWithRefresh(`/reviews/events/${eventId}`, {
    method: "POST",
    body: formData
  });
}

export function deleteEventReview(reviewId) {
  return apiRequestWithRefresh(`/reviews/${reviewId}`, {
    method: "DELETE"
  });
}