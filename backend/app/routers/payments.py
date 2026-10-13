import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.booking import Booking, BookingStatus
from app.models.notification import Notification, NotificationType
from app.models.payment import Payment, PaymentStatus
from app.models.user import User
from app.schemas.payment import PaymentCreate, PaymentProcess, PaymentResponse
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/payments", tags=["Payments"])

@router.post("", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment(data: PaymentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    booking = db.query(Booking).filter(Booking.id == data.booking_id, Booking.user_id == current_user.id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.booking_status == BookingStatus.CANCELLED:
        raise HTTPException(status_code=409, detail="Cancelled bookings cannot be paid")
    if booking.booking_status == BookingStatus.CONFIRMED:
        existing = db.query(Payment).filter(Payment.booking_id == booking.id, Payment.payment_status == PaymentStatus.SUCCESS).first()
        if existing:
            return existing
    payment = Payment(booking_id=booking.id, payment_method=data.payment_method, amount=booking.final_amount, payment_status=PaymentStatus.PENDING)
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment

@router.post("/{payment_id}/process", response_model=PaymentResponse)
def process_payment(payment_id: int, data: PaymentProcess, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    payment = db.query(Payment).join(Booking).filter(Payment.id == payment_id, Booking.user_id == current_user.id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    if payment.payment_status != PaymentStatus.PENDING:
        return payment
    booking = payment.booking
    if data.success:
        payment.payment_status = PaymentStatus.SUCCESS
        payment.transaction_id = f"SE-{uuid.uuid4().hex[:16].upper()}"
        booking.booking_status = BookingStatus.CONFIRMED
        db.add(Notification(user_id=current_user.id, title="Payment Successful", message=f"Payment of ₹{payment.amount:.2f} for booking #{booking.id} was successful. Transaction: {payment.transaction_id}.", type=NotificationType.PAYMENT, is_read=False))
    else:
        payment.payment_status = PaymentStatus.FAILED
        payment.transaction_id = f"FAILED-{uuid.uuid4().hex[:12].upper()}"
        booking.booking_status = BookingStatus.CANCELLED
        event = booking.event
        if event and event.event_status != "CANCELLED":
            event.available_tickets += booking.ticket_quantity
        db.add(Notification(user_id=current_user.id, title="Payment Failed", message=f"Payment for booking #{booking.id} failed. Your ticket reservation has been released.", type=NotificationType.PAYMENT, is_read=False))
    db.commit()
    db.refresh(payment)
    return payment

@router.get("/booking/{booking_id}", response_model=list[PaymentResponse])
def get_booking_payments(booking_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    booking = db.query(Booking).filter(Booking.id == booking_id, Booking.user_id == current_user.id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return db.query(Payment).filter(Payment.booking_id == booking_id).order_by(Payment.created_at.desc()).all()
