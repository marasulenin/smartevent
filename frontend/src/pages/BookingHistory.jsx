
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import api from "../services/api";

function BookingHistory() {
  const [bookings, setBookings] = useState([]);

  const [loading, setLoading] = useState(true);
  const [cancellingId, setCancellingId] = useState(null);

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const loadBookings = async () => {
    setLoading(true);
    setError("");

    try {
      const response = await api.get("/bookings");

      setBookings(response.data);
    } catch (error) {
      setError(
        error.response?.data?.detail ||
          "Failed to load bookings"
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadBookings();
  }, []);

  const handleCancel = async (bookingId) => {
    const confirmed = window.confirm(
      "Are you sure you want to cancel this booking?"
    );

    if (!confirmed) {
      return;
    }

    setCancellingId(bookingId);
    setError("");
    setSuccess("");

    try {
      await api.put(
        `/bookings/${bookingId}/cancel`
      );

      setSuccess(
        `Booking #${bookingId} cancelled successfully.`
      );

      await loadBookings();
    } catch (error) {
      setError(
        error.response?.data?.detail ||
          "Failed to cancel booking"
      );
    } finally {
      setCancellingId(null);
    }
  };

  if (loading) {
    return (
      <div className="loading">
        Loading your bookings...
      </div>
    );
  }

  return (
    <div className="bookings-container">

      <div className="bookings-header">
        <div>
          <h1>My Bookings</h1>
          <p>
            View and manage your event bookings
          </p>
        </div>

        <Link
          to="/"
          className="browse-events-button"
        >
          Browse Events
        </Link>
      </div>

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

      {bookings.length === 0 ? (
        <div className="empty-state">
          <h2>No bookings yet</h2>

          <p>
            You haven't booked any events yet.
          </p>

          <Link to="/">
            Browse Events
          </Link>
        </div>
      ) : (
        <div className="bookings-list">

          {bookings.map((booking) => (
            <div
              className="booking-card"
              key={booking.id}
            >

              <div className="booking-card-header">

                <div>
                  <span className="booking-label">
                    Booking
                  </span>

                  <h2>
                    #{booking.id}
                  </h2>
                </div>

                <span
                  className={`booking-status ${booking.booking_status.toLowerCase()}`}
                >
                  {booking.booking_status}
                </span>

              </div>

              <div className="booking-card-details">

                <div className="booking-info-item">
                  <span>Event ID</span>
                  <strong>
                    #{booking.event_id}
                  </strong>
                </div>

                <div className="booking-info-item">
                  <span>Tickets</span>
                  <strong>
                    {booking.ticket_quantity}
                  </strong>
                </div>

                <div className="booking-info-item">
                  <span>Total Amount</span>
                  <strong>
                    ₹{booking.total_price.toFixed(2)}
                  </strong>
                </div>

                <div className="booking-info-item">
                  <span>Booked On</span>
                  <strong>
                    {new Date(
                      booking.created_at
                    ).toLocaleString()}
                  </strong>
                </div>

              </div>

              <div className="booking-card-actions">

                {booking.booking_status ===
                  "CONFIRMED" && (
                  <button
                    className="cancel-booking-button"
                    onClick={() =>
                      handleCancel(booking.id)
                    }
                    disabled={
                      cancellingId === booking.id
                    }
                  >
                    {cancellingId === booking.id
                      ? "Cancelling..."
                      : "Cancel Booking"}
                  </button>
                )}

                {booking.booking_status ===
                  "CANCELLED" && (
                  <span className="cancelled-text">
                    This booking has been cancelled.
                  </span>
                )}

              </div>

            </div>
          ))}

        </div>
      )}

    </div>
  );
}

export default BookingHistory;
