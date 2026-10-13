"""Create the event end-date index.

Revision ID: ec3e86c44f41
Revises: e71830b6e5f5
"""

from alembic import op

revision = "ec3e86c44f41"
down_revision = "e71830b6e5f5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # The preceding migration already adds events.end_date.
    # Only create its index here.
    op.create_index(
        "ix_events_end_date",
        "events",
        ["end_date"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_events_end_date", table_name="events")
