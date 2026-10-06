function EventCard({ event, onView }) {
  return (
    <div className="event-card">
      {event.banner_image ? (
        <img
          src={event.banner_image}
          alt={event.title}
          className="event-image"
        />
      ) : (
        <div className="event-image-placeholder">
          SmartEvent
        </div>
      )}

      <div className="event-card-content">
        <span className="event-category">
          {event.category}
        </span>

        <h2>{event.title}</h2>

        <p>{event.description}</p>

        <div className="event-info">
          <span>📍 {event.location}</span>

          <span>
            📅{" "}
            {new Date(
              event.event_date
            ).toLocaleString()}
          </span>

          <span>
            🎟️ {event.available_tickets} tickets
          </span>

          <span>
            💰 ₹{event.ticket_price}
          </span>
        </div>

        <button
          onClick={() => onView(event.id)}
        >
          View Details
        </button>
      </div>
    </div>
  );
}

export default EventCard;