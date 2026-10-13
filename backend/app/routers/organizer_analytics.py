
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.booking import Booking, BookingStatus
from app.models.event import Event
from app.models.user import User
from app.schemas.organizer_analytics import (
    OrganizerAnalyticsOverview,
    OrganizerEventInsight,
)
from app.utils.dependencies import require_organizer


router = APIRouter(
    prefix="/api/v1/organizer/analytics",
    tags=["Organizer Analytics"],
)


@router.get(
    "/overview",
    response_model=OrganizerAnalyticsOverview,
)
def get_organizer_analytics_overview(
    current_user: User = Depends(require_organizer),
    db: Session = Depends(get_db),
):
    events = (
        db.query(Event)
        .filter(Event.organizer_id == current_user.id)
        .all()
    )

    total_events = len(events)

    event_ids = [event.id for event in events]

    if not event_ids:
        return OrganizerAnalyticsOverview(
            total_events=0,
            total_bookings=0,
            tickets_sold=0,
            remaining_tickets=0,
            total_revenue=0.0,
        )

    confirmed_bookings = (
        db.query(
            func.count(Booking.id),
            func.coalesce(func.sum(Booking.ticket_quantity), 0),
            func.coalesce(func.sum(Booking.total_price), 0.0),
        )
        .filter(
            Booking.event_id.in_(event_ids),
            Booking.booking_status == BookingStatus.CONFIRMED,
        )
        .first()
    )

    total_bookings = int(confirmed_bookings[0] or 0)
    tickets_sold = int(confirmed_bookings[1] or 0)
    total_revenue = float(confirmed_bookings[2] or 0.0)

    remaining_tickets = sum(
        int(event.available_tickets or 0)
        for event in events
    )

    return OrganizerAnalyticsOverview(
        total_events=total_events,
        total_bookings=total_bookings,
        tickets_sold=tickets_sold,
        remaining_tickets=remaining_tickets,
        total_revenue=total_revenue,
    )


@router.get(
    "/events",
    response_model=list[OrganizerEventInsight],
)
def get_organizer_event_insights(
    current_user: User = Depends(require_organizer),
    db: Session = Depends(get_db),
):
    events = (
        db.query(Event)
        .filter(Event.organizer_id == current_user.id)
        .order_by(Event.event_date.asc())
        .all()
    )

    insights = []

    for event in events:
        booking_stats = (
            db.query(
                func.count(Booking.id),
                func.coalesce(func.sum(Booking.ticket_quantity), 0),
                func.coalesce(func.sum(Booking.total_price), 0.0),
            )
            .filter(
                Booking.event_id == event.id,
                Booking.booking_status == BookingStatus.CONFIRMED,
            )
            .first()
        )

        booking_count = int(booking_stats[0] or 0)
        tickets_sold = int(booking_stats[1] or 0)
        revenue = float(booking_stats[2] or 0.0)

        insights.append(
            OrganizerEventInsight(
                event_id=event.id,
                event_title=event.title,
                event_status=event.event_status,
                tickets_sold=tickets_sold,
                remaining_tickets=int(
                    event.available_tickets or 0
                ),
                booking_count=booking_count,
                revenue=revenue,
            )
        )

    return insights
