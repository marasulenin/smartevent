from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.models.payment import PaymentMethod, PaymentStatus

class PaymentCreate(BaseModel):
    booking_id: int = Field(..., gt=0)
    payment_method: PaymentMethod = PaymentMethod.SIMULATION

class PaymentProcess(BaseModel):
    success: bool = True

class PaymentResponse(BaseModel):
    id: int
    booking_id: int
    payment_method: PaymentMethod
    payment_status: PaymentStatus
    transaction_id: str | None
    amount: float
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
