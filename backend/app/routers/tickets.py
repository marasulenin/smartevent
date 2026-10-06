
import os
import uuid

import qrcode
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.booking import Booking, BookingStatus
from app.models.ticket import Ticket
from app.models.user import User
from app.schemas.ticket import TicketResponse
from app.utils.dependencies import get_current_user


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/api/v1/tickets",
    tags=["Tickets"],
)


# ============================================================
# QR CODE DIRECTORY
# ============================================================

QR_DIRECTORY = "static/qr_codes"

os.makedirs(
    QR_DIRECTORY,
    exist_ok=True,
)


# ============================================================
# CREATE TICKET FOR BOOKING
# ============================================================

@router.post(
    "/booking/{booking_id}",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_ticket(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # --------------------------------------------------------
    # Find user's booking
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Only confirmed bookings can have tickets
    # --------------------------------------------------------

    if booking.booking_status != BookingStatus.CONFIRMED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ticket can only be generated for a confirmed booking",
        )

    # --------------------------------------------------------
    # Prevent duplicate ticket
    # --------------------------------------------------------

    existing_ticket = db.query(Ticket).filter(
        Ticket.booking_id == booking.id
    ).first()

    if existing_ticket is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ticket already exists for this booking",
        )

    # --------------------------------------------------------
    # Generate unique ticket code
    # --------------------------------------------------------

    ticket_code = f"TKT-{uuid.uuid4().hex[:12].upper()}"

    # --------------------------------------------------------
    # QR data
    # --------------------------------------------------------

    qr_data = (
        f"SmartEvent Ticket\n"
        f"Ticket Code: {ticket_code}\n"
        f"Booking ID: {booking.id}\n"
        f"User ID: {current_user.id}\n"
        f"Event ID: {booking.event_id}\n"
        f"Quantity: {booking.ticket_quantity}\n"
        f"Total Price: {booking.total_price}"
    )

    # --------------------------------------------------------
    # Generate QR image
    # --------------------------------------------------------

    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=4,
    )

    qr.add_data(qr_data)
    qr.make(
        fit=True
    )

    qr_image = qr.make_image()

    qr_filename = f"{ticket_code}.png"

    qr_file_path = os.path.join(
        QR_DIRECTORY,
        qr_filename,
    )

    qr_image.save(
        qr_file_path
    )

    # --------------------------------------------------------
    # Store QR URL
    # --------------------------------------------------------

    qr_code_url = f"/static/qr_codes/{qr_filename}"

    # --------------------------------------------------------
    # Create ticket
    # --------------------------------------------------------

    ticket = Ticket(
        booking_id=booking.id,
        ticket_code=ticket_code,
        qr_code_url=qr_code_url,
    )

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    return ticket


# ============================================================
# GET MY TICKETS
# ============================================================

@router.get(
    "",
    response_model=list[TicketResponse],
)
def get_my_tickets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tickets = (
        db.query(Ticket)
        .join(
            Booking,
            Ticket.booking_id == Booking.id,
        )
        .filter(
            Booking.user_id == current_user.id
        )
        .order_by(
            Ticket.created_at.desc()
        )
        .all()
    )

    return tickets


# ============================================================
# GET SINGLE TICKET
# ============================================================

@router.get(
    "/{ticket_id}",
    response_model=TicketResponse,
)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ticket = (
        db.query(Ticket)
        .join(
            Booking,
            Ticket.booking_id == Booking.id,
        )
        .filter(
            Ticket.id == ticket_id,
            Booking.user_id == current_user.id,
        )
        .first()
    )

    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )

    return ticket
