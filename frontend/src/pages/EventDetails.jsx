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


  // ============================================================
  // LOAD EVENT
  // ============================================================

  const loadEvent = async () => {
    setLoading(true);
    setError("");

    try {
      const response = await api.get(
        `/events/${eventId}`
      );

      setEvent(response.data);
    } catch (error) {
      setError(
        error.response?.data?.detail ||
          "Failed to load event"
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

    if (event.available_tickets < quantity) {
      setError(
        "Not enough tickets available."
      );
      return;
    }

    setBooking(true);
    setError("");
    setSuccess("");

    try {
      const response = await api.post(
        "/bookings",
        {
          event_id: event.id,
          ticket_quantity: quantity,
        }
      );

      setSuccess(
        "Booking confirmed successfully!"
      );

      // Store booking for confirmation page
      sessionStorage.setItem(
        "last_booking",
        JSON.stringify(response.data)
      );

      setTimeout(() => {
        navigate(
          `/booking-confirmation/${response.data.id}`
        );
      }, 800);

    } catch (error) {
      setError(
        error.response?.data?.detail ||
          "Booking failed"
      );
    } finally {
      setBooking(false);
    }
  };


  // ============================================================
  // LOADING
  // ============================================================

  if (loading) {
    return (
      <div className="loading">
        Loading event...
      </div>
    );
  }


  // ============================================================
  // ERROR / EVENT NOT FOUND
  // ============================================================

  if (!event) {
    return (
      <div className="empty-state">
        <h2>Event not found</h2>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        <Link to="/">
          ← Back to Events
        </Link>
      </div>
    );
  }


  // ============================================================
  // TOTAL PRICE
  // ============================================================

  const totalPrice =
    event.ticket_price * quantity;


  // ============================================================
  // PAGE
  // ============================================================

  return (
    <div className="event-details-container">

      <Link
        to="/"
        className="back-link"
      >
        ← Back to Events
      </Link>


      <div className="event-details-card">

        {/* ====================================================
            IMAGE
        ==================================================== */}

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


        {/* ====================================================
            DETAILS
        ==================================================== */}

        <div className="event-details-content">

          <span className="event-category">
            {event.category}
          </span>

          <h1>{event.title}</h1>

          <p className="event-description">
            {event.description}
          </p>


          <div className="event-details-info">

            <div>
              <strong>📍 Location</strong>
              <span>{event.location}</span>
            </div>

            <div>
              <strong>📅 Date & Time</strong>
              <span>
                {new Date(
                  event.event_date
                ).toLocaleString()}
              </span>
            </div>

            <div>
              <strong>🎟️ Available Tickets</strong>
              <span>
                {event.available_tickets}
              </span>
            </div>

            <div>
              <strong>💰 Ticket Price</strong>
              <span>
                ₹{event.ticket_price}
              </span>
            </div>

          </div>


          {/* ==================================================
              BOOKING
          ================================================== */}

          <div className="booking-section">

            <h2>Book Tickets</h2>

            {error && (
              <div className="error-message">
                {error}
              </div>
            )}

            {success && (
              <div className="success-message">
                {success}
              </div>
            )}


            {event.available_tickets === 0 ? (
              <div className="sold-out">
                SOLD OUT
              </div>
            ) : (
              <>
                <div className="quantity-selector">

                  <button
                    type="button"
                    onClick={decreaseQuantity}
                    disabled={quantity === 1}
                  >
                    −
                  </button>

                  <span>
                    {quantity}
                  </span>

                  <button
                    type="button"
                    onClick={increaseQuantity}
                    disabled={
                      quantity >=
                      Math.min(
                        event.available_tickets,
                        10
                      )
                    }
                  >
                    +
                  </button>

                </div>


                <div className="booking-total">
                  <span>
                    Total:
                  </span>

                  <strong>
                    ₹{totalPrice.toFixed(2)}
                  </strong>
                </div>


                <button
                  className="book-button"
                  onClick={handleBooking}
                  disabled={booking}
                >
                  {booking
                    ? "Booking..."
                    : "Book Now"}
                </button>
              </>
            )}

          </div>

        </div>

      </div>

    </div>
  );
}


export default EventDetails;