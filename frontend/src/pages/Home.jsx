
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import api from "../services/api";
import EventCard from "../components/EventCard";

const PAGE_SIZE = 3;

function Home() {
  const navigate = useNavigate();

  const [events, setEvents] = useState([]);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");
  const [page, setPage] = useState(1);

  const [hasNextPage, setHasNextPage] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let isActive = true;

    const loadEvents = async () => {
      setLoading(true);
      setError("");

      try {
        const response = await api.get("/events", {
          params: {
            search: search.trim() || undefined,
            category: category || undefined,
            sort: "date",
            skip: (page - 1) * PAGE_SIZE,
            limit: PAGE_SIZE + 1,
          },
        });

        if (!isActive) return;

        const fetchedEvents = response.data;

        // Fetch one extra event to determine whether another page exists.
        setHasNextPage(fetchedEvents.length > PAGE_SIZE);
        setEvents(fetchedEvents.slice(0, PAGE_SIZE));
      } catch (err) {
        if (!isActive) return;

        setEvents([]);
        setHasNextPage(false);
        setError(
          err.response?.data?.detail || "Failed to load events"
        );
      } finally {
        if (isActive) {
          setLoading(false);
        }
      }
    };

    loadEvents();

    return () => {
      isActive = false;
    };
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
          <p>Find and book your favorite events</p>
        </div>
      </div>

      <div className="event-filters">
        <input
          type="text"
          placeholder="Search events by title..."
          value={search}
          onChange={handleSearch}
        />

        <select value={category} onChange={handleCategory}>
          <option value="">All Categories</option>
          <option value="Music">Music</option>
          <option value="Tech">Tech</option>
          <option value="Technology">Technology</option>
          <option value="Sports">Sports</option>
          <option value="Business">Business</option>
        </select>
      </div>

      {error && <div className="error-message">{error}</div>}

      {loading && <div className="loading">Loading events...</div>}

      {!loading && !error && events.length === 0 && (
        <div className="empty-state">
          <h2>No events found</h2>
          <p>Try changing your search or category.</p>
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

      <div className="pagination">
        <button
          disabled={loading || page === 1}
          onClick={() => setPage((current) => current - 1)}
        >
          ← Previous
        </button>

        <span>Page {page}</span>

        <button
          disabled={loading || !hasNextPage}
          onClick={() => setPage((current) => current + 1)}
        >
          Next →
        </button>
      </div>
    </div>
  );
}

export default Home;