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
import Navbar from "./components/Navbar";


function ProtectedLayout({ children }) {
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return (
      <Navigate
        to="/login"
        replace
      />
    );
  }

  return (
    <>
      <Navbar />

      <main className="page-content">
        {children}
      </main>
    </>
  );
}


function App() {
  return (
    <BrowserRouter>

      <Routes>

        {/* LOGIN */}
        <Route
          path="/login"
          element={<Login />}
        />

        {/* REGISTER */}
        <Route
          path="/register"
          element={<Register />}
        />

        {/* HOME */}
        <Route
          path="/"
          element={
            <ProtectedLayout>
              <Home />
            </ProtectedLayout>
          }
        />

        {/* EVENT DETAILS */}
        <Route
          path="/events/:eventId"
          element={
            <ProtectedLayout>
              <EventDetails />
            </ProtectedLayout>
          }
        />

        {/* BOOKING CONFIRMATION */}
        <Route
          path="/booking-confirmation/:bookingId"
          element={
            <ProtectedLayout>
              <BookingConfirmation />
            </ProtectedLayout>
          }
        />

        {/* MY BOOKINGS */}
        <Route
          path="/bookings"
          element={
            <ProtectedLayout>
              <BookingHistory />
            </ProtectedLayout>
          }
        />

        {/* MY TICKETS */}
        <Route
          path="/tickets"
          element={
            <ProtectedLayout>
              <Tickets />
            </ProtectedLayout>
          }
        />

        {/* NOTIFICATIONS */}
        <Route
          path="/notifications"
          element={
            <ProtectedLayout>
              <Notifications />
            </ProtectedLayout>
          }
        />

        {/* UNKNOWN ROUTES */}
        <Route
          path="*"
          element={
            <Navigate
              to="/"
              replace
            />
          }
        />

      </Routes>

    </BrowserRouter>
  );
}

export default App;