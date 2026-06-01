"""add service order completion and cancellation fields

Revision ID: 0006_add_service_order_timestamps_and_reason
Revises: 0005_add_priority_technician_so
Create Date: 2026-05-31

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "0006_add_service_order_timestamps_and_reason"
down_revision = "0005_add_priority_technician_so"
branch_labels = None
depends_on = None


def _has_table(inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names()


def _has_column(inspector, table_name: str, column_name: str) -> bool:
    return any(col["name"] == column_name for col in inspector.get_columns(table_name))


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if not _has_table(inspector, "service_orders"):
        return

    if not _has_column(inspector, "service_orders", "completed_at"):
        op.add_column(
            "service_orders",
            sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        )

    if not _has_column(inspector, "service_orders", "cancellation_reason"):
        op.add_column(
            "service_orders",
            sa.Column("cancellation_reason", sa.Text(), nullable=True),
        )

    if not _has_column(inspector, "service_orders", "service_time_seconds"):
        op.add_column(
            "service_orders",
            sa.Column("service_time_seconds", sa.Integer(), nullable=True),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if not _has_table(inspector, "service_orders"):
        return

    if _has_column(inspector, "service_orders", "service_time_seconds"):
        op.drop_column("service_orders", "service_time_seconds")

    if _has_column(inspector, "service_orders", "cancellation_reason"):
        op.drop_column("service_orders", "cancellation_reason")

    if _has_column(inspector, "service_orders", "completed_at"):
        op.drop_column("service_orders", "completed_at")