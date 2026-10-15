
"""add phase 4 wishlist updates activity

Revision ID: ee28a3154ac1
Revises: 1217features
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "ee28a3154ac1"
down_revision: Union[str, Sequence[str], None] = "1217features"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "event_activities",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.Column("activity_type", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["event_id"], ["events.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_event_activities_event_id",
        "event_activities",
        ["event_id"],
        unique=False,
    )
    op.create_index(
        "ix_event_activities_id",
        "event_activities",
        ["id"],
        unique=False,
    )
    op.create_index(
        "ix_event_activities_user_id",
        "event_activities",
        ["user_id"],
        unique=False,
    )

    op.create_table(
        "event_updates",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("is_important", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["author_id"], ["users.id"]
        ),
        sa.ForeignKeyConstraint(
            ["event_id"], ["events.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_event_updates_event_id",
        "event_updates",
        ["event_id"],
        unique=False,
    )
    op.create_index(
        "ix_event_updates_id",
        "event_updates",
        ["id"],
        unique=False,
    )

    op.create_table(
        "wishlists",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["event_id"], ["events.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "event_id",
            name="uq_wishlist_user_event",
        ),
    )
    op.create_index(
        "ix_wishlists_event_id",
        "wishlists",
        ["event_id"],
        unique=False,
    )
    op.create_index(
        "ix_wishlists_id",
        "wishlists",
        ["id"],
        unique=False,
    )
    op.create_index(
        "ix_wishlists_user_id",
        "wishlists",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_wishlists_user_id", table_name="wishlists")
    op.drop_index("ix_wishlists_id", table_name="wishlists")
    op.drop_index("ix_wishlists_event_id", table_name="wishlists")
    op.drop_table("wishlists")

    op.drop_index("ix_event_updates_id", table_name="event_updates")
    op.drop_index("ix_event_updates_event_id", table_name="event_updates")
    op.drop_table("event_updates")

    op.drop_index(
        "ix_event_activities_user_id",
        table_name="event_activities",
    )
    op.drop_index(
        "ix_event_activities_id",
        table_name="event_activities",
    )
    op.drop_index(
        "ix_event_activities_event_id",
        table_name="event_activities",
    )
    op.drop_table("event_activities")
