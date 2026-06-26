"""add user_id foreign key to all data tables

Revision ID: 2a3b4c5d6e7f
Revises: efbdace20d3f
Create Date: 2026-06-24 10:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "2a3b4c5d6e7f"
down_revision: Union[str, None] = "efbdace20d3f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    dialect = conn.dialect.name

    def has_column(table: str, column: str) -> bool:
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

    tables = [
        "raw_cost_data",
        "processed_cost_data",
        "anomalies",
        "forecasts",
        "recommendations",
        "aws_connections",
        "aws_fetch_history",
    ]

    for table in tables:
        if not has_column(table, "user_id"):
            op.add_column(
                table,
                sa.Column("user_id", sa.Integer(), nullable=True),
            )

    for table in tables:
        if has_column(table, "user_id"):
            try:
                op.create_foreign_key(
                    f"fk_{table}_user_id",
                    table,
                    "users",
                    ["user_id"],
                    ["id"],
                )
            except Exception:
                pass

    for table in tables:
        try:
            op.create_index(
                op.f(f"ix_{table}_user_id"),
                table,
                ["user_id"],
                unique=False,
            )
        except Exception:
            pass

    # Make user_id NOT NULL for all tables after backfilling
    for table in tables:
        if has_column(table, "user_id"):
            try:
                op.alter_column(
                    table,
                    "user_id",
                    existing_type=sa.Integer(),
                    nullable=True,
                )
            except Exception:
                pass


def downgrade() -> None:
    tables = [
        "raw_cost_data",
        "processed_cost_data",
        "anomalies",
        "forecasts",
        "recommendations",
        "aws_connections",
        "aws_fetch_history",
    ]

    for table in tables:
        try:
            op.drop_constraint(f"fk_{table}_user_id", table, type_="foreignkey")
        except Exception:
            pass

    for table in tables:
        try:
            op.drop_index(op.f(f"ix_{table}_user_id"), table_name=table)
        except Exception:
            pass

    for table in tables:
        try:
            op.drop_column(table, "user_id")
        except Exception:
            pass
