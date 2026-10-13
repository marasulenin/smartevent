from pydantic import BaseModel


class OrganizerAnalyticsOverview(BaseModel):
    total_events: int
    total_bookings: int
    tickets_sold: int
    remaining_tickets: int
    total_revenue: float


class OrganizerEventInsight(BaseModel):
    event_id: int
    event_title: str
    event_status: str
    tickets_sold: int
    remaining_tickets: int
    booking_count: int
    revenue: float
