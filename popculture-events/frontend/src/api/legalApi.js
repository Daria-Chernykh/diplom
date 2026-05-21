import { API_BASE_URL, apiRequest, apiRequestWithRefresh } from "./httpClient.js";

export function getLegalDocuments() {
  return apiRequest("/legal/documents", {
    method: "GET"
  });
}

export function getActualLegalDocuments() {
  return getLegalDocuments();
}

export function acceptLegalDocuments() {
  return apiRequestWithRefresh("/auth/accept-legal-documents", {
    method: "POST"
  });
}

export function getLegalDocumentDownloadUrl(documentType) {
  return `${API_BASE_URL}/api/legal/documents/${documentType}/download`;
}