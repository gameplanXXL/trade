"""Analytics API schemas."""

from decimal import Decimal

from pydantic import BaseModel, Field
from pydantic.functional_serializers import PlainSerializer
from typing_extensions import Annotated


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
