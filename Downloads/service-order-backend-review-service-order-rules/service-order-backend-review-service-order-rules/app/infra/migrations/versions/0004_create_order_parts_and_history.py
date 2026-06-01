"""create order_parts and history tables

Revision ID: 0004_create_order_parts_and_history
Revises: 0003_create_technicians_and_parts
Create Date: 2026-05-19

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "0004_create_order_parts_and_history"
down_revision = "0003_create_technicians_and_parts"
branch_labels = None
depends_on = None


def _has_table(inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names()


def _has_index(inspector, table_name: str, index_name: str) -> bool:
    return any(index["name"] == index_name for index in inspector.get_indexes(table_name))


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if not _has_table(inspector, "order_parts"):
        op.create_table(
            "order_parts",
            sa.Column("id", sa.String(length=36), primary_key=True),
            sa.Column("service_order_id", sa.String(length=36), sa.ForeignKey("service_orders.id"), nullable=False),
            sa.Column("part_id", sa.String(length=36), sa.ForeignKey("parts.id"), nullable=False),
            sa.Column("quantity", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")),
        )
        op.create_index("ix_order_parts_service_order_id", "order_parts", ["service_order_id"], unique=False)
        op.create_index("ix_order_parts_part_id", "order_parts", ["part_id"], unique=False)

    if not _has_table(inspector, "history"):
        op.create_table(
            "history",
            sa.Column("id", sa.String(length=36), primary_key=True),
            sa.Column("event_type", sa.String(length=50), nullable=False),
            sa.Column("description", sa.Text(), nullable=False),
            sa.Column("service_order_id", sa.String(length=36), sa.ForeignKey("service_orders.id"), nullable=True),
            sa.Column("part_id", sa.String(length=36), sa.ForeignKey("parts.id"), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")),
        )
        op.create_index("ix_history_service_order_id", "history", ["service_order_id"], unique=False)
        op.create_index("ix_history_event_type", "history", ["event_type"], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if _has_table(inspector, "history"):
        if _has_index(inspector, "history", "ix_history_event_type"):
            op.drop_index("ix_history_event_type", table_name="history")
        if _has_index(inspector, "history", "ix_history_service_order_id"):
            op.drop_index("ix_history_service_order_id", table_name="history")
        op.drop_table("history")

    if _has_table(inspector, "order_parts"):
        if _has_index(inspector, "order_parts", "ix_order_parts_part_id"):
            op.drop_index("ix_order_parts_part_id", table_name="order_parts")
        if _has_index(inspector, "order_parts", "ix_order_parts_service_order_id"):
            op.drop_index("ix_order_parts_service_order_id", table_name="order_parts")
        op.drop_table("order_parts")