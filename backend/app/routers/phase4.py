from datetime import datetime, timedelta
import os

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.database import get_db, SessionLocal
from app.models.event import Event
from app.models.booking import Booking, BookingStatus
from app.models.user import User
from app.models.phase4 import Wishlist, EventUpdate, EventActivity
from app.schemas.phase4 import WishlistOut, EventUpdateCreate, EventUpdateOut, ProfileUpdate, ChatRequest
from app.utils.dependencies import get_current_user, require_roles

router = APIRouter(prefix="/api/v1", tags=["Phase 4"])

@router.post('/wishlist/{event_id}', response_model=WishlistOut)
def add_wishlist(event_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event: raise HTTPException(404, 'Event not found')
    existing = db.query(Wishlist).filter_by(user_id=user.id, event_id=event_id).first()
    if existing: return existing
    item = Wishlist(user_id=user.id, event_id=event_id)
    db.add(item); db.commit(); db.refresh(item)
    return item

@router.delete('/wishlist/{event_id}')
def remove_wishlist(event_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = db.query(Wishlist).filter_by(user_id=user.id, event_id=event_id).first()
    if not item: raise HTTPException(404, 'Wishlist item not found')
    db.delete(item); db.commit()
    return {'message': 'Event removed from wishlist'}

@router.get('/wishlist')
def get_wishlist(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.query(Wishlist, Event).join(Event, Event.id == Wishlist.event_id).filter(Wishlist.user_id == user.id).order_by(Wishlist.created_at.desc()).all()
    return [{'id': w.id, 'event_id': e.id, 'created_at': w.created_at, 'event': {'id': e.id, 'title': e.title, 'category': e.category, 'location': e.location, 'event_date': e.event_date, 'ticket_price': e.ticket_price, 'available_tickets': e.available_tickets, 'banner_image': e.banner_image, 'event_status': e.event_status}} for w,e in rows]

@router.post('/events/{event_id}/updates', response_model=EventUpdateOut)
def create_event_update(event_id: int, data: EventUpdateCreate, db: Session = Depends(get_db), user: User = Depends(require_roles('ORGANIZER','ADMIN'))):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event: raise HTTPException(404, 'Event not found')
    if user.role != 'ADMIN' and event.organizer_id != user.id: raise HTTPException(403, 'You can only post updates for your own events')
    row = EventUpdate(event_id=event_id, author_id=user.id, message=data.message.strip(), is_important=data.is_important)
    db.add(row); db.commit(); db.refresh(row)
    return row

@router.get('/events/{event_id}/updates', response_model=list[EventUpdateOut])
def list_event_updates(event_id: int, db: Session = Depends(get_db)):
    if not db.query(Event.id).filter(Event.id == event_id).first(): raise HTTPException(404, 'Event not found')
    return db.query(EventUpdate).filter_by(event_id=event_id).order_by(EventUpdate.is_important.desc(), EventUpdate.created_at.desc()).limit(100).all()

@router.get('/events/{event_id}/availability')
def availability(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event: raise HTTPException(404, 'Event not found')
    return {'event_id': event.id, 'available_tickets': event.available_tickets, 'sold_out': event.available_tickets <= 0, 'event_status': event.event_status}

@router.websocket('/ws/events/{event_id}/availability')
async def availability_socket(websocket: WebSocket, event_id: int):
    # Polls the authoritative database and pushes only changes; supports SQLite and multiple API workers.
    await websocket.accept()
    last = None
    try:
        while True:
            db = SessionLocal()
            try:
                event = db.query(Event).filter(Event.id == event_id).first()
                if event is None:
                    await websocket.send_json({'error': 'Event not found'})
                    break
                current = {'event_id': event.id, 'available_tickets': event.available_tickets, 'sold_out': event.available_tickets <= 0, 'event_status': event.event_status}
            finally: db.close()
            if current != last:
                await websocket.send_json(current); last = current
            import asyncio
            await asyncio.sleep(3)
    except WebSocketDisconnect:
        pass

@router.post('/events/{event_id}/view', status_code=201)
def track_event_view(event_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not db.query(Event.id).filter(Event.id == event_id).first(): raise HTTPException(404, 'Event not found')
    db.add(EventActivity(user_id=user.id, event_id=event_id, activity_type='VIEW')); db.commit()
    return {'tracked': True}

@router.get('/recommendations')
def recommendations(limit: int = Query(8, ge=1, le=30), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    category_rows = db.query(Event.category, func.count(EventActivity.id).label('n')).join(EventActivity, EventActivity.event_id == Event.id).filter(EventActivity.user_id == user.id).group_by(Event.category).order_by(func.count(EventActivity.id).desc()).all()
    booked_categories = db.query(Event.category, func.count(Booking.id).label('n')).join(Booking, Booking.event_id == Event.id).filter(Booking.user_id == user.id, Booking.booking_status != BookingStatus.CANCELLED).group_by(Event.category).order_by(func.count(Booking.id).desc()).all()
    categories = list(dict.fromkeys([c for c,_ in booked_categories] + [c for c,_ in category_rows]))
    query = db.query(Event).filter(Event.event_status != 'CANCELLED', Event.available_tickets > 0)
    if categories: query = query.order_by((Event.category.in_(categories)).desc(), Event.event_date.asc())
    else: query = query.order_by(Event.created_at.desc())
    items = query.limit(limit).all()
    return {'recommended': [event_payload(e) for e in items], 'trending': trending(db, limit)}

def event_payload(e):
    return {'id': e.id, 'title': e.title, 'category': e.category, 'location': e.location, 'event_date': e.event_date, 'ticket_price': e.ticket_price, 'available_tickets': e.available_tickets, 'banner_image': e.banner_image, 'event_status': e.event_status}

def trending(db, limit):
    rows = db.query(Event, func.count(Booking.id).label('booking_count')).outerjoin(Booking, (Booking.event_id == Event.id) & (Booking.booking_status != BookingStatus.CANCELLED)).filter(Event.event_status != 'CANCELLED').group_by(Event.id).order_by(func.count(Booking.id).desc(), Event.created_at.desc()).limit(limit).all()
    return [{**event_payload(e), 'booking_count': n} for e,n in rows]

@router.get('/events/trending')
def get_trending(limit: int = Query(8, ge=1, le=30), db: Session = Depends(get_db)):
    return trending(db, limit)

@router.get('/discover/events')
def discover_events(search: str | None = None, category: str | None = None, location: str | None = None, min_price: float | None = Query(None, ge=0), max_price: float | None = Query(None, ge=0), start_date: datetime | None = None, end_date: datetime | None = None, sort: str = 'date', skip: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    q = db.query(Event).filter(Event.event_status != 'CANCELLED')
    if search: q = q.filter(or_(Event.title.ilike(f'%{search.strip()}%'), Event.description.ilike(f'%{search.strip()}%')))
    if category: q = q.filter(Event.category.ilike(category.strip()))
    if location: q = q.filter(Event.location.ilike(f'%{location.strip()}%'))
    if min_price is not None: q = q.filter(Event.ticket_price >= min_price)
    if max_price is not None: q = q.filter(Event.ticket_price <= max_price)
    if start_date: q = q.filter(Event.event_date >= start_date)
    if end_date: q = q.filter(Event.event_date <= end_date)
    if sort == 'price': q = q.order_by(Event.ticket_price.asc())
    elif sort == 'popularity': q = q.outerjoin(Booking, Booking.event_id == Event.id).group_by(Event.id).order_by(func.count(Booking.id).desc())
    else: q = q.order_by(Event.event_date.asc())
    return {'items': [event_payload(e) for e in q.offset(skip).limit(limit).all()], 'skip': skip, 'limit': limit}

@router.get('/profile')
def get_profile(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    bookings = db.query(Booking).filter(Booking.user_id == user.id).all()
    return {'id': user.id, 'username': user.username, 'email': user.email, 'role': user.role, 'created_at': user.created_at, 'booking_count': len(bookings), 'confirmed_bookings': sum(1 for b in bookings if str(getattr(b.booking_status,'value',b.booking_status)) == 'CONFIRMED'), 'total_spent': round(sum(float(b.final_amount or 0) for b in bookings if str(getattr(b.booking_status,'value',b.booking_status)) == 'CONFIRMED'), 2)}

@router.patch('/profile')
def update_profile(data: ProfileUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if data.username is None and data.email is None: raise HTTPException(400, 'Provide username or email to update')
    if data.username is not None:
        username = data.username.strip()
        if db.query(User).filter(User.username == username, User.id != user.id).first(): raise HTTPException(409, 'Username already in use')
        user.username = username
    if data.email is not None:
        email = str(data.email).strip().lower()
        if db.query(User).filter(User.email == email, User.id != user.id).first(): raise HTTPException(409, 'Email already in use')
        user.email = email
    db.commit(); db.refresh(user)
    return {'id': user.id, 'username': user.username, 'email': user.email, 'role': user.role}

@router.post('/chat')
def chat(data: ChatRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    text = data.message.strip(); lower = text.lower()
    if any(k in lower for k in ['my booking', 'my bookings', 'booking history', 'show bookings']):
        rows = db.query(Booking).filter(Booking.user_id == user.id).order_by(Booking.created_at.desc()).limit(10).all()
        return {'reply': f'You have {len(rows)} recent booking(s).', 'bookings': [{'id': b.id, 'event': b.event.title if b.event else None, 'quantity': b.ticket_quantity, 'status': str(getattr(b.booking_status,'value',b.booking_status)), 'amount': b.final_amount} for b in rows], 'suggestions': ['Trending events', 'Find music events']}
    if 'trending' in lower or 'popular' in lower:
        return {'reply': 'Here are some trending events on SmartEvent.', 'events': trending(db, 8), 'suggestions': ['My bookings', 'Find events near me']}
    if 'near me' in lower or 'nearby' in lower or 'location' in lower:
        return {'reply': 'Choose a city or enter a location in the event filters; I cannot access your precise location from this chat.', 'events': trending(db, 6), 'suggestions': ['Trending events', 'My bookings']}
    if 'music' in lower or 'weekend' in lower:
        q = db.query(Event).filter(Event.event_status != 'CANCELLED')
        if 'music' in lower: q = q.filter(Event.category.ilike('%music%'))
        now = datetime.utcnow()
        if 'weekend' in lower:
            end = now + timedelta(days=7); q = q.filter(Event.event_date >= now, Event.event_date <= end)
        return {'reply': 'These events may match your request.', 'events': [event_payload(e) for e in q.order_by(Event.event_date.asc()).limit(8).all()], 'suggestions': ['Trending events', 'My bookings']}
    return {'reply': 'I can help you discover events, find trending events, check your bookings, and navigate SmartEvent. Try “Suggest music events this weekend” or “Show my bookings”.', 'suggestions': ['Trending events', 'Suggest music events this weekend', 'Show my bookings']}
