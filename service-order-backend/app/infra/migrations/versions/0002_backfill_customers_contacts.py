"""backfill customer management fields

Revision ID: 0002_backfill_customers_contacts
Revises: 0001_bootstrap_tables
Create Date: 2026-05-21
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "0002_backfill_customers_contacts"
down_revision = "0001_bootstrap_tables"
branch_labels = None
depends_on = None


def _has_table(inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names()


def _has_column(inspector, table_name: str, column_name: str) -> bool:
    return any(column["name"] == column_name for column in inspector.get_columns(table_name))


def _has_index(inspector, table_name: str, index_name: str) -> bool:
    return any(index["name"] == index_name for index in inspector.get_indexes(table_name))


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if not _has_table(inspector, "customers"):
        return

    for column_name, column_type in [
        ("nome", sa.String(length=255)),
        ("cpf", sa.String(length=20)),
        ("telefone", sa.String(length=20)),
        ("email", sa.String(length=255)),
        ("endereco", sa.String(length=255)),
    ]:
        if not _has_column(inspector, "customers", column_name):
            op.add_column("customers", sa.Column(column_name, column_type, nullable=True))

    existing_indexes = {index["name"] for index in inspector.get_indexes("customers")}
    if "ix_customers_nome" not in existing_indexes:
        op.create_index("ix_customers_nome", "customers", ["nome"], unique=False)
    if "ix_customers_cpf" not in existing_indexes:
        op.create_index("ix_customers_cpf", "customers", ["cpf"], unique=True)
    if "ix_customers_telefone" not in existing_indexes:
        op.create_index("ix_customers_telefone", "customers", ["telefone"], unique=False)
    if "ix_customers_email" not in existing_indexes:
        op.create_index("ix_customers_email", "customers", ["email"], unique=True)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if not _has_table(inspector, "customers"):
        return

    for index_name in ["ix_customers_email", "ix_customers_telefone", "ix_customers_cpf", "ix_customers_nome"]:
        if _has_index(inspector, "customers", index_name):
            op.drop_index(index_name, table_name="customers")