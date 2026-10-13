
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.booking import Booking, BookingStatus
from app.models.event import Event
from app.models.notification import Notification, NotificationType
from app.models.user import User
from app.schemas.booking import BookingResponse
from app.schemas.event import EventCreate, EventResponse, EventUpdate
from app.utils.dependencies import (
    get_current_user,
    require_admin,
    require_organizer,
)

router = APIRouter(
    prefix="/api/v1/events",
    tags=["Events"],
)

DEFAULT_EVENT_DURATION = timedelta(hours=2)

NOTIFIABLE_FIELDS = {
    "title",
    "description",
    "category",
    "location",
    "event_date",
    "end_date",
    "ticket_price",
    "banner_image",
}


def normalize_datetime(value: datetime) -> datetime:
    """Use naive UTC datetimes for comparison with existing database values."""
    if value.tzinfo is not None:
        return value.astimezone(timezone.utc).replace(tzinfo=None)
    return value


def get_event_end(event: Event) -> datetime:
    """Use an explicit end time or assume a two-hour event."""
    start = normalize_datetime(event.event_date)

    if event.end_date is not None:
        return normalize_datetime(event.end_date)

    return start + DEFAULT_EVENT_DURATION


def update_event_status(event: Event) -> None:
    """Calculate status from the event's start and end times."""
    if event.event_status == "CANCELLED":
        return

    now = datetime.utcnow()
    start = normalize_datetime(event.event_date)
    end = get_event_end(event)

    if now < start:
        event.event_status = "UPCOMING"
    elif now < end:
        event.event_status = "ONGOING"
    else:
        event.event_status = "COMPLETED"


def update_events_status(
    events: list[Event],
    db: Session,
) -> list[Event]:
    """Persist automatic status changes."""
    changed = False

    for event in events:
        old_status = event.event_status
        update_event_status(event)

        if old_status != event.event_status:
            changed = True

    if changed:
        db.commit()
        for event in events:
            db.refresh(event)

    return events


def get_active_booking_user_ids(
    event_id: int,
    db: Session,
) -> set[int]:
    """Return unique users with pending or confirmed bookings."""
    bookings = (
        db.query(Booking)
        .filter(
            Booking.event_id == event_id,
            Booking.booking_status.in_(
                [BookingStatus.PENDING, BookingStatus.CONFIRMED]
            ),
        )
        .all()
    )

    return {booking.user_id for booking in bookings}


def notify_event_users(
    event: Event,
    db: Session,
    title: str,
    message: str,
) -> None:
    """Create one event notification per user with an active booking."""
    user_ids = get_active_booking_user_ids(event.id, db)

    for user_id in user_ids:
        db.add(
            Notification(
                user_id=user_id,
                title=title,
                message=message,
                type=NotificationType.EVENT,
                is_read=False,
            )
        )


def ensure_valid_dates(
    event_start: datetime,
    event_end: datetime | None,
) -> None:
    if event_end is not None:
        start = normalize_datetime(event_start)
        end = normalize_datetime(event_end)

        if end <= start:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Event end date must be after its start date",
            )


@router.post(
    "",
    response_model=EventResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_event(
    event_data: EventCreate,
    current_user: User = Depends(require_organizer),
    db: Session = Depends(get_db),
):
    ensure_valid_dates(event_data.event_date, event_data.end_date)

    event = Event(
        title=event_data.title,
        description=event_data.description,
        category=event_data.category,
        location=event_data.location,
        event_date=event_data.event_date,
        end_date=event_data.end_date,
        ticket_price=event_data.ticket_price,
        available_tickets=event_data.available_tickets,
        banner_image=event_data.banner_image,
        organizer_id=current_user.id,
        event_status="UPCOMING",
    )

    update_event_status(event)

    db.add(event)
    db.commit()
    db.refresh(event)

    return event


@router.get(
    "/my-events",
    response_model=list[EventResponse],
)
def get_my_events(
    current_user: User = Depends(require_organizer),
    db: Session = Depends(get_db),
):
    events = (
        db.query(Event)
        .filter(Event.organizer_id == current_user.id)
        .order_by(Event.created_at.desc())
        .all()
    )

    return update_events_status(events, db)


@router.get(
    "/my-events/bookings",
    response_model=list[BookingResponse],
)
def get_my_event_bookings(
    current_user: User = Depends(require_organizer),
    db: Session = Depends(get_db),
):
    bookings = (
        db.query(Booking)
        .join(Event, Booking.event_id == Event.id)
        .filter(Event.organizer_id == current_user.id)
        .order_by(Booking.created_at.desc())
        .all()
    )

    return bookings


@router.get(
    "",
    response_model=list[EventResponse],
)
def get_events(
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    sort: str = Query("date"),
    event_status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Event)

    if search:
        pattern = f"%{search}%"
        query = query.filter(
            or_(
                Event.title.ilike(pattern),
                Event.description.ilike(pattern),
                Event.location.ilike(pattern),
            )
        )

    if category:
        query = query.filter(Event.category == category)

    if location:
        query = query.filter(Event.location.ilike(f"%{location}%"))

    if date_from:
        query = query.filter(Event.event_date >= normalize_datetime(date_from))

    if date_to:
        query = query.filter(Event.event_date <= normalize_datetime(date_to))

    sort_key = sort.lower()
    if sort_key == "price":
        query = query.order_by(Event.ticket_price.asc())
    elif sort_key == "popularity":
        query = query.outerjoin(Booking, Booking.event_id == Event.id).group_by(Event.id).order_by(func.count(Booking.id).desc())
    else:
        query = query.order_by(Event.event_date.asc())

    events = query.all()

    events = update_events_status(events, db)

    if event_status:
        requested_status = event_status.upper()
        events = [
            event for event in events
            if event.event_status == requested_status
        ]

    return events[skip:skip + limit]


@router.get(
    "/{event_id}",
    response_model=EventResponse,
)
def get_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    event = db.query(Event).filter(Event.id == event_id).first()

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    old_status = event.event_status
    update_event_status(event)

    if old_status != event.event_status:
        db.commit()
        db.refresh(event)

    return event


@router.put(
    "/{event_id}",
    response_model=EventResponse,
)
def update_event(
    event_id: int,
    event_data: EventUpdate,
    current_user: User = Depends(require_organizer),
    db: Session = Depends(get_db),
):
    event = db.query(Event).filter(Event.id == event_id).first()

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    if (
        current_user.role == "ORGANIZER"
        and event.organizer_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own events",
        )

    if event.event_status == "CANCELLED":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A cancelled event cannot be updated",
        )

    update_data = event_data.model_dump(exclude_unset=True)

    new_start = update_data.get("event_date", event.event_date)
    new_end = update_data.get("end_date", event.end_date)

    if new_start is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Event start date cannot be null",
        )

    ensure_valid_dates(new_start, new_end)

    changed_fields = {
        field
        for field, value in update_data.items()
        if field in NOTIFIABLE_FIELDS
        and getattr(event, field) != value
    }

    for field, value in update_data.items():
        if field == "event_status":
            continue
        setattr(event, field, value)

    update_event_status(event)

    if changed_fields:
        changed_names = ", ".join(sorted(changed_fields))
        notify_event_users(
            event=event,
            db=db,
            title="Event details updated",
            message=(
                f'"{event.title}" has been updated. '
                f"Changed details: {changed_names}. "
                "Please check the event page for the latest information."
            ),
        )

    db.commit()
    db.refresh(event)

    return event


@router.patch(
    "/{event_id}/cancel",
    response_model=EventResponse,
)
def cancel_event(
    event_id: int,
    current_user: User = Depends(require_organizer),
    db: Session = Depends(get_db),
):
    event = db.query(Event).filter(Event.id == event_id).first()

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    if (
        current_user.role == "ORGANIZER"
        and event.organizer_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only cancel your own events",
        )

    if event.event_status != "CANCELLED":
        event.event_status = "CANCELLED"

        notify_event_users(
            event=event,
            db=db,
            title="Event cancelled",
            message=(
                f'"{event.title}" has been cancelled by the organizer. '
                "Please check your booking details for further information."
            ),
        )

        db.commit()
        db.refresh(event)

    return event


@router.delete("/{event_id}")
def delete_event(
    event_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    event = db.query(Event).filter(Event.id == event_id).first()

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    db.delete(event)
    db.commit()

    return {
        "message": "Event deleted successfully",
        "event_id": event_id,
    }