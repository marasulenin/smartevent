from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.booking import Booking, BookingStatus
from app.models.event import Event
from app.models.review import Review
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewUpdate, ReviewListResponse, ReviewResponse
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/reviews", tags=["Reviews"])

def to_response(review: Review):
    return ReviewResponse(id=review.id, user_id=review.user_id, event_id=review.event_id, rating=review.rating, review_text=review.review_text, created_at=review.created_at, username=review.user.username if review.user else None)

def ensure_attended(db, user_id, event_id):
    booking = db.query(Booking).filter(Booking.user_id == user_id, Booking.event_id == event_id, Booking.booking_status == BookingStatus.CONFIRMED).first()
    if not booking:
        raise HTTPException(status_code=403, detail="Only users with a confirmed booking can review this event")
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    from datetime import datetime
    event_end = event.end_date or event.event_date
    if event_end > datetime.utcnow():
        raise HTTPException(status_code=403, detail="You can review the event after it has ended")

@router.post("", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(data: ReviewCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ensure_attended(db, current_user.id, data.event_id)
    if db.query(Review).filter(Review.user_id == current_user.id, Review.event_id == data.event_id).first():
        raise HTTPException(status_code=409, detail="You have already reviewed this event")
    review = Review(user_id=current_user.id, event_id=data.event_id, rating=data.rating, review_text=data.review_text)
    db.add(review); db.commit(); db.refresh(review)
    return to_response(review)

@router.get("/event/{event_id}", response_model=ReviewListResponse)
def get_reviews(event_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    reviews = db.query(Review).filter(Review.event_id == event_id).order_by(Review.created_at.desc()).all()
    avg = db.query(func.avg(Review.rating)).filter(Review.event_id == event_id).scalar()
    return ReviewListResponse(average_rating=round(float(avg or 0), 2), review_count=len(reviews), reviews=[to_response(r) for r in reviews])

@router.put("/{review_id}", response_model=ReviewResponse)
def update_review(review_id: int, data: ReviewUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    review = db.query(Review).filter(Review.id == review_id, Review.user_id == current_user.id).first()
    if not review: raise HTTPException(status_code=404, detail="Review not found")
    for key, value in data.model_dump(exclude_unset=True).items(): setattr(review, key, value)
    db.commit(); db.refresh(review)
    return to_response(review)

@router.delete("/{review_id}")
def delete_review(review_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    review = db.query(Review).filter(Review.id == review_id, Review.user_id == current_user.id).first()
    if not review: raise HTTPException(status_code=404, detail="Review not found")
    db.delete(review); db.commit()
    return {"message": "Review deleted successfully"}
