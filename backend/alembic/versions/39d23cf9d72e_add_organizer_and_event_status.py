"""add organizer and event status

Revision ID: 39d23cf9d72e
Revises: a1b2c3d4e5f6
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "39d23cf9d72e"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    columns = {
        column["name"]
        for column in inspector.get_columns("events")
    }

    # ---------------------------------------------------------
    # Add organizer_id only if it does not already exist
    # ---------------------------------------------------------
    if "organizer_id" not in columns:
        op.execute(
            """
            ALTER TABLE events
            ADD COLUMN organizer_id INTEGER
            """
        )

    # Give existing events an organizer.
    op.execute(
        """
        UPDATE events
        SET organizer_id = 1
        WHERE organizer_id IS NULL
        """
    )

    # ---------------------------------------------------------
    # Add event_status only if it does not already exist
    # ---------------------------------------------------------
    if "event_status" not in columns:
        op.execute(
            """
            ALTER TABLE events
            ADD COLUMN event_status VARCHAR(20)
            DEFAULT 'ACTIVE'
            """
        )

    # Give existing events an ACTIVE status.
    op.execute(
        """
        UPDATE events
        SET event_status = 'ACTIVE'
        WHERE event_status IS NULL
        """
    )

    # ---------------------------------------------------------
    # Create indexes
    # ---------------------------------------------------------
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_events_organizer_id
        ON events (organizer_id)
        """
    )

    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_events_event_status
        ON events (event_status)
        """
    )


def downgrade() -> None:
    # Development migration.
    # SQLite column removal is intentionally avoided here.
    pass