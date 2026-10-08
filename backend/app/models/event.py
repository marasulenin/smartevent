from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    location: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    event_date: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        index=True,
    )

    ticket_price: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    available_tickets: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    banner_image: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    # ========================================================
    # ORGANIZER
    # ========================================================

    organizer_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    organizer = relationship(
        "User",
        back_populates="organized_events",
    )

    # ========================================================
    # EVENT STATUS
    # ========================================================

    event_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="ACTIVE",
        server_default="ACTIVE",
        index=True,
    )

    # ========================================================
    # CREATED AT
    # ========================================================

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    # ========================================================
    # BOOKINGS
    # ========================================================

    bookings = relationship(
        "Booking",
        back_populates="event",
        cascade="all, delete-orphan",
    )