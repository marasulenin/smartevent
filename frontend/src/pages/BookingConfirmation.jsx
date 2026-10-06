
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import api from "../services/api";

function BookingConfirmation() {
  const { bookingId } = useParams();

  const [booking, setBooking] = useState(null);
  const [event, setEvent] = useState(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadBookingDetails = async () => {
    setLoading(true);
    setError("");

    try {
      // Get booking details
      const bookingResponse = await api.get(
        `/bookings/${bookingId}`
      );

      const bookingData = bookingResponse.data;

      setBooking(bookingData);

      // Get related event details
      const eventResponse = await api.get(
        `/events/${bookingData.event_id}`
      );

      setEvent(eventResponse.data);
    } catch (error) {
      setError(
        error.response?.data?.detail ||
          "Failed to load booking details"
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadBookingDetails();
  }, [bookingId]);

  if (loading) {
    return (
      <div className="loading">
        Loading booking confirmation...
      </div>
    );
  }

  if (error) {
    return (
      <div className="empty-state">
        <h2>Unable to load booking</h2>

        <div className="error-message">
          {error}
        </div>

        <Link to="/">
          ← Back to Events
        </Link>
      </div>
    );
  }

  if (!booking) {
    return (
      <div className="empty-state">
        <h2>Booking not found</h2>

        <Link to="/">
          ← Back to Events
        </Link>
      </div>
    );
  }

  return (
    <div className="confirmation-container">
      <div className="confirmation-card">

        <div className="confirmation-icon">
          ✓
        </div>

        <h1>Booking Confirmed!</h1>

        <p className="confirmation-message">
          Your event booking has been successfully
          confirmed.
        </p>

        <div className="confirmation-status">
          <span>Status</span>

          <strong>
            {booking.booking_status}
          </strong>
        </div>

        <div className="booking-details">

          <h2>Booking Details</h2>

          <div className="booking-detail-row">
            <span>Booking ID</span>
            <strong>
              #{booking.id}
            </strong>
          </div>

          {event && (
            <>
              <div className="booking-detail-row">
                <span>Event</span>
                <strong>
                  {event.title}
                </strong>
              </div>

              <div className="booking-detail-row">
                <span>Category</span>
                <strong>
                  {event.category}
                </strong>
              </div>

              <div className="booking-detail-row">
                <span>Location</span>
                <strong>
                  {event.location}
                </strong>
              </div>

              <div className="booking-detail-row">
                <span>Date & Time</span>
                <strong>
                  {new Date(
                    event.event_date
                  ).toLocaleString()}
                </strong>
              </div>
            </>
          )}

          <div className="booking-detail-row">
            <span>Tickets</span>
            <strong>
              {booking.ticket_quantity}
            </strong>
          </div>

          <div className="booking-detail-row">
            <span>Total Amount</span>
            <strong>
              ₹{booking.total_price.toFixed(2)}
            </strong>
          </div>

          <div className="booking-detail-row">
            <span>Booked On</span>
            <strong>
              {new Date(
                booking.created_at
              ).toLocaleString()}
            </strong>
          </div>

        </div>

        <div className="confirmation-actions">
          <Link
            to="/"
            className="primary-action"
          >
            Browse More Events
          </Link>

          <Link
            to="/bookings"
            className="secondary-action"
          >
            View My Bookings
          </Link>
        </div>

      </div>
    </div>
  );
}

export default BookingConfirmation;
