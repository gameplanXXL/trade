"""SQLAlchemy database models."""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, Numeric, String, func
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.session import Base


class TeamInstanceStatus(str, Enum):
    """Status of a team instance."""

    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"


class TeamInstanceMode(str, Enum):
    """Trading mode for a team instance."""

    PAPER = "paper"
    LIVE = "live"


class User(Base):
    """User model for authentication."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username!r})>"


class TeamInstance(Base):
    """Team instance model with budget tracking.

    Tracks virtual budget and P/L for paper trading per team instance.
    Full lifecycle management in Epic 005.
    """

    __tablename__ = "team_instances"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    template_name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Status and mode (Story 005-01)
    # Note: create_type=False because enum types are created in Alembic migrations
    # Note: values_callable ensures enum values (not names) are used in SQL
    status: Mapped[TeamInstanceStatus] = mapped_column(
        SQLEnum(
            TeamInstanceStatus,
            create_type=False,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        default=TeamInstanceStatus.STOPPED,
    )
    mode: Mapped[TeamInstanceMode] = mapped_column(
        SQLEnum(
            TeamInstanceMode,
            create_type=False,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        default=TeamInstanceMode.PAPER,
    )

    # Trading symbols (canonical format: EUR/USD)
    symbols: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)

    # Budget tracking (Story 004-05)
    initial_budget: Mapped[Decimal] = mapped_column(
        Numeric(precision=18, scale=2),
        nullable=False,
        default=Decimal("10000.00"),
    )
    current_budget: Mapped[Decimal] = mapped_column(
        Numeric(precision=18, scale=2),
        nullable=False,
        default=Decimal("10000.00"),
    )
    realized_pnl: Mapped[Decimal] = mapped_column(
        Numeric(precision=18, scale=2),
        nullable=False,
        default=Decimal("0.00"),
    )
    unrealized_pnl: Mapped[Decimal] = mapped_column(
        Numeric(precision=18, scale=2),
        nullable=False,
        default=Decimal("0.00"),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=True,
    )

    # Relationships
    trades: Mapped[list["Trade"]] = relationship(
        "Trade", back_populates="team_instance", cascade="all, delete-orphan"
    )
    decisions: Mapped[list["AgentDecisionLog"]] = relationship(
        "AgentDecisionLog", backref="team_instance"
    )

    __table_args__ = (
        Index("ix_team_instances_status", "status"),
        Index("ix_team_instances_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<TeamInstance(id={self.id}, name={self.name!r}, "
            f"status={self.status.value}, budget={self.current_budget})>"
        )


class Trade(Base):
    """Trade model for tracking all executed trades.

    Records every trade for paper trading and live trading.
    Designed for TimescaleDB hypertable conversion.
    """

    __tablename__ = "trades"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    team_instance_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("team_instances.id"),
        nullable=False,
    )

    # Trade details
    ticket: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    symbol: Mapped[str] = mapped_column(String(20), nullable=False)  # Canonical: EUR/USD
    side: Mapped[str] = mapped_column(String(4), nullable=False)  # BUY, SELL
    size: Mapped[Decimal] = mapped_column(Numeric(precision=18, scale=8), nullable=False)

    # Prices
    entry_price: Mapped[Decimal] = mapped_column(
        Numeric(precision=18, scale=6), nullable=False
    )
    exit_price: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=18, scale=6), nullable=True
    )
    stop_loss: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=18, scale=6), nullable=True
    )
    take_profit: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=18, scale=6), nullable=True
    )

    # Trailing stop configuration (M4 fix: persist for restart recovery)
    trailing_stop_pct: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=5, scale=2), nullable=True
    )

    # P/L
    pnl: Mapped[Decimal | None] = mapped_column(Numeric(precision=18, scale=2), nullable=True)
    spread_cost: Mapped[Decimal] = mapped_column(
        Numeric(precision=18, scale=2),
        nullable=False,
        default=Decimal("0.00"),
    )

    # Status
    status: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="open",
    )  # open, closed

    # Timestamps
    opened_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    closed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Metadata
    magic_number: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    comment: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Relationship
    team_instance: Mapped["TeamInstance"] = relationship("TeamInstance", back_populates="trades")

    __table_args__ = (
        Index("ix_trades_team_instance_id", "team_instance_id"),
        Index("ix_trades_opened_at", "opened_at"),
        Index("ix_trades_symbol", "symbol"),
        Index("ix_trades_status", "status"),
    )

    def __repr__(self) -> str:
        return (
            f"<Trade(id={self.id}, ticket={self.ticket}, symbol={self.symbol!r}, "
            f"side={self.side}, status={self.status})>"
        )


class AgentDecisionLog(Base):
    """Audit log for agent decisions - Story 003-04.

    Records every decision made by agents during pipeline execution
    for audit, debugging, and analytics purposes.

    Note: This table is designed for TimescaleDB hypertable conversion.
    See Alembic migration for hypertable setup.
    """

    __tablename__ = "agent_decisions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    team_instance_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("team_instances.id"),
        nullable=False,
    )
    agent_name: Mapped[str] = mapped_column(String(50), nullable=False)
    decision_type: Mapped[str] = mapped_column(String(20), nullable=False)
    data: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        Index("ix_agent_decisions_team_instance_id", "team_instance_id"),
        Index("ix_agent_decisions_created_at", "created_at"),
        Index("ix_agent_decisions_agent_name", "agent_name"),
        Index("ix_agent_decisions_decision_type", "decision_type"),
    )

    def __repr__(self) -> str:
        return (
            f"<AgentDecisionLog(id={self.id}, agent={self.agent_name!r}, "
            f"type={self.decision_type!r})>"
        )


class PerformanceMetric(Base):
    """Performance metrics aggregated over time - Story 006-02.

    Stores pre-calculated performance metrics for teams at different time periods
    (hourly, daily, weekly) for efficient historical trend analysis.

    Note: This table is designed for TimescaleDB hypertable conversion.
    See Alembic migration for hypertable setup with retention policies.
    """

    __tablename__ = "performance_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    team_instance_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("team_instances.id"),
        nullable=False,
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    period: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )  # hourly, daily, weekly
    pnl: Mapped[Decimal] = mapped_column(
        Numeric(precision=18, scale=2),
        nullable=False,
    )
    pnl_percent: Mapped[float] = mapped_column(Float, nullable=False)
    win_rate: Mapped[float] = mapped_column(Float, nullable=False)
    sharpe_ratio: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_drawdown: Mapped[float] = mapped_column(Float, nullable=False)
    trade_count: Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (
        Index("ix_performance_metrics_team_instance_id", "team_instance_id"),
        Index("ix_performance_metrics_timestamp", "timestamp"),
        Index("ix_performance_metrics_period", "period"),
        Index("ix_performance_metrics_composite", "team_instance_id", "period", "timestamp"),
    )

    def __repr__(self) -> str:
        return (
            f"<PerformanceMetric(id={self.id}, team_id={self.team_instance_id}, "
            f"period={self.period!r}, timestamp={self.timestamp})>"
        )
