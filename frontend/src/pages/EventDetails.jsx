import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import api from "../services/api";
import LiveAvailability from "../components/LiveAvailability";

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

  const availableTickets = Math.max(
    0,
    Number(event?.available_tickets ?? 0)
  );

  const ticketPrice = Number(event?.ticket_price ?? 0);
  const totalPrice = ticketPrice * quantity;

  // Load event details.
  useEffect(() => {
    let active = true;

    async function loadEvent() {
      setLoading(true);
      setError("");

      try {
        const response = await api.get(`/events/${eventId}`);

        if (active) {
          setEvent(response.data);
          setQuantity(1);
        }
      } catch (err) {
        if (active) {
          setEvent(null);
          setError(
            err.response?.data?.detail || "Failed to load event."
          );
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    loadEvent();

    return () => {
      active = false;
    };
  }, [eventId]);

  // Keep the selected quantity within the current inventory.
  useEffect(() => {
    if (!event) return;

    setQuantity((current) => {
      if (availableTickets <= 0) return 1;

      return Math.min(
        Math.max(1, current),
        availableTickets,
        10
      );
    });
  }, [availableTickets, event]);

  const increaseQuantity = () => {
    if (
      !booking &&
      !isCancelled &&
      quantity < Math.min(availableTickets, 10)
    ) {
      setQuantity((current) => current + 1);
    }
  };

  const decreaseQuantity = () => {
    if (!booking && quantity > 1) {
      setQuantity((current) => current - 1);
    }
  };

  // Create a booking.
  const handleBooking = async () => {
    if (!event || booking) return;

    if (isCancelled) {
      setError("This event has been cancelled. Booking is unavailable.");
      return;
    }

    if (availableTickets <= 0) {
      setError("This event is sold out.");
      return;
    }

    if (quantity > availableTickets) {
      setError("Not enough tickets are available. Please try again.");
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

      setSuccess("Booking created successfully!");

      sessionStorage.setItem(
        "last_booking",
        JSON.stringify(response.data)
      );

      // Continue to the existing booking confirmation/payment flow.
      navigate(`/booking-confirmation/${response.data.id}`, {
        state: { booking: response.data },
      });
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Booking failed. Please refresh availability and try again."
      );

      // Refresh event details after a booking error.
      try {
        const response = await api.get(`/events/${eventId}`);
        setEvent(response.data);
      } catch {
        // Keep the original booking error visible.
      }
    } finally {
      setBooking(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading event...</div>;
  }

  if (!event) {
    return (
      <div className="empty-state">
        <h2>Event not found</h2>

        {error && (
          <div className="error-message" role="alert">
            {error}
          </div>
        )}

        <Link to="/" className="back-link">
          Back to Events
        </Link>
      </div>
    );
  }

  return (
    <div className="event-details-page">
      <div className="event-details-container">
        <Link to="/" className="back-link">
          &larr; Back to Events
        </Link>

        <section className="event-details">
          <header className="event-details-header">
            <h1>{event.title}</h1>

            {event.category && (
              <p className="event-category">
                Category: {event.category}
              </p>
            )}

            {event.event_status && (
              <p>
                Status:{" "}
                <strong>{event.event_status}</strong>
              </p>
            )}
          </header>

          {event.description && (
            <div className="event-description">
              <h2>About This Event</h2>
              <p>{event.description}</p>
            </div>
          )}

          <div className="event-information">
            <div>
              <strong>Location</strong>
              <span>{event.location || "Not specified"}</span>
            </div>

            <div>
              <strong>Start Date &amp; Time</strong>
              <span>
                {event.event_date
                  ? new Date(event.event_date).toLocaleString()
                  : "Not specified"}
              </span>
            </div>

            {event.end_date && (
              <div>
                <strong>End Date &amp; Time</strong>
                <span>
                  {new Date(event.end_date).toLocaleString()}
                </span>
              </div>
            )}

            <div>
              <strong>Ticket Price</strong>
              <span>
                ₹{ticketPrice.toFixed(2)}
              </span>
            </div>

            <div>
              <strong>Available Tickets</strong>
              <span>{availableTickets}</span>
            </div>
          </div>

          {/* Module 18: live availability and inventory updates */}
          <section className="live-availability-section">
            <h2>Live Ticket Availability</h2>

            <LiveAvailability
              eventId={event.id}
              onUpdate={setEvent}
            />
          </section>

          {/* Booking section */}
          <section className="booking-section">
            {isCancelled ? (
              <>
                <h2>Booking Unavailable</h2>
                <p>
                  This event has been cancelled. You cannot book
                  new tickets.
                </p>

                <Link to="/" className="back-link">
                  Browse Other Events
                </Link>
              </>
            ) : availableTickets <= 0 ? (
              <>
                <h2>Booking Unavailable</h2>
                <p className="sold-out" role="status">
                  SOLD OUT
                </p>
                <p>No tickets are currently available.</p>
              </>
            ) : (
              <>
                <h2>Book Tickets</h2>

                {error && (
                  <div className="error-message" role="alert">
                    {error}
                  </div>
                )}

                {success && (
                  <div className="success-message" role="status">
                    {success}
                  </div>
                )}

                <div className="quantity-selector">
                  <button
                    type="button"
                    onClick={decreaseQuantity}
                    disabled={quantity <= 1 || booking}
                    aria-label="Decrease ticket quantity"
                  >
                    −
                  </button>

                  <span aria-live="polite">{quantity}</span>

                  <button
                    type="button"
                    onClick={increaseQuantity}
                    disabled={
                      booking ||
                      quantity >= Math.min(availableTickets, 10)
                    }
                    aria-label="Increase ticket quantity"
                  >
                    +
                  </button>
                </div>

                <p>
                  You can book up to{" "}
                  {Math.min(availableTickets, 10)} tickets per booking.
                </p>

                <div className="booking-total">
                  <span>Total:</span>
                  <strong>₹{totalPrice.toFixed(2)}</strong>
                </div>

                <button
                  type="button"
                  className="book-button"
                  onClick={handleBooking}
                  disabled={
                    booking ||
                    isCancelled ||
                    availableTickets <= 0 ||
                    quantity > availableTickets
                  }
                >
                  {booking ? "Creating Booking..." : "Book Now"}
                </button>
              </>
            )}
          </section>
        </section>
      </div>
    </div>
  );
}

export default EventDetails;