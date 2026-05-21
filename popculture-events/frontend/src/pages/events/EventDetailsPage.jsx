import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import { getEventById } from "../../api/eventsApi.js";
import { EventExternalPage } from "./EventExternalPage.jsx";
import { EventInternalPage } from "./EventInternalPage.jsx";
import { EventPastPage } from "./EventPastPage.jsx";
import { EventWithoutRegistrationPage } from "./EventWithoutRegistrationPage.jsx";

export function EventDetailsPage() {
  const { eventId } = useParams();

  const [event, setEvent] = useState(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadEvent() {
      setIsLoading(true);
      setError("");

      try {
        const response = await getEventById(eventId);
        setEvent(response.event);
      } catch (requestError) {
        setError(requestError.message || "Не удалось загрузить мероприятие.");
      } finally {
        setIsLoading(false);
      }
    }

    loadEvent();
  }, [eventId]);

  if (isLoading) {
    return <div className="loading-screen">Загрузка мероприятия...</div>;
  }

  if (error) {
    return (
      <main className="page">
        <section className="card">
          <h1>Мероприятие недоступно</h1>
          <div className="error-box">{error}</div>
        </section>
      </main>
    );
  }

  if (!event) {
    return (
      <main className="page">
        <section className="card">
          <h1>Мероприятие не найдено</h1>
        </section>
      </main>
    );
  }

  if (event.status === "archived") {
    return <EventPastPage event={event} />;
  }

  if (event.registration_type === "internal") {
    return <EventInternalPage event={event} />;
  }

  if (event.registration_type === "external") {
    return <EventExternalPage event={event} />;
  }

  return <EventWithoutRegistrationPage event={event} />;
}