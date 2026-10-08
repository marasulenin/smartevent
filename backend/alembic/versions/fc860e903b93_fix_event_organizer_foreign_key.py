"""fix event organizer foreign key

Revision ID: fc860e903b93
Revises: 39d23cf9d72e
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "fc860e903b93"
down_revision: Union[str, Sequence[str], None] = "39d23cf9d72e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # SQLite requires batch mode for changing column constraints.
    with op.batch_alter_table("events", recreate="always") as batch_op:
        batch_op.alter_column(
            "organizer_id",
            existing_type=sa.Integer(),
            nullable=False,
        )

        batch_op.create_foreign_key(
            "fk_events_organizer_id_users",
            "users",
            ["organizer_id"],
            ["id"],
        )


def downgrade() -> None:
    with op.batch_alter_table("events", recreate="always") as batch_op:
        batch_op.drop_constraint(
            "fk_events_organizer_id_users",
            type_="foreignkey",
        )

        batch_op.alter_column(
            "organizer_id",
            existing_type=sa.Integer(),
            nullable=True,
        )