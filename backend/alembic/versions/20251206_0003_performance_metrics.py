"""Add performance_metrics table with TimescaleDB hypertable and retention policies.

Epic 006: Analytics Dashboard
Story 006-02: Performance-Historie und Aggregationen

Revision ID: 0003
Revises: 0002
Create Date: 2025-12-06

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create performance_metrics table
    op.create_table(
        "performance_metrics",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("team_instance_id", sa.Integer(), nullable=False),
        sa.Column(
            "timestamp",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column("period", sa.String(length=10), nullable=False),
        sa.Column("pnl", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("pnl_percent", sa.Float(), nullable=False),
        sa.Column("win_rate", sa.Float(), nullable=False),
        sa.Column("sharpe_ratio", sa.Float(), nullable=True),
        sa.Column("max_drawdown", sa.Float(), nullable=False),
        sa.Column("trade_count", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["team_instance_id"],
            ["team_instances.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes
    op.create_index(
        "ix_performance_metrics_team_instance_id",
        "performance_metrics",
        ["team_instance_id"],
        unique=False,
    )
    op.create_index(
        "ix_performance_metrics_timestamp",
        "performance_metrics",
        ["timestamp"],
        unique=False,
    )
    op.create_index(
        "ix_performance_metrics_period",
        "performance_metrics",
        ["period"],
        unique=False,
    )
    op.create_index(
        "ix_performance_metrics_composite",
        "performance_metrics",
        ["team_instance_id", "period", "timestamp"],
        unique=False,
    )

    # Note: TimescaleDB hypertable conversion requires composite primary keys
    # including the time column. For now, using regular tables with indexes.
    # To enable hypertables later, tables need (id, timestamp) composite PK.
    # op.execute(
    #     "SELECT create_hypertable('performance_metrics', 'timestamp', "
    #     "migrate_data => true, if_not_exists => true)"
    # )

    # Retention policies disabled until hypertable is enabled
    # op.execute(
    #     """
    #     SELECT add_retention_policy('performance_metrics',
    #         INTERVAL '7 days',
    #         if_not_exists => true,
    #         schedule_interval => INTERVAL '1 day'
    #     )
    #     WHERE period = 'hourly'
    #     """
    # )


def downgrade() -> None:
    # Remove retention policy (disabled - no hypertable)
    # op.execute(
    #     "SELECT remove_retention_policy('performance_metrics', if_exists => true)"
    # )

    # Drop indexes
    op.drop_index("ix_performance_metrics_composite", table_name="performance_metrics")
    op.drop_index("ix_performance_metrics_period", table_name="performance_metrics")
    op.drop_index("ix_performance_metrics_timestamp", table_name="performance_metrics")
    op.drop_index(
        "ix_performance_metrics_team_instance_id", table_name="performance_metrics"
    )

    # Drop table (hypertable becomes regular table first automatically)
    op.drop_table("performance_metrics")
