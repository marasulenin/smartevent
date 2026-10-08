
from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="USER",
        server_default="USER",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    # ========================================================
    # USER BOOKINGS
    # ========================================================

    bookings = relationship(
        "Booking",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # ========================================================
    # USER NOTIFICATIONS
    # ========================================================

    notifications = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # ========================================================
    # ORGANIZED EVENTS
    # ========================================================

    organized_events = relationship(
        "Event",
        back_populates="organizer",
        foreign_keys="Event.organizer_id",
    )
