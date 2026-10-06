
from datetime import datetime

from pydantic import BaseModel, ConfigDict


# ============================================================
# TICKET RESPONSE
# ============================================================

class TicketResponse(BaseModel):
    id: int
    booking_id: int
    ticket_code: str
    qr_code_url: str | None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )
