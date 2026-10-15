
import {
  BrowserRouter,
  Navigate,
  Route,
  Routes,
} from "react-router-dom";

import { useAuth } from "./context/AuthContext";

import Login from "./pages/Login";
import Register from "./pages/Register";
import Home from "./pages/Home";
import EventDetails from "./pages/EventDetails";
import BookingConfirmation from "./pages/BookingConfirmation";
import BookingHistory from "./pages/BookingHistory";
import Tickets from "./pages/Tickets";
import Notifications from "./pages/Notifications";

import OrganizerDashboard from "./pages/OrganizerDashboard";
import CreateEvent from "./pages/CreateEvent";
import ManageEvents from "./pages/ManageEvents";
import EditEvent from "./pages/EditEvent";
import EventBookings from "./pages/EventBookings";
import OrganizerAnalytics from "./pages/OrganizerAnalytics";

import Phase4Hub from "./pages/Phase4Hub";

import Navbar from "./components/Navbar";

function ProtectedLayout({ children }) {
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return (
    <>
      <Navbar />
      <main className="page-content">{children}</main>
    </>
  );
}

function OrganizerRoute({ children }) {
  const { isAuthenticated, user } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (
    user?.role !== "ORGANIZER" &&
    user?.role !== "ADMIN"
  ) {
    return <Navigate to="/" replace />;
  }

  return (
    <>
      <Navbar />
      <main className="page-content">{children}</main>
    </>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* User routes */}
        <Route
          path="/"
          element={
            <ProtectedLayout>
              <Home />
            </ProtectedLayout>
          }
        />

        <Route
          path="/events/:eventId"
          element={
            <ProtectedLayout>
              <EventDetails />
            </ProtectedLayout>
          }
        />

        <Route
          path="/booking-confirmation/:bookingId"
          element={
            <ProtectedLayout>
              <BookingConfirmation />
            </ProtectedLayout>
          }
        />

        <Route
          path="/bookings"
          element={
            <ProtectedLayout>
              <BookingHistory />
            </ProtectedLayout>
          }
        />

        <Route
          path="/tickets"
          element={
            <ProtectedLayout>
              <Tickets />
            </ProtectedLayout>
          }
        />

        <Route
          path="/notifications"
          element={
            <ProtectedLayout>
              <Notifications />
            </ProtectedLayout>
          }
        />

        {/* Phase 4 */}
        <Route
          path="/phase4"
          element={
            <ProtectedLayout>
              <Phase4Hub />
            </ProtectedLayout>
          }
        />

        {/* Organizer routes */}
        <Route
          path="/organizer"
          element={
            <OrganizerRoute>
              <OrganizerDashboard />
            </OrganizerRoute>
          }
        />

        <Route
          path="/organizer/events/create"
          element={
            <OrganizerRoute>
              <CreateEvent />
            </OrganizerRoute>
          }
        />

        <Route
          path="/organizer/events"
          element={
            <OrganizerRoute>
              <ManageEvents />
            </OrganizerRoute>
          }
        />

        <Route
          path="/organizer/events/:eventId/edit"
          element={
            <OrganizerRoute>
              <EditEvent />
            </OrganizerRoute>
          }
        />

        <Route
          path="/organizer/bookings"
          element={
            <OrganizerRoute>
              <EventBookings />
            </OrganizerRoute>
          }
        />

        <Route
          path="/organizer/analytics"
          element={
            <OrganizerRoute>
              <OrganizerAnalytics />
            </OrganizerRoute>
          }
        />

        {/* Fallback */}
        <Route
          path="*"
          element={<Navigate to="/" replace />}
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
