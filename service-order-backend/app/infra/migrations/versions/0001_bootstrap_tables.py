"""bootstrap tables

Revision ID: 0001_bootstrap_tables
Revises:
Create Date: 2026-05-20
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "0001_bootstrap_tables"
down_revision = None
branch_labels = None
depends_on = None


def _has_table(inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names()


def _has_column(inspector, table_name: str, column_name: str) -> bool:
    return any(col["name"] == column_name for col in inspector.get_columns(table_name))


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if not _has_table(inspector, "users"):
        op.create_table(
            "users",
            sa.Column("id", sa.String(length=36), primary_key=True),
            sa.Column("email", sa.String(length=255), nullable=False),
            sa.Column("password", sa.String(length=255), nullable=False),
            sa.Column("full_name", sa.String(length=255), nullable=True),
            sa.Column("role", sa.String(length=20), nullable=False, server_default=sa.text("'client'")),
            sa.Column("is_active", sa.Boolean(), nullable=True, server_default=sa.text("1")),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        )
        op.create_index("ix_users_email", "users", ["email"], unique=True)

    if _has_table(inspector, "users") and not _has_column(inspector, "users", "role"):
        op.add_column(
            "users",
            sa.Column("role", sa.String(length=20), nullable=False, server_default=sa.text("'client'")),
        )

    if not _has_table(inspector, "password_recovery"):
        op.create_table(
            "password_recovery",
            sa.Column("id", sa.String(length=36), primary_key=True),
            sa.Column("user_id", sa.String(length=36), nullable=False),
            sa.Column("recovery_code", sa.String(length=6), nullable=False),
            sa.Column("is_used", sa.Integer(), nullable=True, server_default=sa.text("0")),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        )
        op.create_index("ix_password_recovery_recovery_code", "password_recovery", ["recovery_code"], unique=True)

    if not _has_table(inspector, "customers"):
        op.create_table(
            "customers",
            sa.Column("id", sa.String(length=36), primary_key=True),
            sa.Column("nome", sa.String(length=255), nullable=False),
            sa.Column("cpf", sa.String(length=20), nullable=False),
            sa.Column("telefone", sa.String(length=20), nullable=False),
            sa.Column("email", sa.String(length=255), nullable=False),
            sa.Column("endereco", sa.String(length=255), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        )
        op.create_index("ix_customers_nome", "customers", ["nome"], unique=False)
        op.create_index("ix_customers_cpf", "customers", ["cpf"], unique=True)
        op.create_index("ix_customers_telefone", "customers", ["telefone"], unique=False)
        op.create_index("ix_customers_email", "customers", ["email"], unique=True)

    if _has_table(inspector, "customers"):
        existing_columns = {column["name"] for column in inspector.get_columns("customers")}

        for column_name, column_type in [
            ("nome", sa.String(length=255)),
            ("cpf", sa.String(length=20)),
            ("telefone", sa.String(length=20)),
            ("email", sa.String(length=255)),
            ("endereco", sa.String(length=255)),
        ]:
            if column_name not in existing_columns:
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

    if not _has_table(inspector, "service_orders"):
        op.create_table(
            "service_orders",
            sa.Column("id", sa.String(length=36), primary_key=True),
            sa.Column("customer_id", sa.String(length=36), nullable=False),
            sa.Column("title", sa.String(length=255), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column(
                "status",
                sa.Enum("pending", "in_progress", "completed", "cancelled", name="serviceorderstatus"),
                nullable=True,
                server_default=sa.text("'pending'"),
            ),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(["customer_id"], ["customers.id"]),
        )
        op.create_index("ix_service_orders_customer_id", "service_orders", ["customer_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_service_orders_customer_id", table_name="service_orders")
    op.drop_table("service_orders")
    op.drop_index("ix_customers_email", table_name="customers")
    op.drop_index("ix_customers_telefone", table_name="customers")
    op.drop_index("ix_customers_cpf", table_name="customers")
    op.drop_index("ix_customers_nome", table_name="customers")
    op.drop_table("customers")
    op.drop_index("ix_password_recovery_recovery_code", table_name="password_recovery")
    op.drop_table("password_recovery")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
