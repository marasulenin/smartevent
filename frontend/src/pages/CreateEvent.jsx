import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

function CreateEvent() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    title: "",
    description: "",
    category: "",
    location: "",
    event_date: "",
    ticket_price: "",
    available_tickets: "",
    banner_image: "",
  });

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (event) => {
    setForm({
      ...form,
      [event.target.name]: event.target.value,
    });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    setError("");
    setSuccess("");
    setLoading(true);

    try {
      const payload = {
        title: form.title.trim(),
        description: form.description.trim(),
        category: form.category.trim(),
        location: form.location.trim(),
        event_date: new Date(form.event_date).toISOString(),
        ticket_price: Number(form.ticket_price),
        available_tickets: Number(form.available_tickets),
        banner_image: form.banner_image.trim() || null,
      };

      await api.post("/events", payload);

      setSuccess("Event created successfully!");

      setTimeout(() => {
        navigate("/organizer/events");
      }, 1000);
    } catch (error) {
      setError(
        error.response?.data?.detail ||
          "Failed to create event."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="form-page">
      <div className="form-card">
        <div className="form-header">
          <h1>Create Event</h1>

          <p>
            Create a new event for SmartEvent users.
          </p>
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

        <form onSubmit={handleSubmit}>
          <label htmlFor="title">
            Event Title
          </label>

          <input
            id="title"
            type="text"
            name="title"
            value={form.title}
            onChange={handleChange}
            placeholder="Enter event title"
            minLength={3}
            maxLength={255}
            required
          />

          <label htmlFor="description">
            Description
          </label>

          <textarea
            id="description"
            name="description"
            value={form.description}
            onChange={handleChange}
            placeholder="Describe your event"
            minLength={10}
            rows={5}
            required
          />

          <label htmlFor="category">
            Category
          </label>

          <input
            id="category"
            type="text"
            name="category"
            value={form.category}
            onChange={handleChange}
            placeholder="Technology, Music, Sports..."
            maxLength={50}
            required
          />

          <label htmlFor="location">
            Location
          </label>

          <input
            id="location"
            type="text"
            name="location"
            value={form.location}
            onChange={handleChange}
            placeholder="Enter event location"
            maxLength={255}
            required
          />

          <label htmlFor="event_date">
            Event Date & Time
          </label>

          <input
            id="event_date"
            type="datetime-local"
            name="event_date"
            value={form.event_date}
            onChange={handleChange}
            required
          />

          <div className="form-row">
            <div>
              <label htmlFor="ticket_price">
                Ticket Price
              </label>

              <input
                id="ticket_price"
                type="number"
                name="ticket_price"
                value={form.ticket_price}
                onChange={handleChange}
                placeholder="0"
                min="0"
                step="0.01"
                required
              />
            </div>

            <div>
              <label htmlFor="available_tickets">
                Available Tickets
              </label>

              <input
                id="available_tickets"
                type="number"
                name="available_tickets"
                value={form.available_tickets}
                onChange={handleChange}
                placeholder="100"
                min="0"
                required
              />
            </div>
          </div>

          <label htmlFor="banner_image">
            Banner Image URL
          </label>

          <input
            id="banner_image"
            type="text"
            name="banner_image"
            value={form.banner_image}
            onChange={handleChange}
            placeholder="Optional image URL"
            maxLength={500}
          />

          <div className="form-actions">
            <button
              type="button"
              className="secondary-button"
              onClick={() =>
                navigate("/organizer")
              }
              disabled={loading}
            >
              Cancel
            </button>

            <button
              type="submit"
              disabled={loading}
            >
              {loading
                ? "Creating Event..."
                : "Create Event"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default CreateEvent;