
import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../services/api";

function EventBookings() {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadBookings = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const response = await api.get("/events/my-events/bookings");
      setBookings(response.data);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Unable to load event bookings. Please try again."
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadBookings();
  }, [loadBookings]);

  const formatDate = (dateValue) => {
    if (!dateValue) return "N/A";

    return new Date(dateValue).toLocaleString();
  };

  const getStatus = (booking) => {
    return booking.status || booking.booking_status || "CONFIRMED";
  };

  const getUserName = (booking) => {
    if (booking.user?.username) {
      return booking.user.username;
    }

    if (booking.username) {
      return booking.username;
    }

    if (booking.user?.email) {
      return booking.user.email;
    }

    return "User";
  };

  return (
    <section className="page-container">
      <div className="page-header">
        <div>
          <h1>Event Bookings</h1>
          <p>View bookings made for your events.</p>
        </div>
      </div>

      {error && (
        <div className="error-message" role="alert">
          {error}
        </div>
      )}

      {loading ? (
        <p>Loading bookings...</p>
      ) : bookings.length === 0 ? (
        <div className="empty-state">
          <h2>No bookings yet</h2>
          <p>
            Bookings for your events will appear here once users
            purchase tickets.
          </p>

          <Link to="/organizer/events" className="btn btn-secondary">
            Back to Manage Events
          </Link>
        </div>
      ) : (
        <>
          <div className="bookings-summary">
            <h2>Total Bookings: {bookings.length}</h2>
          </div>

          <div className="bookings-list">
            {bookings.map((booking) => {
              const status = getStatus(booking);

              return (
                <article
                  className="booking-card"
                  key={booking.id}
                >
                  <div className="booking-card-header">
                    <div>
                      <h2>
                        Booking #{booking.id}
                      </h2>

                      <p>
                        Event ID: {booking.event_id ?? "N/A"}
                      </p>
                    </div>

                    <span
                      className={`booking-status status-${String(
                        status
                      ).toLowerCase()}`}
                    >
                      {status}
                    </span>
                  </div>

                  <div className="booking-details">
                    <div>
                      <strong>Customer</strong>
                      <span>{getUserName(booking)}</span>
                    </div>

                    <div>
                      <strong>Tickets</strong>
                      <span>
                        {booking.quantity ??
                          booking.ticket_quantity ??
                          0}
                      </span>
                    </div>

                    <div>
                      <strong>Total Amount</strong>
                      <span>
                        ₹
                        {Number(
                          booking.total_amount ??
                            booking.total_price ??
                            0
                        ).toLocaleString("en-IN")}
                      </span>
                    </div>

                    <div>
                      <strong>Booking Date</strong>
                      <span>
                        {formatDate(
                          booking.created_at ??
                            booking.booking_date
                        )}
                      </span>
                    </div>
                  </div>
                </article>
              );
            })}
          </div>
        </>
      )}

      <div className="page-actions">
        <Link to="/organizer" className="btn btn-secondary">
          Back to Organizer Dashboard
        </Link>
      </div>
    </section>
  );
}

export default EventBookings;
