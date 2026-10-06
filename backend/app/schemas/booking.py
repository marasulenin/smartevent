from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.booking import BookingStatus


# ============================================================
# CREATE BOOKING
# ============================================================

class BookingCreate(BaseModel):
    event_id: int = Field(
        ...,
        gt=0,
    )

    ticket_quantity: int = Field(
        ...,
        ge=1,
        le=10,
    )


# ============================================================
# BOOKING RESPONSE
# ============================================================

class BookingResponse(BaseModel):
    id: int
    user_id: int
    event_id: int
    ticket_quantity: int
    total_price: float
    booking_status: BookingStatus
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )