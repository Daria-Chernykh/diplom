import { useEffect, useState } from "react";
import { Link, useParams, useSearchParams } from "react-router-dom";

import { getEventById } from "../../api/eventsApi.js";
import { EventPageLayout } from "../../components/events/EventPageLayout.jsx";
import { AdminReviewsBlock } from "../../components/reviews/AdminReviewsBlock.jsx";

export function EventPastAdminPage() {
  const { eventId } = useParams();
  const [searchParams] = useSearchParams();

  const highlightedReviewId = Number(searchParams.get("reviewId"));
  const complaintId = Number(searchParams.get("complaintId"));

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
          <Link className="btn btn-outline" to="/admin">
            Назад к жалобам
          </Link>
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

  return (
    <EventPageLayout
      event={event}
      warning={
        <div className="warning-note">
          Режим администратора. Спорный отзыв выделен красным цветом.
        </div>
      }
      actions={
        <Link className="btn btn-outline" to="/admin">
          Назад к жалобам
        </Link>
      }
    >
      <AdminReviewsBlock
        event={event}
        highlightedReviewId={highlightedReviewId}
        complaintId={complaintId}
      />
    </EventPageLayout>
  );
}