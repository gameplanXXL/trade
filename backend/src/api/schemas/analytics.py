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
