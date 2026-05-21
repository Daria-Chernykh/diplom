import { API_BASE_URL, apiRequest, apiRequestWithRefresh } from "./httpClient.js";

export function buildFileUrl(fileUrl) {
  if (!fileUrl) {
    return "";
  }

  if (fileUrl.startsWith("http")) {
    return fileUrl;
  }

  return `${API_BASE_URL}${fileUrl}`;
}

function uploadFile(path, file) {
  const formData = new FormData();
  formData.append("file", file);

  return apiRequestWithRefresh(path, {
    method: "POST",
    body: formData
  });
}

export function uploadEventImage(eventId, file) {
  return uploadFile(`/files/events/${eventId}/image`, file);
}

export function uploadUserProfileImage(file) {
  return uploadFile("/files/profile-image", file);
}

export function uploadOrganizerImage(file) {
  return uploadFile("/files/organizer-image", file);
}

export function deleteFile(fileId) {
  return apiRequestWithRefresh(`/files/${fileId}`, {
    method: "DELETE"
  });
}

export function getEntityFiles(entityType, entityId) {
  return apiRequest(`/files/entities/${entityType}/${entityId}`, {
    method: "GET"
  });
}

export function getEntityMainFile(entityType, entityId) {
  return apiRequest(`/files/entities/${entityType}/${entityId}/main`, {
    method: "GET"
  });
}