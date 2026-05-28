"""create technicians and parts tables

Revision ID: 0003_create_technicians_and_parts
Revises: 0002_backfill_customers_contacts
Create Date: 2026-05-21
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "0003_create_technicians_and_parts"
down_revision = "0002_backfill_customers_contacts"
branch_labels = None
depends_on = None


def _has_table(inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names()


def _has_index(inspector, table_name: str, index_name: str) -> bool:
    return any(index["name"] == index_name for index in inspector.get_indexes(table_name))


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if not _has_table(inspector, "technicians"):
        op.create_table(
            "technicians",
            sa.Column("id", sa.String(length=36), primary_key=True),
            sa.Column("full_name", sa.String(length=255), nullable=False),
            sa.Column("email", sa.String(length=255), nullable=False),
            sa.Column("phone", sa.String(length=20), nullable=False),
            sa.Column("specialty", sa.String(length=100), nullable=False),
            sa.Column("is_active", sa.Boolean(), nullable=True, server_default=sa.text("1")),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        )
        op.create_index("ix_technicians_full_name", "technicians", ["full_name"], unique=False)
        op.create_index("ix_technicians_email", "technicians", ["email"], unique=True)
        op.create_index("ix_technicians_phone", "technicians", ["phone"], unique=False)
        op.create_index("ix_technicians_specialty", "technicians", ["specialty"], unique=False)

    if not _has_table(inspector, "parts"):
        op.create_table(
            "parts",
            sa.Column("id", sa.String(length=36), primary_key=True),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("sku", sa.String(length=80), nullable=False),
            sa.Column("description", sa.String(length=500), nullable=True),
            sa.Column("quantity", sa.Integer(), nullable=False, server_default=sa.text("0")),
            sa.Column("price", sa.Numeric(10, 2), nullable=False, server_default=sa.text("0")),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        )
        op.create_index("ix_parts_name", "parts", ["name"], unique=False)
        op.create_index("ix_parts_sku", "parts", ["sku"], unique=True)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if _has_table(inspector, "parts"):
        if _has_index(inspector, "parts", "ix_parts_sku"):
            op.drop_index("ix_parts_sku", table_name="parts")
        if _has_index(inspector, "parts", "ix_parts_name"):
            op.drop_index("ix_parts_name", table_name="parts")
        op.drop_table("parts")

    if _has_table(inspector, "technicians"):
        if _has_index(inspector, "technicians", "ix_technicians_specialty"):
            op.drop_index("ix_technicians_specialty", table_name="technicians")
        if _has_index(inspector, "technicians", "ix_technicians_phone"):
            op.drop_index("ix_technicians_phone", table_name="technicians")
        if _has_index(inspector, "technicians", "ix_technicians_email"):
            op.drop_index("ix_technicians_email", table_name="technicians")
        if _has_index(inspector, "technicians", "ix_technicians_full_name"):
            op.drop_index("ix_technicians_full_name", table_name="technicians")
        op.drop_table("technicians")
