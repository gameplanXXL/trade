"""Analytics API schemas."""

from datetime import datetime
from decimal import Decimal
from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field
from pydantic.functional_serializers import PlainSerializer

# Custom serializer for Decimal to string
DecimalAsStr = Annotated[Decimal, PlainSerializer(lambda x: str(x), return_type=str)]


class PerformanceSummary(BaseModel):
    """Performance summary for a team instance.

    Contains all key metrics for evaluating team trading performance.
    """

    total_pnl: DecimalAsStr = Field(..., description="Total P/L (realized + unrealized)")
    total_pnl_percent: float = Field(..., description="Total P/L as percentage of initial budget")
    win_rate: float = Field(..., description="Percentage of winning trades")
    sharpe_ratio: float = Field(..., description="Risk-adjusted return metric")
    max_drawdown: float = Field(..., description="Maximum drawdown from peak equity")
    total_trades: int = Field(..., description="Total number of trades")
    winning_trades: int = Field(..., description="Number of profitable trades")
    losing_trades: int = Field(..., description="Number of losing trades")


class ActivitySummary(BaseModel):
    """Activity summary for agent decisions.

    Provides overview of all agent activities including signals, warnings,
    rejections, and overrides for a team instance.
    """

    total_signals: int = Field(..., description="Total number of trading signals")
    buy_signals: int = Field(..., description="Number of BUY signals")
    sell_signals: int = Field(..., description="Number of SELL signals")
    hold_signals: int = Field(..., description="Number of HOLD signals")
    warnings: int = Field(..., description="Number of warning decisions")
    rejections: int = Field(..., description="Number of rejected decisions")
    overrides: int = Field(..., description="Number of override decisions")


class PerformanceMetricResponse(BaseModel):
    """Response schema for performance metric."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Metric ID")
    team_instance_id: int = Field(..., description="Team instance ID")
    timestamp: datetime = Field(..., description="Timestamp of the metric")
    period: str = Field(..., description="Time period (hourly, daily, weekly)")
    pnl: DecimalAsStr = Field(..., description="Total P/L at this timestamp")
    pnl_percent: float = Field(..., description="P/L as percentage")
    win_rate: float = Field(..., description="Win rate at this timestamp")
    sharpe_ratio: float | None = Field(None, description="Sharpe ratio")
    max_drawdown: float = Field(..., description="Maximum drawdown")
    trade_count: int = Field(..., description="Number of trades")


class AgentDecisionResponse(BaseModel):
    """Response schema for agent decision log."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Decision ID")
    team_instance_id: int = Field(..., description="Team instance ID")
    agent_name: str = Field(..., description="Name of the agent")
    decision_type: str = Field(..., description="Type of decision")
    data: dict[str, Any] = Field(..., description="Decision data")
    confidence: float | None = Field(None, description="Confidence score")
    created_at: datetime = Field(..., description="When decision was made")
