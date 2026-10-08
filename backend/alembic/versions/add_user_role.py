"""add user role

Revision ID: a1b2c3d4e5f6
Revises: 94db36db5c2f
Create Date: 2026-10-08
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# ============================================================
# REVISION IDENTIFIERS
# ============================================================

revision: str = "a1b2c3d4e5f6"

down_revision: Union[str, Sequence[str], None] = "94db36db5c2f"

branch_labels: Union[str, Sequence[str], None] = None

depends_on: Union[str, Sequence[str], None] = None


# ============================================================
# UPGRADE
# ============================================================

def upgrade() -> None:
    """
    Add role column to users table.

    Existing users will automatically receive USER.
    """

    op.add_column(
        "users",
        sa.Column(
            "role",
            sa.String(length=20),
            nullable=False,
            server_default="USER",
        ),
    )


# ============================================================
# DOWNGRADE
# ============================================================

def downgrade() -> None:
    """
    Remove role column from users table.
    """

    op.drop_column(
        "users",
        "role",
    )