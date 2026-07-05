"""add explanation columns to anomalies table

Revision ID: efbdace20d3f
Revises:
Create Date: 2026-06-24 02:53:41.038577

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "efbdace20d3f"
down_revision: Union[str, None] = None
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

    def has_index(table: str, index_name: str) -> bool:
        if dialect == "postgresql":
            from sqlalchemy import text
            result = conn.execute(
                text(
                    "SELECT indexname FROM pg_indexes "
                    "WHERE tablename = :t AND indexname = :n"
                ),
                {"t": table, "n": index_name},
            )
            return result.first() is not None
        elif dialect == "sqlite":
            from sqlalchemy import text
            result = conn.execute(
                text(
                    "SELECT name FROM sqlite_master "
                    "WHERE type='index' AND tbl_name=:t AND name=:n"
                ),
                {"t": table, "n": index_name},
            )
            return result.first() is not None
        else:
            try:
                inspector = sa.inspect(conn)
                idxs = [ix["name"] for ix in inspector.get_indexes(table)]
                return index_name in idxs
            except Exception:
                return False

    if not has_column("anomalies", "cost_zscore"):
        op.add_column("anomalies", sa.Column("cost_zscore", sa.Float(), nullable=True))
    if not has_column("anomalies", "cost_ratio_p95"):
        op.add_column("anomalies", sa.Column("cost_ratio_p95", sa.Float(), nullable=True))
    if not has_column("anomalies", "daily_spend_zscore"):
        op.add_column("anomalies", sa.Column("daily_spend_zscore", sa.Float(), nullable=True))
    if not has_column("anomalies", "cost_per_unit_ratio"):
        op.add_column("anomalies", sa.Column("cost_per_unit_ratio", sa.Float(), nullable=True))
    if not has_column("anomalies", "error_count"):
        op.add_column("anomalies", sa.Column("error_count", sa.Integer(), nullable=True))

    if not has_index("anomalies", "ix_anomalies_cost_zscore"):
        op.create_index(op.f("ix_anomalies_cost_zscore"), "anomalies", ["cost_zscore"], unique=False)
    if not has_index("anomalies", "ix_anomalies_cost_ratio_p95"):
        op.create_index(op.f("ix_anomalies_cost_ratio_p95"), "anomalies", ["cost_ratio_p95"], unique=False)
    if not has_index("anomalies", "ix_anomalies_daily_spend_zscore"):
        op.create_index(op.f("ix_anomalies_daily_spend_zscore"), "anomalies", ["daily_spend_zscore"], unique=False)
    if not has_index("anomalies", "ix_anomalies_cost_per_unit_ratio"):
        op.create_index(op.f("ix_anomalies_cost_per_unit_ratio"), "anomalies", ["cost_per_unit_ratio"], unique=False)
    if not has_index("anomalies", "ix_anomalies_error_count"):
        op.create_index(op.f("ix_anomalies_error_count"), "anomalies", ["error_count"], unique=False)


def downgrade() -> None:
    conn = op.get_bind()
    dialect = conn.dialect.name

    def has_index(table: str, index_name: str) -> bool:
        if dialect == "postgresql":
            from sqlalchemy import text
            result = conn.execute(
                text(
                    "SELECT indexname FROM pg_indexes "
                    "WHERE tablename = :t AND indexname = :n"
                ),
                {"t": table, "n": index_name},
            )
            return result.first() is not None
        elif dialect == "sqlite":
            from sqlalchemy import text
            result = conn.execute(
                text(
                    "SELECT name FROM sqlite_master "
                    "WHERE type='index' AND tbl_name=:t AND name=:n"
                ),
                {"t": table, "n": index_name},
            )
            return result.first() is not None
        else:
            try:
                inspector = sa.inspect(conn)
                idxs = [ix["name"] for ix in inspector.get_indexes(table)]
                return index_name in idxs
            except Exception:
                return False

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

    if has_index("anomalies", "ix_anomalies_error_count"):
        op.drop_index(op.f("ix_anomalies_error_count"), table_name="anomalies")
    if has_index("anomalies", "ix_anomalies_cost_per_unit_ratio"):
        op.drop_index(op.f("ix_anomalies_cost_per_unit_ratio"), table_name="anomalies")
    if has_index("anomalies", "ix_anomalies_daily_spend_zscore"):
        op.drop_index(op.f("ix_anomalies_daily_spend_zscore"), table_name="anomalies")
    if has_index("anomalies", "ix_anomalies_cost_ratio_p95"):
        op.drop_index(op.f("ix_anomalies_cost_ratio_p95"), table_name="anomalies")
    if has_index("anomalies", "ix_anomalies_cost_zscore"):
        op.drop_index(op.f("ix_anomalies_cost_zscore"), table_name="anomalies")

    if has_column("anomalies", "error_count"):
        op.drop_column("anomalies", "error_count")
    if has_column("anomalies", "cost_per_unit_ratio"):
        op.drop_column("anomalies", "cost_per_unit_ratio")
    if has_column("anomalies", "daily_spend_zscore"):
        op.drop_column("anomalies", "daily_spend_zscore")
    if has_column("anomalies", "cost_ratio_p95"):
        op.drop_column("anomalies", "cost_ratio_p95")
    if has_column("anomalies", "cost_zscore"):
        op.drop_column("anomalies", "cost_zscore")
