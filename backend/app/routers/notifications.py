
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.booking import Booking, BookingStatus
from app.models.event import Event
from app.models.notification import Notification, NotificationType
from app.models.user import User
from app.schemas.notification import NotificationResponse
from app.utils.dependencies import get_current_user


router = APIRouter(
    prefix="/api/v1/notifications",
    tags=["Notifications"],
)


def normalize_datetime(value: datetime) -> datetime:
    """Normalize datetimes to naive UTC for database comparisons."""
    if value.tzinfo is not None:
        return value.astimezone(timezone.utc).replace(tzinfo=None)
    return value


def create_upcoming_event_reminders(
    db: Session,
    current_user: User,
) -> None:
    """Create reminders for confirmed bookings starting within 24 hours."""
    now = datetime.utcnow()
    reminder_window = now + timedelta(hours=24)

    events = (
        db.query(Event)
        .join(Booking, Booking.event_id == Event.id)
        .filter(
            Booking.user_id == current_user.id,
            Booking.booking_status == BookingStatus.CONFIRMED,
            Event.event_status != "CANCELLED",
        )
        .distinct()
        .all()
    )

    for event in events:
        if event.event_date is None:
            continue

        event_start = normalize_datetime(event.event_date)

        if not now <= event_start <= reminder_window:
            continue

        reminder_title = "Event Reminder"
        reminder_message = (
            f"Reminder: '{event.title}' starts within the next "
            f"24 hours at {event.location}."
        )

        existing_reminder = (
            db.query(Notification)
            .filter(
                Notification.user_id == current_user.id,
                Notification.title == reminder_title,
                Notification.message == reminder_message,
            )
            .first()
        )

        if existing_reminder is None:
            db.add(
                Notification(
                    user_id=current_user.id,
                    title=reminder_title,
                    message=reminder_message,
                    type=NotificationType.EVENT,
                    is_read=False,
                )
            )

    db.commit()


@router.get(
    "",
    response_model=list[NotificationResponse],
)
def get_my_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return the current user's notification history."""
    create_upcoming_event_reminders(db, current_user)

    return (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
        .all()
    )


@router.get("/unread-count")
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return the number of unread notifications."""
    count = (
        db.query(Notification)
        .filter(
            Notification.user_id == current_user.id,
            Notification.is_read.is_(False),
        )
        .count()
    )

    return {"unread_count": count}


@router.put(
    "/{notification_id}/read",
    response_model=NotificationResponse,
)
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark one notification as read, if it belongs to the current user."""
    notification = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id,
            Notification.user_id == current_user.id,
        )
        .first()
    )

    if notification is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    notification.is_read = True
    db.commit()
    db.refresh(notification)

    return notification


@router.put("/read-all")
def mark_all_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark all notifications belonging to the current user as read."""
    updated_count = (
        db.query(Notification)
        .filter(
            Notification.user_id == current_user.id,
            Notification.is_read.is_(False),
        )
        .update(
            {Notification.is_read: True},
            synchronize_session=False,
        )
    )

    db.commit()

    return {
        "message": "All notifications marked as read",
        "updated_count": updated_count,
    }