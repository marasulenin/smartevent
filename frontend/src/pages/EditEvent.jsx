
import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import api from "../services/api";

function toDateTimeLocal(value) {
  if (!value) return "";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value.slice(0, 16);
  }

  const localDate = new Date(
    date.getTime() - date.getTimezoneOffset() * 60000
  );

  return localDate.toISOString().slice(0, 16);
}

function EditEvent() {
  const { eventId } = useParams();
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    title: "",
    description: "",
    category: "",
    location: "",
    event_date: "",
    end_date: "",
    ticket_price: "",
    available_tickets: "",
    banner_image: "",
  });

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    let active = true;

    async function fetchEvent() {
      try {
        const response = await api.get(`/events/${eventId}`);

        if (!active) return;

        const event = response.data;

        setFormData({
          title: event.title ?? "",
          description: event.description ?? "",
          category: event.category ?? "",
          location: event.location ?? "",
          event_date: toDateTimeLocal(event.event_date),
          end_date: toDateTimeLocal(event.end_date),
          ticket_price: String(event.ticket_price ?? ""),
          available_tickets: String(event.available_tickets ?? ""),
          banner_image: event.banner_image ?? "",
        });
      } catch (err) {
        if (active) {
          setError(
            err.response?.data?.detail ||
              "Unable to load the event. Please try again."
          );
        }
      } finally {
        if (active) setLoading(false);
      }
    }

    fetchEvent();

    return () => {
      active = false;
    };
  }, [eventId]);

  function handleChange(event) {
    const { name, value } = event.target;

    setFormData((current) => ({
      ...current,
      [name]: value,
    }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setSuccess("");

    if (
      formData.end_date &&
      new Date(formData.end_date) <= new Date(formData.event_date)
    ) {
      setError("Event end date and time must be after the start date and time.");
      return;
    }

    setSaving(true);

    try {
      const payload = {
        ...formData,
        event_date: new Date(formData.event_date).toISOString(),
        end_date: formData.end_date
          ? new Date(formData.end_date).toISOString()
          : null,
        ticket_price: Number(formData.ticket_price),
        available_tickets: Number(formData.available_tickets),
        banner_image: formData.banner_image.trim() || null,
      };

      await api.put(`/events/${eventId}`, payload);

      setSuccess("Event updated successfully!");
      navigate("/organizer/events");
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Unable to update the event. Please check your details."
      );
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <section className="page-container">
        <p>Loading event details...</p>
      </section>
    );
  }

  return (
    <section className="page-container">
      <div className="page-header">
        <div>
          <h1>Edit Event</h1>
          <p>Update the details of your event.</p>
        </div>
      </div>

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

      <form onSubmit={handleSubmit} className="event-form">
        <div className="form-group">
          <label htmlFor="title">Event Title</label>
          <input
            id="title"
            name="title"
            value={formData.title}
            onChange={handleChange}
            minLength={3}
            maxLength={255}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="description">Description</label>
          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleChange}
            minLength={10}
            rows={4}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="category">Category</label>
          <input
            id="category"
            name="category"
            value={formData.category}
            onChange={handleChange}
            maxLength={50}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="location">Location</label>
          <input
            id="location"
            name="location"
            value={formData.location}
            onChange={handleChange}
            maxLength={255}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="event_date">Event Start Date and Time</label>
          <input
            id="event_date"
            name="event_date"
            type="datetime-local"
            value={formData.event_date}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="end_date">
            Event End Date and Time (Optional)
          </label>
          <input
            id="end_date"
            name="end_date"
            type="datetime-local"
            value={formData.end_date}
            min={formData.event_date || undefined}
            onChange={handleChange}
          />
          <small>
            If left blank, the backend uses a default two-hour duration.
          </small>
        </div>

        <div className="form-group">
          <label htmlFor="ticket_price">Ticket Price (₹)</label>
          <input
            id="ticket_price"
            name="ticket_price"
            type="number"
            min="0"
            step="0.01"
            value={formData.ticket_price}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="available_tickets">Available Tickets</label>
          <input
            id="available_tickets"
            name="available_tickets"
            type="number"
            min="0"
            step="1"
            value={formData.available_tickets}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="banner_image">
            Banner Image URL (Optional)
          </label>
          <input
            id="banner_image"
            name="banner_image"
            type="url"
            value={formData.banner_image}
            onChange={handleChange}
          />
        </div>

        <div className="page-actions">
          <button
            type="submit"
            className="btn btn-primary"
            disabled={saving}
          >
            {saving ? "Saving Changes..." : "Save Changes"}
          </button>

          <Link to="/organizer/events" className="btn btn-secondary">
            Back to Manage Events
          </Link>
        </div>
      </form>
    </section>
  );
}

export default EditEvent;