import { useEffect, useState } from "react";
import api from "../services/api";

function OrganizerAnalytics() {
  const [overview, setOverview] = useState(null);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      setError("");

      const [overviewResponse, eventsResponse] = await Promise.all([
        api.get("/organizer/analytics/overview"),
        api.get("/organizer/analytics/events"),
      ]);

      setOverview(overviewResponse.data);
      setEvents(eventsResponse.data);
    } catch (err) {
      console.error(err);
      setError(
        err.response?.data?.detail ||
          "Failed to load organizer analytics."
      );
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 p-6">
        <div className="mx-auto max-w-7xl">
          <p className="text-gray-600">Loading analytics...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-100 p-6">
        <div className="mx-auto max-w-7xl">
          <div className="rounded-lg bg-red-100 p-4 text-red-700">
            {error}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="mx-auto max-w-7xl">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-800">
            Organizer Analytics
          </h1>
          <p className="mt-1 text-gray-600">
            Track your events, ticket sales, bookings and revenue.
          </p>
        </div>

        {overview && (
          <div className="mb-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
            <div className="rounded-xl bg-white p-5 shadow">
              <p className="text-sm text-gray-500">Total Events</p>
              <p className="mt-2 text-3xl font-bold text-blue-600">
                {overview.total_events}
              </p>
            </div>

            <div className="rounded-xl bg-white p-5 shadow">
              <p className="text-sm text-gray-500">Bookings</p>
              <p className="mt-2 text-3xl font-bold text-purple-600">
                {overview.total_bookings}
              </p>
            </div>

            <div className="rounded-xl bg-white p-5 shadow">
              <p className="text-sm text-gray-500">Tickets Sold</p>
              <p className="mt-2 text-3xl font-bold text-green-600">
                {overview.tickets_sold}
              </p>
            </div>

            <div className="rounded-xl bg-white p-5 shadow">
              <p className="text-sm text-gray-500">Remaining Tickets</p>
              <p className="mt-2 text-3xl font-bold text-orange-600">
                {overview.remaining_tickets}
              </p>
            </div>

            <div className="rounded-xl bg-white p-5 shadow">
              <p className="text-sm text-gray-500">Total Revenue</p>
              <p className="mt-2 text-3xl font-bold text-emerald-600">
                ?{Number(overview.total_revenue).toFixed(2)}
              </p>
            </div>
          </div>
        )}

        <div className="rounded-xl bg-white shadow">
          <div className="border-b p-5">
            <h2 className="text-xl font-semibold text-gray-800">
              Event-wise Analytics
            </h2>
          </div>

          {events.length === 0 ? (
            <div className="p-6 text-gray-600">
              No events found.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">
                      Event
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">
                      Status
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">
                      Bookings
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">
                      Tickets Sold
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">
                      Remaining
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">
                      Revenue
                    </th>
                  </tr>
                </thead>

                <tbody className="divide-y divide-gray-200">
                  {events.map((event) => (
                    <tr key={event.event_id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 font-medium text-gray-800">
                        {event.event_title}
                      </td>

                      <td className="px-6 py-4">
                        <span className="rounded-full bg-green-100 px-3 py-1 text-xs font-medium text-green-700">
                          {event.event_status}
                        </span>
                      </td>

                      <td className="px-6 py-4 text-gray-700">
                        {event.booking_count}
                      </td>

                      <td className="px-6 py-4 text-gray-700">
                        {event.tickets_sold}
                      </td>

                      <td className="px-6 py-4 text-gray-700">
                        {event.remaining_tickets}
                      </td>

                      <td className="px-6 py-4 font-medium text-emerald-600">
                        ?{Number(event.revenue).toFixed(2)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default OrganizerAnalytics;
