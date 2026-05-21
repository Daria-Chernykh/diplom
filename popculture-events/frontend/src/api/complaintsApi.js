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

export function createEventComplaint(eventId, payload) {
  return apiRequestWithRefresh(`/complaints/events/${eventId}`, {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function createReviewComplaint(reviewId) {
  return apiRequestWithRefresh(`/complaints/reviews/${reviewId}`, {
    method: "POST"
  });
}

export function getAdminEventComplaints(params = {}) {
  return apiRequestWithRefresh(`/complaints/admin/events${buildQuery(params)}`, {
    method: "GET"
  });
}

export function getAdminReviewComplaints() {
  return apiRequestWithRefresh("/complaints/admin/reviews", {
    method: "GET"
  });
}

export function restoreEventComplaint(complaintId) {
  return apiRequestWithRefresh(`/complaints/admin/events/${complaintId}/restore`, {
    method: "POST"
  });
}

export function rejectEventComplaint(complaintId) {
  return apiRequestWithRefresh(`/complaints/admin/events/${complaintId}/reject`, {
    method: "POST"
  });
}

export function keepEventBlocked(complaintId) {
  return apiRequestWithRefresh(`/complaints/admin/events/${complaintId}/keep-blocked`, {
    method: "POST"
  });
}

export function blockEventOrganizer(complaintId) {
  return apiRequestWithRefresh(`/complaints/admin/events/${complaintId}/block-organizer`, {
    method: "POST"
  });
}

export function blockFalseEventComplainant(complaintId) {
  return apiRequestWithRefresh(`/complaints/admin/events/${complaintId}/block-complainant`, {
    method: "POST"
  });
}

export function keepReviewAfterComplaint(complaintId) {
  return apiRequestWithRefresh(`/complaints/admin/reviews/${complaintId}/keep`, {
    method: "POST"
  });
}

export function deleteReviewAndBlockAuthor(complaintId) {
  return apiRequestWithRefresh(`/complaints/admin/reviews/${complaintId}/delete-and-block`, {
    method: "POST"
  });
}

export function getEventComplaints(params = {}) {
  return getAdminEventComplaints(params);
}

export function getReviewComplaints() {
  return getAdminReviewComplaints();
}

export function resolveEventComplaint(complaintId, action) {
  if (action === "restore_event") {
    return restoreEventComplaint(complaintId);
  }

  if (action === "keep_blocked") {
    return keepEventBlocked(complaintId);
  }

  if (action === "block_organizer") {
    return blockEventOrganizer(complaintId);
  }

  if (action === "block_false_reporter") {
    return blockFalseEventComplainant(complaintId);
  }

  if (action === "reject_complaint") {
    return rejectEventComplaint(complaintId);
  }

  throw new Error("Неизвестное действие по жалобе.");
}

export function deleteReviewAfterComplaint(complaintId) {
  return deleteReviewAndBlockAuthor(complaintId);
}

export function blockAuthorAndDeleteReviewAfterComplaint(complaintId) {
  return deleteReviewAndBlockAuthor(complaintId);
}