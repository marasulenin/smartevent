
import { useState } from "react";

function EventCard({ event, onView }) {
  const [imageError, setImageError] = useState(false);

  const eventStatus = (
    event.event_status || "UPCOMING"
  ).toUpperCase();

  const statusLabels = {
    UPCOMING: "Upcoming",
    ONGOING: "Ongoing",
    COMPLETED: "Completed",
    CANCELLED: "Cancelled",
  };

  const statusClassNames = {
    UPCOMING: "status-upcoming",
    ONGOING: "status-ongoing",
    COMPLETED: "status-completed",
    CANCELLED: "status-cancelled",
  };

  const isCancelled = eventStatus === "CANCELLED";
  const isCompleted = eventStatus === "COMPLETED";
  const hasNoTickets = Number(event.available_tickets) <= 0;

  const bookingUnavailable =
    isCancelled || isCompleted || hasNoTickets;

  const formattedDate = event.event_date
    ? new Date(event.event_date).toLocaleString()
    : "Date to be announced";

  const formattedEndDate = event.end_date
    ? new Date(event.end_date).toLocaleString()
    : null;

  const handleView = () => {
    if (typeof onView === "function") {
      onView(event.id);
    }
  };

  return (
    <article
      className={`event-card ${
        isCancelled ? "event-card-cancelled" : ""
      }`}
    >
      {event.banner_image && !imageError ? (
        <img
          src={event.banner_image}
          alt={`${event.title} banner`}
          className="event-image"
          loading="lazy"
          onError={() => setImageError(true)}
        />
      ) : (
        <div
          className="event-image-placeholder"
          role="img"
          aria-label={`${event.title} image unavailable`}
        >
          <span>SmartEvent</span>
          <small>Discover your next event</small>
        </div>
      )}

      <div className="event-card-content">
        <div className="event-card-labels">
          <span className="event-category">
            {event.category || "General"}
          </span>

          <span
            className={`event-status ${
              statusClassNames[eventStatus] || ""
            }`}
          >
            {statusLabels[eventStatus] || eventStatus}
          </span>
        </div>

        {isCancelled && (
          <div
            className="event-cancellation-notice"
            role="alert"
          >
            <strong>Event cancelled</strong>
            <p>
              This event has been cancelled. Ticket booking is
              unavailable.
            </p>
          </div>
        )}

        {!isCancelled && isCompleted && (
          <p className="event-unavailable-notice">
            This event has already been completed.
          </p>
        )}

        {!isCancelled && !isCompleted && hasNoTickets && (
          <p className="event-unavailable-notice">
            All tickets have been booked.
          </p>
        )}

        <h2 className="event-card-title">
          {event.title || "Untitled event"}
        </h2>

        <p className="event-description">
          {event.description || "No description available."}
        </p>

        <div className="event-info">
          <span>
            📍 {event.location || "Location to be announced"}
          </span>

          <span>📅 {formattedDate}</span>

          {formattedEndDate && (
            <span>🕒 Ends: {formattedEndDate}</span>
          )}

          <span>
            🎟️ {Math.max(0, Number(event.available_tickets) || 0)}{" "}
            tickets available
          </span>

          <span>
            💰 ₹{Number(event.ticket_price || 0).toLocaleString("en-IN")}
          </span>
        </div>

        <button
          type="button"
          className="event-view-button"
          onClick={handleView}
        >
          View Details
        </button>

        {bookingUnavailable && (
          <p className="event-booking-hint">
            {isCancelled
              ? "Booking is unavailable for this cancelled event."
              : isCompleted
                ? "Booking is unavailable for completed events."
                : "No tickets are currently available."}
          </p>
        )}
      </div>
    </article>
  );
}

export default EventCard;
