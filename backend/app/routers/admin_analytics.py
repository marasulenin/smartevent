from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.booking import Booking, BookingStatus
from app.models.event import Event
from app.models.payment import Payment, PaymentStatus
from app.models.user import User
from app.utils.dependencies import require_admin


router = APIRouter(
    prefix="/api/v1/admin/analytics",
    tags=["Admin Analytics"],
)


@router.get("/overview")
def get_admin_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Return platform-wide summary statistics for administrators."""

    total_users = (
        db.query(func.count(User.id))
        .filter(User.role == "USER")
        .scalar()
        or 0
    )

    total_organizers = (
        db.query(func.count(User.id))
        .filter(User.role == "ORGANIZER")
        .scalar()
        or 0
    )

    total_admins = (
        db.query(func.count(User.id))
        .filter(User.role == "ADMIN")
        .scalar()
        or 0
    )

    total_events = db.query(func.count(Event.id)).scalar() or 0

    total_bookings = db.query(func.count(Booking.id)).scalar() or 0

    successful_payments = (
        db.query(Payment)
        .filter(Payment.payment_status == PaymentStatus.SUCCESS)
        .all()
    )

    successful_revenue = round(
        sum(payment.amount for payment in successful_payments),
        2,
    )

    return {
        "users": {
            "total_users": total_users,
            "total_organizers": total_organizers,
            "total_admins": total_admins,
            "total_accounts": total_users + total_organizers + total_admins,
        },
        "events": {
            "total_events": total_events,
        },
        "bookings": {
            "total_bookings": total_bookings,
            "pending": (
                db.query(func.count(Booking.id))
                .filter(Booking.booking_status == BookingStatus.PENDING)
                .scalar()
                or 0
            ),
            "confirmed": (
                db.query(func.count(Booking.id))
                .filter(Booking.booking_status == BookingStatus.CONFIRMED)
                .scalar()
                or 0
            ),
            "cancelled": (
                db.query(func.count(Booking.id))
                .filter(Booking.booking_status == BookingStatus.CANCELLED)
                .scalar()
                or 0
            ),
        },
        "payments": {
            "successful_payment_count": len(successful_payments),
            "successful_revenue": successful_revenue,
        },
    }


@router.get("/events")
def get_admin_event_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Return event counts grouped by event status and category."""

    status_rows = (
        db.query(Event.event_status, func.count(Event.id))
        .group_by(Event.event_status)
        .all()
    )

    category_rows = (
        db.query(Event.category, func.count(Event.id))
        .group_by(Event.category)
        .all()
    )

    return {
        "total_events": db.query(func.count(Event.id)).scalar() or 0,
        "by_status": {
            str(event_status): count
            for event_status, count in status_rows
        },
        "by_category": {
            str(category): count
            for category, count in category_rows
        },
    }


@router.get("/bookings")
def get_admin_booking_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Return booking counts and ticket quantities by booking status."""

    rows = (
        db.query(
            Booking.booking_status,
            func.count(Booking.id),
            func.coalesce(func.sum(Booking.ticket_quantity), 0),
        )
        .group_by(Booking.booking_status)
        .all()
    )

    by_status = {}

    for booking_status, booking_count, ticket_count in rows:
        status_name = (
            booking_status.value
            if isinstance(booking_status, BookingStatus)
            else str(booking_status)
        )

        by_status[status_name] = {
            "booking_count": booking_count,
            "ticket_quantity": int(ticket_count),
        }

    return {
        "total_bookings": db.query(func.count(Booking.id)).scalar() or 0,
        "by_status": by_status,
    }


@router.get("/revenue")
def get_admin_revenue_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Return payment totals grouped by payment status."""

    rows = (
        db.query(
            Payment.payment_status,
            func.count(Payment.id),
            func.coalesce(func.sum(Payment.amount), 0.0),
        )
        .group_by(Payment.payment_status)
        .all()
    )

    by_status = {}

    for payment_status, payment_count, amount in rows:
        status_name = (
            payment_status.value
            if isinstance(payment_status, PaymentStatus)
            else str(payment_status)
        )

        by_status[status_name] = {
            "payment_count": payment_count,
            "amount": round(float(amount), 2),
        }

    successful_revenue = (
        db.query(func.coalesce(func.sum(Payment.amount), 0.0))
        .filter(Payment.payment_status == PaymentStatus.SUCCESS)
        .scalar()
        or 0.0
    )

    return {
        "successful_revenue": round(float(successful_revenue), 2),
        "by_status": by_status,
    }