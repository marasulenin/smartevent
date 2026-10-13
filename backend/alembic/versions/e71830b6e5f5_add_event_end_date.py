
"""add event end date

Revision ID: e71830b6e5f5
Revises: 3131459875e1
Create Date: 2026-10-09 15:06:44.553339
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# Revision identifiers used by Alembic.
revision: str = "e71830b6e5f5"
down_revision: Union[str, Sequence[str], None] = "3131459875e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add the event end date column."""
    op.add_column(
        "events",
        sa.Column("end_date", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    """Remove the event end date column."""
    op.drop_column("events", "end_date")
