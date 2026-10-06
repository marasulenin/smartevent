from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.booking import Booking, BookingStatus
from app.models.event import Event
from app.models.notification import Notification, NotificationType
from app.models.user import User
from app.schemas.booking import BookingCreate, BookingResponse
from app.utils.dependencies import get_current_user


router = APIRouter(
    prefix="/api/v1/bookings",
    tags=["Bookings"],
)


# ============================================================
# CREATE BOOKING
# ============================================================

@router.post(
    "",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_booking(
    booking_data: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = (
        db.query(Event)
        .filter(
            Event.id == booking_data.event_id
        )
        .first()
    )

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    if booking_data.ticket_quantity > event.available_tickets:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Only {event.available_tickets} tickets "
                f"are available"
            ),
        )

    total_price = (
        event.ticket_price *
        booking_data.ticket_quantity
    )

    # Reduce available tickets
    event.available_tickets -= (
        booking_data.ticket_quantity
    )

    # Create booking
    booking = Booking(
        user_id=current_user.id,
        event_id=event.id,
        ticket_quantity=booking_data.ticket_quantity,
        total_price=total_price,
        booking_status=BookingStatus.CONFIRMED,
    )

    db.add(booking)
    db.flush()

    # ========================================================
    # CREATE BOOKING NOTIFICATION
    # ========================================================

    notification = Notification(
        user_id=current_user.id,
        title="Booking Confirmed",
        message=(
            f"Your booking for '{event.title}' has been "
            f"confirmed successfully. "
            f"You booked {booking_data.ticket_quantity} ticket(s). "
            f"Total amount: ₹{total_price:.2f}."
        ),
        type=NotificationType.BOOKING,
        is_read=False,
    )

    db.add(notification)

    db.commit()
    db.refresh(booking)

    return booking


# ============================================================
# GET MY BOOKINGS
# ============================================================

@router.get(
    "",
    response_model=list[BookingResponse],
)
def get_my_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bookings = (
        db.query(Booking)
        .filter(
            Booking.user_id == current_user.id
        )
        .order_by(
            Booking.created_at.desc()
        )
        .all()
    )

    return bookings


# ============================================================
# GET SINGLE BOOKING
# ============================================================

@router.get(
    "/{booking_id}",
    response_model=BookingResponse,
)
def get_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    booking = (
        db.query(Booking)
        .filter(
            Booking.id == booking_id,
            Booking.user_id == current_user.id,
        )
        .first()
    )

    if booking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )

    return booking


# ============================================================
# CANCEL BOOKING
# ============================================================

@router.put(
    "/{booking_id}/cancel",
    response_model=BookingResponse,
)
def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    booking = (
        db.query(Booking)
        .filter(
            Booking.id == booking_id,
            Booking.user_id == current_user.id,
        )
        .first()
    )

    if booking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )

    if booking.booking_status == BookingStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking is already cancelled",
        )

    event = (
        db.query(Event)
        .filter(
            Event.id == booking.event_id
        )
        .first()
    )

    if event is not None:
        event.available_tickets += (
            booking.ticket_quantity
        )

    booking.booking_status = BookingStatus.CANCELLED

    # ========================================================
    # CREATE CANCELLATION NOTIFICATION
    # ========================================================

    event_title = (
        event.title
        if event is not None
        else "your event"
    )

    notification = Notification(
        user_id=current_user.id,
        title="Booking Cancelled",
        message=(
            f"Your booking for '{event_title}' has been "
            f"cancelled successfully. "
            f"{booking.ticket_quantity} ticket(s) "
            f"have been returned to inventory."
        ),
        type=NotificationType.BOOKING,
        is_read=False,
    )

    db.add(notification)

    db.commit()
    db.refresh(booking)

    return booking