"""Trade API schemas for request/response models - Story 008-02."""

from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class TradeResponse(BaseModel):
    """Response schema for trade details."""

    id: int
    team_instance_id: int
    ticket: int
    symbol: str
    side: str  # BUY, SELL
    size: Decimal
    entry_price: Decimal
    exit_price: Decimal | None
    stop_loss: Decimal | None
    take_profit: Decimal | None
    pnl: Decimal | None
    spread_cost: Decimal
    status: str  # open, closed
    opened_at: datetime
    closed_at: datetime | None
    magic_number: int
    comment: str | None

    model_config = ConfigDict(from_attributes=True)


class TradeListResponse(BaseModel):
    """Response schema for paginated list of trades."""

    data: list[TradeResponse]
    meta: dict[str, Any] = Field(
        default_factory=lambda: {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "total": 0,
            "page": 1,
            "page_size": 20,
        }
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "data": [
                    {
                        "id": 1,
                        "team_instance_id": 1,
                        "ticket": 123456,
                        "symbol": "EUR/USD",
                        "side": "BUY",
                        "size": 0.1,
                        "entry_price": 1.0850,
                        "exit_price": 1.0875,
                        "stop_loss": 1.0800,
                        "take_profit": 1.0900,
                        "pnl": 25.00,
                        "spread_cost": 2.00,
                        "status": "closed",
                        "opened_at": "2025-12-01T10:00:00Z",
                        "closed_at": "2025-12-01T11:30:00Z",
                        "magic_number": 100,
                        "comment": "LLM decision",
                    }
                ],
                "meta": {
                    "timestamp": "2025-12-01T12:00:00Z",
                    "total": 42,
                    "page": 1,
                    "page_size": 20,
                },
            }
        }
    )
