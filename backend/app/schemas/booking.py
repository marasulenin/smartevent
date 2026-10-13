from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.models.booking import BookingStatus

class BookingCreate(BaseModel):
    event_id: int = Field(..., gt=0)
    ticket_quantity: int = Field(..., ge=1, le=10)
    coupon_code: str | None = Field(default=None, max_length=50)

class BookingResponse(BaseModel):
    id: int
    user_id: int
    event_id: int
    ticket_quantity: int
    total_price: float
    coupon_id: int | None
    discount_amount: float
    final_amount: float
    booking_status: BookingStatus
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
