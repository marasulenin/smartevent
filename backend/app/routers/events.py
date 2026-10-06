from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.event import Event
from app.schemas.event import EventCreate, EventResponse, EventUpdate
from app.models.user import User
from app.utils.dependencies import get_current_user


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/api/v1/events",
    tags=["Events"],
)


# ============================================================
# CREATE EVENT
# ============================================================

@router.post(
    "",
    response_model=EventResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_event(
    event_data: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new event.
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
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return event


# ============================================================
# LIST EVENTS
# ============================================================

@router.get(
    "",
    response_model=list[EventResponse],
)
def list_events(
    category: str | None = Query(
        default=None,
        description="Filter events by category",
    ),
    search: str | None = Query(
        default=None,
        description="Search events by title",
    ),
    page: int = Query(
        default=1,
        ge=1,
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_db),
):
    """
    Get events with optional category filtering,
    title search, and pagination.
    """

    query = db.query(Event)

    # Category filter
    if category:
        query = query.filter(
            Event.category.ilike(f"%{category}%")
        )

    # Title search
    if search:
        query = query.filter(
            Event.title.ilike(f"%{search}%")
        )

    # Pagination
    offset = (page - 1) * limit

    events = (
        query
        .order_by(Event.event_date.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return events


# ============================================================
# GET EVENT DETAILS
# ============================================================

@router.get(
    "/{event_id}",
    response_model=EventResponse,
)
def get_event(
    event_id: int,
    db: Session = Depends(get_db),
):
    """
    Get details of a single event.
    """

    event = db.query(Event).filter(
        Event.id == event_id
    ).first()

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    return event


# ============================================================
# UPDATE EVENT
# ============================================================

@router.put(
    "/{event_id}",
    response_model=EventResponse,
)
def update_event(
    event_id: int,
    event_data: EventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update an existing event.
    """

    event = db.query(Event).filter(
        Event.id == event_id
    ).first()

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    update_data = event_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(event, field, value)

    db.commit()
    db.refresh(event)

    return event


# ============================================================
# DELETE EVENT
# ============================================================

@router.delete(
    "/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete an event.
    """

    event = db.query(Event).filter(
        Event.id == event_id
    ).first()

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    db.delete(event)
    db.commit()

    return None