
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import api from "../services/api";

function Tickets() {
  const [tickets, setTickets] = useState([]);
  const [bookings, setBookings] = useState([]);

  const [loading, setLoading] = useState(true);
  const [generatingId, setGeneratingId] = useState(null);

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const loadTickets = async () => {
    const response = await api.get("/tickets");
    setTickets(response.data);
  };

  const loadBookings = async () => {
    const response = await api.get("/bookings");
    setBookings(response.data);
  };

  const loadData = async () => {
    setLoading(true);
    setError("");

    try {
      await Promise.all([
        loadTickets(),
        loadBookings(),
      ]);
    } catch (error) {
      setError(
        error.response?.data?.detail ||
          "Failed to load tickets"
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const generateTicket = async (bookingId) => {
    setGeneratingId(bookingId);
    setError("");
    setSuccess("");

    try {
      await api.post(
        `/tickets/booking/${bookingId}`
      );

      setSuccess(
        `Ticket generated successfully for booking #${bookingId}.`
      );

      await loadTickets();
    } catch (error) {
      setError(
        error.response?.data?.detail ||
          "Failed to generate ticket"
      );
    } finally {
      setGeneratingId(null);
    }
  };

  const confirmedBookings = bookings.filter(
    (booking) =>
      booking.booking_status === "CONFIRMED"
  );

  const ticketBookingIds = new Set(
    tickets.map(
      (ticket) => ticket.booking_id
    )
  );

  if (loading) {
    return (
      <div className="loading">
        Loading your tickets...
      </div>
    );
  }

  return (
    <div className="tickets-container">

      <div className="tickets-header">
        <div>
          <h1>My Tickets</h1>
          <p>
            View your event tickets and QR codes
          </p>
        </div>

        <Link
          to="/bookings"
          className="back-bookings-button"
        >
          My Bookings
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

      {confirmedBookings.length > 0 && (
        <div className="ticket-generation-section">

          <h2>Generate Tickets</h2>

          <p>
            Generate a ticket for your confirmed
            bookings.
          </p>

          <div className="generation-list">

            {confirmedBookings.map(
              (booking) => (
                <div
                  className="generation-item"
                  key={booking.id}
                >

                  <div>
                    <strong>
                      Booking #{booking.id}
                    </strong>

                    <span>
                      {booking.ticket_quantity} ticket(s)
                      {" • "}
                      ₹{booking.total_price.toFixed(2)}
                    </span>
                  </div>

                  {ticketBookingIds.has(
                    booking.id
                  ) ? (
                    <span className="ticket-created">
                      ✓ Ticket Created
                    </span>
                  ) : (
                    <button
                      className="generate-ticket-button"
                      onClick={() =>
                        generateTicket(
                          booking.id
                        )
                      }
                      disabled={
                        generatingId ===
                        booking.id
                      }
                    >
                      {generatingId ===
                      booking.id
                        ? "Generating..."
                        : "Generate Ticket"}
                    </button>
                  )}

                </div>
              )
            )}

          </div>

        </div>
      )}

      {tickets.length === 0 ? (
        <div className="empty-state">

          <h2>No tickets yet</h2>

          {confirmedBookings.length === 0 ? (
            <>
              <p>
                You don't have any confirmed
                bookings.
              </p>

              <Link to="/">
                Browse Events
              </Link>
            </>
          ) : (
            <p>
              Generate a ticket above for your
              confirmed booking.
            </p>
          )}

        </div>
      ) : (
        <div className="tickets-grid">

          {tickets.map((ticket) => {

            const booking =
              bookings.find(
                (item) =>
                  item.id ===
                  ticket.booking_id
              );

            const qrUrl =
              `http://127.0.0.1:8000${ticket.qr_code_url}`;

            return (
              <div
                className="ticket-card"
                key={ticket.id}
              >

                <div className="ticket-card-header">
                  <div>
                    <span>
                      SmartEvent Ticket
                    </span>

                    <h2>
                      {ticket.ticket_code}
                    </h2>
                  </div>

                  <span className="ticket-icon">
                    🎟️
                  </span>
                </div>

                <div className="ticket-qr-section">

                  <img
                    src={qrUrl}
                    alt={`QR code for ${ticket.ticket_code}`}
                    className="ticket-qr"
                  />

                  <p>
                    Scan this QR code at the
                    event entrance.
                  </p>

                </div>

                <div className="ticket-details">

                  <div>
                    <span>Ticket Code</span>
                    <strong>
                      {ticket.ticket_code}
                    </strong>
                  </div>

                  <div>
                    <span>Booking ID</span>
                    <strong>
                      #{ticket.booking_id}
                    </strong>
                  </div>

                  {booking && (
                    <>
                      <div>
                        <span>Tickets</span>
                        <strong>
                          {booking.ticket_quantity}
                        </strong>
                      </div>

                      <div>
                        <span>Total Amount</span>
                        <strong>
                          ₹
                          {booking.total_price.toFixed(
                            2
                          )}
                        </strong>
                      </div>
                    </>
                  )}

                  <div>
                    <span>Created On</span>
                    <strong>
                      {new Date(
                        ticket.created_at
                      ).toLocaleString()}
                    </strong>
                  </div>

                </div>

                <a
                  href={qrUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="view-qr-button"
                >
                  Open QR Code
                </a>

              </div>
            );
          })}

        </div>
      )}

    </div>
  );
}

export default Tickets;
