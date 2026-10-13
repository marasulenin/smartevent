
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


# ============================================================
# EVENT BASE SCHEMA
# ============================================================

class EventBase(BaseModel):
    title: str = Field(
        ...,
        min_length=3,
        max_length=255,
    )

    description: str = Field(
        ...,
        min_length=10,
    )

    category: str = Field(
        ...,
        min_length=1,
        max_length=50,
    )

    location: str = Field(
        ...,
        min_length=2,
        max_length=255,
    )

    event_date: datetime

    end_date: datetime | None = None

    ticket_price: float = Field(
        ...,
        ge=0,
    )

    available_tickets: int = Field(
        ...,
        ge=0,
    )

    banner_image: str | None = Field(
        default=None,
        max_length=500,
    )

    @model_validator(mode="after")
    def validate_event_dates(self):
        if (
            self.end_date is not None
            and self.end_date <= self.event_date
        ):
            raise ValueError(
                "Event end date must be later than the event start date."
            )

        return self


# ============================================================
# CREATE EVENT
# ============================================================

class EventCreate(EventBase):
    pass


# ============================================================
# UPDATE EVENT
# ============================================================

class EventUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=3,
        max_length=255,
    )

    description: str | None = Field(
        default=None,
        min_length=10,
    )

    category: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )

    location: str | None = Field(
        default=None,
        min_length=2,
        max_length=255,
    )

    event_date: datetime | None = None

    end_date: datetime | None = None

    ticket_price: float | None = Field(
        default=None,
        ge=0,
    )

    available_tickets: int | None = Field(
        default=None,
        ge=0,
    )

    banner_image: str | None = Field(
        default=None,
        max_length=500,
    )

    @model_validator(mode="after")
    def validate_event_dates(self):
        if (
            self.event_date is not None
            and self.end_date is not None
            and self.end_date <= self.event_date
        ):
            raise ValueError(
                "Event end date must be later than the event start date."
            )

        return self


# ============================================================
# EVENT RESPONSE
# ============================================================

class EventResponse(EventBase):
    id: int
    organizer_id: int
    event_status: str
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )
