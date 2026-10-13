
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.booking import Booking, BookingStatus
from app.models.coupon import Coupon, DiscountType
from app.models.event import Event
from app.models.notification import Notification, NotificationType
from app.models.user import User
from app.schemas.booking import BookingCreate, BookingResponse
from app.utils.dependencies import get_current_user


router = APIRouter(
    prefix="/api/v1/bookings",
    tags=["Bookings"],
)


def normalize_event_status(event):
    """Return an event status as an uppercase string."""
    value = getattr(event.event_status, "value", event.event_status)
    return str(value or "UPCOMING").upper()


def apply_coupon(db: Session, code: str | None, amount: float):
    """Validate a coupon and calculate its discount."""
    if not code:
        return None, 0.0

    coupon_code = code.strip().upper()

    coupon = (
        db.query(Coupon)
        .filter(Coupon.coupon_code == coupon_code)
        .first()
    )

    if not coupon or not coupon.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or inactive coupon",
        )

    if datetime.utcnow() > coupon.expiry_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Coupon has expired",
        )

    if amount < coupon.minimum_booking_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Minimum booking amount is "
                f"₹{coupon.minimum_booking_amount:.2f}"
            ),
        )

    used = (
        db.query(Booking)
        .filter(
            Booking.coupon_id == coupon.id,
            Booking.booking_status != BookingStatus.CANCELLED,
        )
        .count()
    )

    if used >= coupon.usage_limit:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Coupon usage limit reached",
        )

    if coupon.discount_type == DiscountType.PERCENTAGE:
        if not 0 <= coupon.discount_value <= 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid coupon percentage",
            )

        discount = amount * coupon.discount_value / 100
    else:
        if coupon.discount_value < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid coupon discount",
            )

        discount = min(coupon.discount_value, amount)

    return coupon, round(discount, 2)


@router.post(
    "",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_booking(
    data: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        # Locking may be supported by some database engines.
        # SQLite does not provide an equivalent row-level lock.
        event = (
            db.query(Event)
            .filter(Event.id == data.event_id)
            .with_for_update()
            .first()
        )

        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found",
            )

        event_status = normalize_event_status(event)

        if event_status == "CANCELLED":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "This event has been cancelled. "
                    "Booking is unavailable."
                ),
            )

        if event_status == "COMPLETED":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "This event has already been completed. "
                    "Booking is unavailable."
                ),
            )

        if data.ticket_quantity < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ticket quantity must be at least 1",
            )

        if data.ticket_quantity > event.available_tickets:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Only {event.available_tickets} "
                    "tickets are available"
                ),
            )

        total = round(
            float(event.ticket_price) * data.ticket_quantity,
            2,
        )

        coupon, discount = apply_coupon(
            db,
            data.coupon_code,
            total,
        )

        final_amount = round(total - discount, 2)

        # Reserve tickets in the same database transaction
        # as the booking.
        event.available_tickets -= data.ticket_quantity

        booking = Booking(
            user_id=current_user.id,
            event_id=event.id,
            ticket_quantity=data.ticket_quantity,
            total_price=total,
            coupon_id=coupon.id if coupon else None,
            discount_amount=discount,
            final_amount=final_amount,
            booking_status=BookingStatus.PENDING,
        )

        db.add(booking)
        db.flush()

        notification = Notification(
            user_id=current_user.id,
            title="Booking Created",
            message=(
                f"Booking #{booking.id} is ready for payment. "
                f"Amount due: ₹{final_amount:.2f}."
            ),
            type=NotificationType.BOOKING,
            is_read=False,
        )

        db.add(notification)
        db.commit()
        db.refresh(booking)

        return booking

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create booking. Please try again.",
        )


@router.get("", response_model=list[BookingResponse])
def get_my_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Booking)
        .filter(Booking.user_id == current_user.id)
        .order_by(Booking.created_at.desc())
        .all()
    )


@router.get("/{booking_id}", response_model=BookingResponse)
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

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )

    return booking


@router.put("/{booking_id}/cancel", response_model=BookingResponse)
def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        booking = (
            db.query(Booking)
            .filter(
                Booking.id == booking_id,
                Booking.user_id == current_user.id,
            )
            .with_for_update()
            .first()
        )

        if not booking:
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
            .filter(Event.id == booking.event_id)
            .with_for_update()
            .first()
        )

        if event:
            # Restore the tickets reserved by this booking.
            event.available_tickets += booking.ticket_quantity

        booking.booking_status = BookingStatus.CANCELLED

        notification = Notification(
            user_id=current_user.id,
            title="Booking Cancelled",
            message=(
                f"Your booking #{booking.id} "
                "was cancelled successfully."
            ),
            type=NotificationType.BOOKING,
            is_read=False,
        )

        db.add(notification)
        db.commit()
        db.refresh(booking)

        return booking

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel booking. Please try again.",
        )
