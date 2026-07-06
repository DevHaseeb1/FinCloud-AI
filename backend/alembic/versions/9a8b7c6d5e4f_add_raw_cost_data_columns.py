"""add line_item_type, resource_id, operation, product_family, pricing_term, currency_code, normalization_factor to raw_cost_data

Revision ID: 9a8b7c6d5e4f
Revises: efbdace20d3f
Create Date: 2026-06-29 10:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9a8b7c6d5e4f"
down_revision: Union[str, None] = "2a3b4c5d6e7f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def has_column(table: str, column: str) -> bool:
    conn = op.get_bind()
    dialect = conn.dialect.name
    if dialect == "postgresql":
        from sqlalchemy import text
        result = conn.execute(
            text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name = :t AND column_name = :c"
            ),
            {"t": table, "c": column},
        )
        return result.first() is not None
    else:
        inspector = sa.inspect(conn)
        cols = [c["name"] for c in inspector.get_columns(table)]
        return column in cols


def upgrade() -> None:
    if not has_column("raw_cost_data", "line_item_type"):
        op.add_column("raw_cost_data", sa.Column("line_item_type", sa.String(50), nullable=True))
    if not has_column("raw_cost_data", "resource_id"):
        op.add_column("raw_cost_data", sa.Column("resource_id", sa.String(200), nullable=True))
    if not has_column("raw_cost_data", "operation"):
        op.add_column("raw_cost_data", sa.Column("operation", sa.String(100), nullable=True))
    if not has_column("raw_cost_data", "product_family"):
        op.add_column("raw_cost_data", sa.Column("product_family", sa.String(100), nullable=True))
    if not has_column("raw_cost_data", "pricing_term"):
        op.add_column("raw_cost_data", sa.Column("pricing_term", sa.String(50), nullable=True))
    if not has_column("raw_cost_data", "currency_code"):
        op.add_column("raw_cost_data", sa.Column("currency_code", sa.String(10), nullable=True))
    if not has_column("raw_cost_data", "normalization_factor"):
        op.add_column("raw_cost_data", sa.Column("normalization_factor", sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column("raw_cost_data", "normalization_factor")
    op.drop_column("raw_cost_data", "currency_code")
    op.drop_column("raw_cost_data", "pricing_term")
    op.drop_column("raw_cost_data", "product_family")
    op.drop_column("raw_cost_data", "operation")
    op.drop_column("raw_cost_data", "resource_id")
    op.drop_column("raw_cost_data", "line_item_type")
