"""Add team instance full schema with status, mode, template, and symbols.

Epic 005: Team-Instanz-Management

Revision ID: 0002
Revises: 0001
Create Date: 2025-12-06

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create enum types (IF NOT EXISTS to handle partial migrations)
    op.execute(
        "DO $$ BEGIN "
        "CREATE TYPE teaminstancestatus AS ENUM ('active', 'paused', 'stopped'); "
        "EXCEPTION WHEN duplicate_object THEN null; END $$"
    )
    op.execute(
        "DO $$ BEGIN "
        "CREATE TYPE teaminstancemode AS ENUM ('paper', 'live'); "
        "EXCEPTION WHEN duplicate_object THEN null; END $$"
    )

    # Create team_instances table
    op.create_table(
        "team_instances",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("template_name", sa.String(length=100), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM("active", "paused", "stopped", name="teaminstancestatus", create_type=False),
            nullable=False,
            server_default="stopped",
        ),
        sa.Column(
            "mode",
            postgresql.ENUM("paper", "live", name="teaminstancemode", create_type=False),
            nullable=False,
            server_default="paper",
        ),
        sa.Column("symbols", postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "initial_budget",
            sa.Numeric(precision=18, scale=2),
            nullable=False,
            server_default="10000.00",
        ),
        sa.Column(
            "current_budget",
            sa.Numeric(precision=18, scale=2),
            nullable=False,
            server_default="10000.00",
        ),
        sa.Column(
            "realized_pnl",
            sa.Numeric(precision=18, scale=2),
            nullable=False,
            server_default="0.00",
        ),
        sa.Column(
            "unrealized_pnl",
            sa.Numeric(precision=18, scale=2),
            nullable=False,
            server_default="0.00",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_team_instances_status", "team_instances", ["status"], unique=False
    )
    op.create_index(
        "ix_team_instances_created_at", "team_instances", ["created_at"], unique=False
    )

    # Create trades table
    op.create_table(
        "trades",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("team_instance_id", sa.Integer(), nullable=False),
        sa.Column("ticket", sa.Integer(), nullable=False),
        sa.Column("symbol", sa.String(length=20), nullable=False),
        sa.Column("side", sa.String(length=4), nullable=False),
        sa.Column("size", sa.Numeric(precision=18, scale=8), nullable=False),
        sa.Column("entry_price", sa.Numeric(precision=18, scale=6), nullable=False),
        sa.Column("exit_price", sa.Numeric(precision=18, scale=6), nullable=True),
        sa.Column("stop_loss", sa.Numeric(precision=18, scale=6), nullable=True),
        sa.Column("take_profit", sa.Numeric(precision=18, scale=6), nullable=True),
        sa.Column("pnl", sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column(
            "spread_cost",
            sa.Numeric(precision=18, scale=2),
            nullable=False,
            server_default="0.00",
        ),
        sa.Column(
            "status",
            sa.String(length=10),
            nullable=False,
            server_default="open",
        ),
        sa.Column(
            "opened_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("magic_number", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("comment", sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(
            ["team_instance_id"],
            ["team_instances.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_trades_team_instance_id", "trades", ["team_instance_id"])
    op.create_index("ix_trades_opened_at", "trades", ["opened_at"])
    op.create_index("ix_trades_symbol", "trades", ["symbol"])
    op.create_index("ix_trades_status", "trades", ["status"])
    op.create_index("ix_trades_ticket", "trades", ["ticket"])

    # Create agent_decisions table (for audit logging)
    op.create_table(
        "agent_decisions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("team_instance_id", sa.Integer(), nullable=False),
        sa.Column("agent_name", sa.String(length=50), nullable=False),
        sa.Column("decision_type", sa.String(length=20), nullable=False),
        sa.Column("data", postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["team_instance_id"],
            ["team_instances.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_agent_decisions_team_instance_id", "agent_decisions", ["team_instance_id"]
    )
    op.create_index(
        "ix_agent_decisions_created_at", "agent_decisions", ["created_at"]
    )
    op.create_index(
        "ix_agent_decisions_agent_name", "agent_decisions", ["agent_name"]
    )
    op.create_index(
        "ix_agent_decisions_decision_type", "agent_decisions", ["decision_type"]
    )

    # Note: TimescaleDB hypertable conversion requires composite primary keys
    # including the time column. For now, using regular tables with indexes.
    # To enable hypertables later, tables need (id, opened_at) composite PK.
    # op.execute(
    #     "SELECT create_hypertable('trades', 'opened_at', "
    #     "migrate_data => true, if_not_exists => true)"
    # )
    # op.execute(
    #     "SELECT create_hypertable('agent_decisions', 'created_at', "
    #     "migrate_data => true, if_not_exists => true)"
    # )


def downgrade() -> None:
    # Drop hypertables (they become regular tables)
    op.drop_table("agent_decisions")
    op.drop_table("trades")
    op.drop_index("ix_team_instances_created_at", table_name="team_instances")
    op.drop_index("ix_team_instances_status", table_name="team_instances")
    op.drop_table("team_instances")

    # Drop enum types
    op.execute("DROP TYPE IF EXISTS teaminstancemode")
    op.execute("DROP TYPE IF EXISTS teaminstancestatus")
