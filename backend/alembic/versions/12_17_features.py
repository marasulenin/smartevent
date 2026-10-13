"""Add payment coupon review and booking discount fields.

Revision ID: 1217features
Revises: e71830b6e5f5
"""
from alembic import op
import sqlalchemy as sa

revision = "1217features"
down_revision = "ec3e86c44f41"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "coupons",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("coupon_code", sa.String(50), nullable=False),
        sa.Column("discount_type", sa.Enum("PERCENTAGE", "FIXED", name="discounttype"), nullable=False),
        sa.Column("discount_value", sa.Float(), nullable=False),
        sa.Column("minimum_booking_amount", sa.Float(), nullable=False, server_default="0"),
        sa.Column("expiry_date", sa.DateTime(), nullable=False),
        sa.Column("usage_limit", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_coupons_coupon_code", "coupons", ["coupon_code"], unique=True)

    op.add_column("bookings", sa.Column("coupon_id", sa.Integer(), nullable=True))
    op.add_column("bookings", sa.Column("discount_amount", sa.Float(), nullable=False, server_default="0"))
    op.add_column("bookings", sa.Column("final_amount", sa.Float(), nullable=True))
    op.execute("UPDATE bookings SET final_amount = total_price WHERE final_amount IS NULL")

    with op.batch_alter_table("bookings", recreate="always") as batch:
        batch.create_foreign_key("fk_bookings_coupon_id", "coupons", ["coupon_id"], ["id"])
        batch.alter_column("final_amount", nullable=False)

    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("booking_id", sa.Integer(), sa.ForeignKey("bookings.id"), nullable=False),
        sa.Column("payment_method", sa.Enum("CARD", "UPI", "NET_BANKING", "SIMULATION", name="paymentmethod"), nullable=False),
        sa.Column("payment_status", sa.Enum("PENDING", "SUCCESS", "FAILED", name="paymentstatus"), nullable=False),
        sa.Column("transaction_id", sa.String(100), nullable=True),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_payments_transaction_id", "payments", ["transaction_id"], unique=True)

    op.create_table(
        "reviews",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("event_id", sa.Integer(), sa.ForeignKey("events.id"), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("review_text", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    # Existing notification enum is recreated by SQLite when needed.
    with op.batch_alter_table("notifications", recreate="always") as batch:
        batch.alter_column("type", existing_type=sa.Enum("EVENT", "BOOKING", "SYSTEM", name="notificationtype"), type_=sa.Enum("EVENT", "BOOKING", "PAYMENT", "SYSTEM", name="notificationtype"), existing_nullable=False)


def downgrade():
    op.drop_table("reviews")
    op.drop_table("payments")
    op.drop_index("ix_coupons_coupon_code", table_name="coupons")
    op.drop_table("coupons")
    with op.batch_alter_table("bookings", recreate="always") as batch:
        batch.drop_column("final_amount")
        batch.drop_column("discount_amount")
        batch.drop_column("coupon_id")
    with op.batch_alter_table("notifications", recreate="always") as batch:
        batch.alter_column("type", existing_type=sa.Enum("EVENT", "BOOKING", "PAYMENT", "SYSTEM", name="notificationtype"), type_=sa.Enum("EVENT", "BOOKING", "SYSTEM", name="notificationtype"), existing_nullable=False)
