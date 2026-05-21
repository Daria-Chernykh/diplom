import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import {
  approveRegistration,
  getEventParticipants,
  getEventParticipantsExportUrl,
  rejectRegistration
} from "../../api/registrationsApi.js";
import { getAccessToken } from "../../api/httpClient.js";

function formatDate(value) {
  if (!value) {
    return "Дата не указана";
  }

  return new Date(value).toLocaleString("ru-RU");
}

function getStatusLabel(status) {
  if (status === "pending") {
    return "Ожидает подтверждения";
  }

  if (status === "registered") {
    return "Зарегистрирован";
  }

  if (status === "rejected") {
    return "Отклонено";
  }

  if (status === "canceled") {
    return "Отменено";
  }

  return status || "Не указан";
}

export function RegisteredParticipantsPage() {
  const { eventId } = useParams();

  const [participants, setParticipants] = useState([]);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  async function loadParticipants() {
    setIsLoading(true);
    setError("");

    try {
      const response = await getEventParticipants(eventId);
      setParticipants(response.participants || []);
    } catch (requestError) {
      setError(requestError.message || "Не удалось загрузить список участников.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    loadParticipants();
  }, [eventId]);

  async function handleApprove(registrationId) {
    setError("");
    setMessage("");

    try {
      const response = await approveRegistration(registrationId);
      setMessage(response.message || "Заявка подтверждена.");
      await loadParticipants();
    } catch (requestError) {
      setError(requestError.message || "Не удалось подтвердить заявку.");
    }
  }

  async function handleReject(registrationId) {
    setError("");
    setMessage("");

    try {
      const response = await rejectRegistration(registrationId);
      setMessage(response.message || "Заявка отклонена.");
      await loadParticipants();
    } catch (requestError) {
      setError(requestError.message || "Не удалось отклонить заявку.");
    }
  }

  async function handleExport() {
    setError("");

    try {
      const token = getAccessToken();
      const response = await fetch(getEventParticipantsExportUrl(eventId), {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error("Не удалось экспортировать список участников.");
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");

      link.href = url;
      link.download = `event_${eventId}_participants.xlsx`;
      document.body.appendChild(link);
      link.click();
      link.remove();

      window.URL.revokeObjectURL(url);
    } catch (requestError) {
      setError(requestError.message || "Не удалось экспортировать список участников.");
    }
  }

  return (
    <main className="page">
      <section className="title-box">
        <h1>Зарегистрированные участники</h1>
      </section>

      <section className="content single-content">
        {error && <div className="error-box">{error}</div>}
        {message && <div className="success-box">{message}</div>}

        <div className="form-actions">
          <button className="btn btn-outline" type="button" onClick={handleExport}>
            Экспортировать в Excel
          </button>
        </div>

        {isLoading && <div className="loading-screen">Загрузка участников...</div>}

        {!isLoading && participants.length === 0 && (
          <div className="empty-state">
            <h3>Участников пока нет</h3>
            <p>После регистрации пользователей список появится на этой странице.</p>
          </div>
        )}

        {!isLoading && participants.length > 0 && (
          <div className="table-wrapper">
            <table className="table">
              <thead>
                <tr>
                  <th>Пользователь</th>
                  <th>Email</th>
                  <th>Статус</th>
                  <th>Дата подачи</th>
                  <th>Ответы</th>
                  <th>Действия</th>
                </tr>
              </thead>

              <tbody>
                {participants.map((registration) => (
                  <tr key={registration.id}>
                    <td>{registration.user?.full_name || "Пользователь"}</td>
                    <td>{registration.user?.email || "Не указан"}</td>
                    <td>{getStatusLabel(registration.status)}</td>
                    <td>{formatDate(registration.submitted_at)}</td>
                    <td>
                      {registration.answers && Object.keys(registration.answers).length > 0
                        ? Object.entries(registration.answers).map(([key, value]) => (
                            <div key={key}>
                              <strong>{key}:</strong> {String(value)}
                            </div>
                          ))
                        : "Нет ответов"}
                    </td>
                    <td>
                      {registration.status === "pending" ? (
                        <div className="table-actions">
                          <button
                            className="btn btn-primary"
                            type="button"
                            onClick={() => handleApprove(registration.id)}
                          >
                            Подтвердить
                          </button>

                          <button
                            className="btn btn-danger"
                            type="button"
                            onClick={() => handleReject(registration.id)}
                          >
                            Отклонить
                          </button>
                        </div>
                      ) : (
                        <span className="muted">Действия недоступны</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </main>
  );
}