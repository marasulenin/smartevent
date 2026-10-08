
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.event import Event
from app.models.user import User
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


# ============================================================
# CREATE EVENT
# ORGANIZER + ADMIN
# ============================================================

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
    """
    Create a new event.

    ORGANIZER:
        Event is automatically assigned to the logged-in organizer.

    ADMIN:
        Admin can also create events.
    """

    event = Event(
        title=event_data.title,
        description=event_data.description,
        category=event_data.category,
        location=event_data.location,
        event_date=event_data.event_date,
        ticket_price=event_data.ticket_price,
        available_tickets=event_data.available_tickets,
        banner_image=event_data.banner_image,
        organizer_id=current_user.id,
        event_status="ACTIVE",
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return event


# ============================================================
# LIST EVENTS
# ALL AUTHENTICATED USERS
# ============================================================

@router.get(
    "",
    response_model=list[EventResponse],
)
def get_events(
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    event_status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get events with search, category, status and pagination.

    USER:
        Can view events.

    ORGANIZER:
        Can view events.

    ADMIN:
        Can view events.
    """

    query = db.query(Event)

    if search:
        search_pattern = f"%{search}%"

        query = query.filter(
            or_(
                Event.title.ilike(search_pattern),
                Event.description.ilike(search_pattern),
                Event.location.ilike(search_pattern),
            )
        )

    if category:
        query = query.filter(
            Event.category == category
        )

    if event_status:
        query = query.filter(
            Event.event_status == event_status
        )

    events = (
        query
        .order_by(Event.event_date.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return events


# ============================================================
# GET SINGLE EVENT
# ALL AUTHENTICATED USERS
# ============================================================

@router.get(
    "/{event_id}",
    response_model=EventResponse,
)
def get_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get a single event.

    USER:
        Can view event.

    ORGANIZER:
        Can view event.

    ADMIN:
        Can view event.
    """

    event = (
        db.query(Event)
        .filter(Event.id == event_id)
        .first()
    )

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    return event


# ============================================================
# UPDATE EVENT
# ORGANIZER -> OWN EVENTS
# ADMIN -> ANY EVENT
# ============================================================

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
    """
    Update an event.

    ORGANIZER:
        Can update only their own event.

    ADMIN:
        Can update any event.
    """

    event = (
        db.query(Event)
        .filter(Event.id == event_id)
        .first()
    )

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    # --------------------------------------------------------
    # Organizer ownership validation
    # --------------------------------------------------------

    if (
        current_user.role == "ORGANIZER"
        and event.organizer_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own events",
        )

    # --------------------------------------------------------
    # Update only provided fields
    # --------------------------------------------------------

    update_data = event_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(event, field, value)

    db.commit()
    db.refresh(event)

    return event


# ============================================================
# CANCEL EVENT
# ORGANIZER -> OWN EVENTS
# ADMIN -> ANY EVENT
# ============================================================

@router.patch(
    "/{event_id}/cancel",
    response_model=EventResponse,
)
def cancel_event(
    event_id: int,
    current_user: User = Depends(require_organizer),
    db: Session = Depends(get_db),
):
    """
    Cancel an event.

    ORGANIZER:
        Can cancel only their own event.

    ADMIN:
        Can cancel any event.
    """

    event = (
        db.query(Event)
        .filter(Event.id == event_id)
        .first()
    )

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    # --------------------------------------------------------
    # Organizer ownership validation
    # --------------------------------------------------------

    if (
        current_user.role == "ORGANIZER"
        and event.organizer_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only cancel your own events",
        )

    event.event_status = "CANCELLED"

    db.commit()
    db.refresh(event)

    return event


# ============================================================
# DELETE EVENT
# ADMIN ONLY
# ============================================================

@router.delete(
    "/{event_id}",
)
def delete_event(
    event_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Delete an event.

    ADMIN only.
    """

    event = (
        db.query(Event)
        .filter(Event.id == event_id)
        .first()
    )

    if not event:
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
