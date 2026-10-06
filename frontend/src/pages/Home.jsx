import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import api from "../services/api";
import EventCard from "../components/EventCard";


function Home() {
  const navigate = useNavigate();

  const [events, setEvents] = useState([]);

  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");

  const [page, setPage] = useState(1);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");


  const loadEvents = async () => {
    setLoading(true);
    setError("");

    try {
      const response = await api.get(
        "/events",
        {
          params: {
            search: search || undefined,
            category: category || undefined,
            page,
            limit: 6,
          },
        }
      );

      setEvents(response.data);
    } catch (error) {
      setError(
        error.response?.data?.detail ||
          "Failed to load events"
      );
    } finally {
      setLoading(false);
    }
  };


  useEffect(() => {
    loadEvents();
  }, [search, category, page]);


  const handleSearch = (event) => {
    setSearch(event.target.value);
    setPage(1);
  };


  const handleCategory = (event) => {
    setCategory(event.target.value);
    setPage(1);
  };


  const handleView = (eventId) => {
    navigate(`/events/${eventId}`);
  };


  return (
    <div className="home-container">

      <div className="home-header">
        <div>
          <h1>Discover Events</h1>

          <p>
            Find and book your favorite events
          </p>
        </div>
      </div>


      {/* =====================================================
          SEARCH & FILTER
      ===================================================== */}

      <div className="event-filters">

        <input
          type="text"
          placeholder="Search events by title..."
          value={search}
          onChange={handleSearch}
        />

        <select
          value={category}
          onChange={handleCategory}
        >
          <option value="">
            All Categories
          </option>

          <option value="Music">
            Music
          </option>

          <option value="Tech">
            Tech
          </option>

          <option value="Sports">
            Sports
          </option>

          <option value="Business">
            Business
          </option>
        </select>

      </div>


      {/* =====================================================
          ERROR
      ===================================================== */}

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}


      {/* =====================================================
          LOADING
      ===================================================== */}

      {loading && (
        <div className="loading">
          Loading events...
        </div>
      )}


      {/* =====================================================
          EVENTS
      ===================================================== */}

      {!loading && events.length === 0 && (
        <div className="empty-state">
          <h2>No events found</h2>

          <p>
            Try changing your search or category.
          </p>
        </div>
      )}


      {!loading && events.length > 0 && (
        <div className="events-grid">

          {events.map((event) => (
            <EventCard
              key={event.id}
              event={event}
              onView={handleView}
            />
          ))}

        </div>
      )}


      {/* =====================================================
          PAGINATION
      ===================================================== */}

      <div className="pagination">

        <button
          disabled={page === 1}
          onClick={() =>
            setPage((current) => current - 1)
          }
        >
          ← Previous
        </button>

        <span>
          Page {page}
        </span>

        <button
          disabled={events.length < 6}
          onClick={() =>
            setPage((current) => current + 1)
          }
        >
          Next →
        </button>

      </div>

    </div>
  );
}


export default Home;