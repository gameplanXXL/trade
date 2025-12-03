"""MT5 Integration module for MetaTrader 5 connectivity."""

from src.mt5.connector import MT5Connector
from src.mt5.market_data import MarketDataFeed, canonicalize_symbol, to_mt5_symbol
from src.mt5.orders import (
    OrderError,
    OrderManager,
    OrderRequest,
    OrderResult,
    OrderSide,
    OrderStatus,
    OrderType,
    Position,
    PositionStatus,
)
from src.mt5.schemas import OHLCV, AccountInfo, MT5Settings, Price, Timeframe

__all__ = [
    "MT5Connector",
    "MT5Settings",
    "AccountInfo",
    "Price",
    "OHLCV",
    "Timeframe",
    "MarketDataFeed",
    "canonicalize_symbol",
    "to_mt5_symbol",
    "OrderManager",
    "OrderRequest",
    "OrderResult",
    "OrderSide",
    "OrderType",
    "OrderStatus",
    "Position",
    "PositionStatus",
    "OrderError",
]
