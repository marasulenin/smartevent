import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import api from "../services/api";

function Notifications() {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);

  const [loading, setLoading] = useState(true);
  const [markingId, setMarkingId] = useState(null);

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const loadNotifications = async () => {
    setLoading(true);
    setError("");

    try {
      const [notificationsResponse, unreadResponse] =
        await Promise.all([
          api.get("/notifications"),
          api.get("/notifications/unread-count"),
        ]);

      setNotifications(
        notificationsResponse.data
      );

      setUnreadCount(
        unreadResponse.data.unread_count
      );
    } catch (error) {
      setError(
        error.response?.data?.detail ||
          "Failed to load notifications"
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadNotifications();
  }, []);

  const markAsRead = async (notificationId) => {
    setMarkingId(notificationId);
    setError("");
    setSuccess("");

    try {
      await api.put(
        `/notifications/${notificationId}/read`
      );

      setNotifications((current) =>
        current.map((notification) =>
          notification.id === notificationId
            ? {
                ...notification,
                is_read: true,
              }
            : notification
        )
      );

      setUnreadCount((current) =>
        current > 0 ? current - 1 : 0
      );

      setSuccess(
        "Notification marked as read."
      );
    } catch (error) {
      setError(
        error.response?.data?.detail ||
          "Failed to mark notification as read"
      );
    } finally {
      setMarkingId(null);
    }
  };

  const markAllAsRead = async () => {
    const unreadNotifications =
      notifications.filter(
        (notification) =>
          !notification.is_read
      );

    if (unreadNotifications.length === 0) {
      return;
    }

    setError("");
    setSuccess("");

    try {
      for (const notification of unreadNotifications) {
        await api.put(
          `/notifications/${notification.id}/read`
        );
      }

      setNotifications((current) =>
        current.map((notification) => ({
          ...notification,
          is_read: true,
        }))
      );

      setUnreadCount(0);

      setSuccess(
        "All notifications marked as read."
      );
    } catch (error) {
      setError(
        error.response?.data?.detail ||
          "Failed to mark all notifications as read"
      );
    }
  };

  if (loading) {
    return (
      <div className="loading">
        Loading notifications...
      </div>
    );
  }

  return (
    <div className="notifications-container">

      <div className="notifications-header">

        <div>
          <h1>Notifications</h1>

          <p>
            Stay updated with your bookings and
            SmartEvent activities.
          </p>
        </div>

        <div className="notification-summary">
          <span>
            Unread: <strong>{unreadCount}</strong>
          </span>

          <button
            type="button"
            onClick={markAllAsRead}
            disabled={unreadCount === 0}
          >
            Mark All as Read
          </button>
        </div>

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

      {notifications.length === 0 ? (
        <div className="empty-state">

          <h2>No notifications</h2>

          <p>
            You don't have any notifications yet.
          </p>

          <Link to="/">
            Browse Events
          </Link>

        </div>
      ) : (
        <div className="notifications-list">

          {notifications.map(
            (notification) => (
              <div
                key={notification.id}
                className={`notification-card ${
                  notification.is_read
                    ? "read"
                    : "unread"
                }`}
              >

                <div className="notification-icon">
                  {notification.type ===
                  "BOOKING"
                    ? "🎟️"
                    : notification.type ===
                      "EVENT"
                    ? "📅"
                    : "🔔"}
                </div>

                <div className="notification-content">

                  <div className="notification-top">

                    <div>
                      <span className="notification-type">
                        {notification.type}
                      </span>

                      <h2>
                        {notification.title}
                      </h2>
                    </div>

                    {!notification.is_read && (
                      <span className="unread-badge">
                        NEW
                      </span>
                    )}

                  </div>

                  <p>
                    {notification.message}
                  </p>

                  <div className="notification-bottom">

                    <span>
                      {new Date(
                        notification.created_at
                      ).toLocaleString()}
                    </span>

                    {!notification.is_read && (
                      <button
                        type="button"
                        onClick={() =>
                          markAsRead(
                            notification.id
                          )
                        }
                        disabled={
                          markingId ===
                          notification.id
                        }
                      >
                        {markingId ===
                        notification.id
                          ? "Updating..."
                          : "Mark as Read"}
                      </button>
                    )}

                  </div>

                </div>

              </div>
            )
          )}

        </div>
      )}

    </div>
  );
}

export default Notifications;