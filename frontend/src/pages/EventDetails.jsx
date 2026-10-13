
import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import api from "../services/api";

function EventDetails() {
  const { eventId } = useParams();
  const navigate = useNavigate();

  const [event, setEvent] = useState(null);
  const [quantity, setQuantity] = useState(1);

  const [loading, setLoading] = useState(true);
  const [booking, setBooking] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const isCancelled =
    event?.event_status?.toUpperCase() === "CANCELLED";

  // ============================================================
  // LOAD EVENT
  // ============================================================

  const loadEvent = async () => {
    setLoading(true);
    setError("");

    try {
      const response = await api.get(`/events/${eventId}`);
      setEvent(response.data);
      setQuantity(1);
    } catch (error) {
      setEvent(null);
      setError(
        error.response?.data?.detail || "Failed to load event"
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadEvent();
  }, [eventId]);

  // ============================================================
  // QUANTITY
  // ============================================================

  const increaseQuantity = () => {
    if (
      event &&
      !isCancelled &&
      quantity < Math.min(event.available_tickets, 10)
    ) {
      setQuantity((current) => current + 1);
    }
  };

  const decreaseQuantity = () => {
    if (quantity > 1) {
      setQuantity((current) => current - 1);
    }
  };

  // ============================================================
  // BOOK EVENT
  // ============================================================

  const handleBooking = async () => {
    if (!event) {
      return;
    }

    // Never allow booking a cancelled event.
    if (event.event_status?.toUpperCase() === "CANCELLED") {
      setError("This event has been cancelled. Booking is unavailable.");
      return;
    }

    if (event.available_tickets <= 0) {
      setError("This event is sold out.");
      return;
    }

    if (quantity > event.available_tickets) {
      setError("Not enough tickets available.");
      return;
    }

    setBooking(true);
    setError("");
    setSuccess("");

    try {
      const response = await api.post("/bookings", {
        event_id: event.id,
        ticket_quantity: quantity,
      });

      setSuccess("Booking confirmed successfully!");

      sessionStorage.setItem(
        "last_booking",
        JSON.stringify(response.data)
      );

      setTimeout(() => {
        navigate(`/booking-confirmation/${response.data.id}`);
      }, 800);
    } catch (error) {
      setError(
        error.response?.data?.detail || "Booking failed"
      );
    } finally {
      setBooking(false);
    }
  };

  // ============================================================
  // LOADING
  // ============================================================

  if (loading) {
    return <div className="loading">Loading event...</div>;
  }

  // ============================================================
  // EVENT NOT FOUND
  // ============================================================

  if (!event) {
    return (
      <div className="empty-state">
        <h2>Event not found</h2>

        {error && (
          <div className="error-message">{error}</div>
        )}

        <Link to="/">← Back to Events</Link>
      </div>
    );
  }

  const totalPrice = event.ticket_price * quantity;

  // ============================================================
  // PAGE
  // ============================================================

  return (
    <div className="event-details-container">
      <Link to="/" className="back-link">
        ← Back to Events
      </Link>

      <div className="event-details-card">
        {event.banner_image ? (
          <img
            src={event.banner_image}
            alt={event.title}
            className="event-details-image"
          />
        ) : (
          <div className="event-details-placeholder">
            SmartEvent
          </div>
        )}

        <div className="event-details-content">
          <span className="event-category">
            {event.category}
          </span>

          <div className="event-status">
            <strong
              className={
                isCancelled
                  ? "cancelled-status"
                  : "upcoming-status"
              }
            >
              {event.event_status || "UPCOMING"}
            </strong>
          </div>

          <h1>{event.title}</h1>

          <p className="event-description">
            {event.description}
          </p>

          {isCancelled && (
            <div className="error-message" role="alert">
              <strong>This event has been cancelled.</strong>
              <p>
                Booking is unavailable for this event.
                Please return to the events list to discover
                other events.
              </p>
            </div>
          )}

          <div className="event-details-info">
            <div>
              <strong>📍 Location</strong>
              <span>{event.location}</span>
            </div>

            <div>
              <strong>📅 Start Date &amp; Time</strong>
              <span>
                {new Date(event.event_date).toLocaleString()}
              </span>
            </div>

            {event.end_date && (
              <div>
                <strong>🕒 End Date &amp; Time</strong>
                <span>
                  {new Date(event.end_date).toLocaleString()}
                </span>
              </div>
            )}

            <div>
              <strong>🎟️ Available Tickets</strong>
              <span>{event.available_tickets}</span>
            </div>

            <div>
              <strong>💰 Ticket Price</strong>
              <span>₹{event.ticket_price}</span>
            </div>
          </div>

          {/* BOOKING */}

          {isCancelled ? (
            <div className="booking-section">
              <h2>Booking Unavailable</h2>
              <p>
                This event has been cancelled. You cannot book
                new tickets.
              </p>
              <Link to="/" className="back-link">
                Browse Other Events
              </Link>
            </div>
          ) : (
            <div className="booking-section">
              <h2>Book Tickets</h2>

              {error && (
                <div className="error-message" role="alert">
                  {error}
                </div>
              )}

              {success && (
                <div
                  className="success-message"
                  role="status"
                >
                  {success}
                </div>
              )}

              {event.available_tickets <= 0 ? (
                <div className="sold-out">SOLD OUT</div>
              ) : (
                <>
                  <div className="quantity-selector">
                    <button
                      type="button"
                      onClick={decreaseQuantity}
                      disabled={quantity === 1 || booking}
                    >
                      −
                    </button>

                    <span>{quantity}</span>

                    <button
                      type="button"
                      onClick={increaseQuantity}
                      disabled={
                        booking ||
                        quantity >=
                          Math.min(event.available_tickets, 10)
                      }
                    >
                      +
                    </button>
                  </div>

                  <div className="booking-total">
                    <span>Total:</span>
                    <strong>₹{totalPrice.toFixed(2)}</strong>
                  </div>

                  <button
                    type="button"
                    className="book-button"
                    onClick={handleBooking}
                    disabled={booking || isCancelled}
                  >
                    {booking ? "Booking..." : "Book Now"}
                  </button>
                </>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default EventDetails;