
import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../services/api";

function ManageEvents() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [cancellingId, setCancellingId] = useState(null);

  const loadEvents = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const response = await api.get("/events/my-events");
      setEvents(response.data);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Unable to load your events. Please try again."
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadEvents();
  }, [loadEvents]);

  const handleCancel = async (event) => {
    const confirmed = window.confirm(
      `Are you sure you want to cancel "${event.title}"?`
    );

    if (!confirmed) return;

    setCancellingId(event.id);
    setError("");
    setMessage("");

    try {
      const response = await api.patch(
        `/events/${event.id}/cancel`
      );

      setEvents((currentEvents) =>
        currentEvents.map((item) =>
          item.id === event.id ? response.data : item
        )
      );

      setMessage(`"${event.title}" was cancelled successfully.`);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Unable to cancel this event. Please try again."
      );
    } finally {
      setCancellingId(null);
    }
  };

  const getStatus = (event) => {
    if (event.event_status === "CANCELLED") return "CANCELLED";
    if (event.event_status === "COMPLETED") return "COMPLETED";
    if (event.event_status === "ONGOING") return "ONGOING";
    if (event.event_status === "UPCOMING") return "UPCOMING";
    return event.event_status || "ACTIVE";
  };

  return (
    <section className="page-container">
      <div className="page-header">
        <div>
          <h1>Manage Events</h1>
          <p>View and manage the events you have created.</p>
        </div>

        <Link
          to="/organizer/events/create"
          className="btn btn-primary"
        >
          + Create Event
        </Link>
      </div>

      {message && (
        <div className="success-message" role="status">
          {message}
        </div>
      )}

      {error && (
        <div className="error-message" role="alert">
          {error}
        </div>
      )}

      {loading ? (
        <p>Loading your events...</p>
      ) : events.length === 0 ? (
        <div className="empty-state">
          <h2>No events yet</h2>
          <p>Create your first event to see it listed here.</p>

          <Link to="/organizer/events/create">
            Create an event
          </Link>
        </div>
      ) : (
        <div className="events-list">
          {events.map((event) => {
            const status = getStatus(event);
            const isCancelled = status === "CANCELLED";

            return (
              <article
                className="manage-event-card"
                key={event.id}
              >
                <div className="manage-event-info">
                  <div className="manage-event-heading">
                    <h2>{event.title}</h2>

                    <span
                      className={`event-status status-${status.toLowerCase()}`}
                    >
                      {status}
                    </span>
                  </div>

                  <p>{event.description}</p>

                  <div className="manage-event-details">
                    <span>📍 {event.location}</span>
                    <span>🏷️ {event.category}</span>

                    <span>
                      📅{" "}
                      {new Date(event.event_date).toLocaleString()}
                    </span>

                    <span>
                      🎟️ {event.available_tickets} tickets available
                    </span>

                    <span>
                      💰 ₹
                      {Number(event.ticket_price).toLocaleString(
                        "en-IN"
                      )}
                    </span>
                  </div>

                  <p className="event-id">
                    Event ID: {event.id}
                  </p>
                </div>

                <div className="manage-event-actions">
                  {!isCancelled && (
                    <>
                      <Link
                        to={`/organizer/events/${event.id}/edit`}
                        className="btn btn-primary"
                      >
                        Edit Event
                      </Link>

                      <button
                        type="button"
                        className="btn btn-danger"
                        disabled={cancellingId === event.id}
                        onClick={() => handleCancel(event)}
                      >
                        {cancellingId === event.id
                          ? "Cancelling..."
                          : "Cancel Event"}
                      </button>
                    </>
                  )}
                </div>
              </article>
            );
          })}
        </div>
      )}

      <div className="page-actions">
        <Link
          to="/organizer"
          className="btn btn-secondary"
        >
          Back to Organizer Dashboard
        </Link>
      </div>
    </section>
  );
}

export default ManageEvents;
