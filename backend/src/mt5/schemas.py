"""Pydantic schemas for MT5 integration."""

from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field


class MT5Settings(BaseModel):
    """MT5 connection settings."""

    login: int = Field(..., description="MT5 account login number")
    password: str = Field(..., description="MT5 account password")
    server: str = Field(..., description="MT5 broker server address")
    timeout: int = Field(default=60000, description="Connection timeout in milliseconds")
    path: str | None = Field(default=None, description="Path to MT5 terminal (for Wine)")


class AccountInfo(BaseModel):
    """MT5 account information."""

    login: int = Field(..., description="Account login number")
    balance: Decimal = Field(..., description="Account balance")
    equity: Decimal = Field(..., description="Account equity")
    margin: Decimal = Field(default=Decimal("0"), description="Used margin")
    free_margin: Decimal = Field(..., description="Free margin available")
    leverage: int = Field(..., description="Account leverage")
    currency: str = Field(default="USD", description="Account currency")
    server: str = Field(..., description="Connected server")
    trade_allowed: bool = Field(default=True, description="Trading is allowed")


class Price(BaseModel):
    """Current price information for a symbol."""

    symbol: str = Field(..., description="Symbol name (canonical: EUR/USD)")
    bid: Decimal = Field(..., description="Bid price")
    ask: Decimal = Field(..., description="Ask price")
    spread: Decimal = Field(..., description="Current spread in points")
    time: datetime = Field(..., description="Price timestamp")

    @property
    def mid(self) -> Decimal:
        """Calculate mid price."""
        return (self.bid + self.ask) / 2


class Timeframe(str, Enum):
    """MT5 timeframes."""

    M1 = "M1"
    M5 = "M5"
    M15 = "M15"
    M30 = "M30"
    H1 = "H1"
    H4 = "H4"
    D1 = "D1"
    W1 = "W1"
    MN1 = "MN1"


class OHLCV(BaseModel):
    """OHLCV candlestick data."""

    time: datetime = Field(..., description="Candle open time")
    open: Decimal = Field(..., description="Open price")
    high: Decimal = Field(..., description="High price")
    low: Decimal = Field(..., description="Low price")
    close: Decimal = Field(..., description="Close price")
    volume: int = Field(..., description="Tick volume")
    spread: int = Field(default=0, description="Spread in points")
