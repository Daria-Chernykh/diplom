import { EventMoreFromOrganizer } from "../../components/events/EventMoreFromOrganizer.jsx";
import { EventPageLayout } from "../../components/events/EventPageLayout.jsx";
import { ReviewsBlock } from "../../components/reviews/ReviewsBlock.jsx";

export function EventPastPage({ event }) {
  return (
    <EventPageLayout
      event={event}
      warning={
        <div className="info-note">
          Мероприятие завершено и находится в архиве. Регистрация, добавление в избранное
          и жалоба на карточку недоступны.
        </div>
      }
      actions={null}
    >
      <ReviewsBlock event={event} />

      <EventMoreFromOrganizer event={event} />
    </EventPageLayout>
  );
}