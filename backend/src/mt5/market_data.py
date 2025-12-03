"""Market Data Feed for real-time price data from MT5."""

import asyncio
from collections.abc import Callable
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

import structlog

from src.core.exceptions import MT5ConnectionError
from src.mt5.connector import MT5Connector
from src.mt5.schemas import OHLCV, Price, Timeframe

log = structlog.get_logger()


def canonicalize_symbol(symbol: str) -> str:
    """Convert MT5 symbol to canonical format.

    MT5 uses: EURUSD
    Canonical: EUR/USD

    Args:
        symbol: Symbol in any format

    Returns:
        Canonical symbol format (e.g., EUR/USD)
    """
    # Remove any existing slashes and spaces
    clean = symbol.replace("/", "").replace(" ", "").upper()

    # Standard forex pairs are 6 characters
    if len(clean) == 6:
        return f"{clean[:3]}/{clean[3:]}"

    # Return as-is for other instruments (indices, commodities)
    return clean


def to_mt5_symbol(symbol: str) -> str:
    """Convert canonical symbol to MT5 format.

    Canonical: EUR/USD
    MT5: EURUSD

    Args:
        symbol: Symbol in canonical format

    Returns:
        MT5 symbol format (e.g., EURUSD)
    """
    return symbol.replace("/", "").replace(" ", "").upper()


class MarketDataFeed:
    """Market data feed for real-time and historical price data.

    Provides access to current prices, historical OHLCV data, and
    real-time tick subscriptions.
    """

    def __init__(
        self,
        connector: MT5Connector,
        symbols: list[str],
        tick_interval: float = 1.0,
    ) -> None:
        """Initialize Market Data Feed.

        Args:
            connector: MT5 connector instance
            symbols: List of symbols to track (canonical format: EUR/USD)
            tick_interval: Interval between tick checks in seconds
        """
        self.connector = connector
        self.symbols = [canonicalize_symbol(s) for s in symbols]
        self.tick_interval = tick_interval
        self._callbacks: list[Callable[[Price], Any]] = []
        self._subscription_task: asyncio.Task | None = None
        self._running = False
        self._last_prices: dict[str, Price] = {}

    async def get_current_price(self, symbol: str) -> Price:
        """Get current bid/ask price for a symbol.

        Args:
            symbol: Symbol in canonical format (e.g., EUR/USD)

        Returns:
            Price object with current bid/ask

        Raises:
            MT5ConnectionError: If not connected or request fails
        """
        canonical = canonicalize_symbol(symbol)
        mt5_symbol = to_mt5_symbol(canonical)

        if not self.connector.is_connected:
            raise MT5ConnectionError(
                "Not connected to MT5",
                details={"symbol": canonical},
            )

        log.debug("fetching_price", symbol=canonical, mt5_symbol=mt5_symbol)

        # Get price from backend (mock or real)
        price_data = await self._fetch_price(mt5_symbol)

        price = Price(
            symbol=canonical,
            bid=Decimal(str(price_data["bid"])),
            ask=Decimal(str(price_data["ask"])),
            spread=Decimal(str(price_data.get("spread", 0))),
            time=price_data.get("time", datetime.now(UTC)),
        )

        self._last_prices[canonical] = price
        return price

    async def get_ohlcv(
        self,
        symbol: str,
        timeframe: str | Timeframe,
        count: int = 100,
    ) -> list[OHLCV]:
        """Get historical OHLCV candlestick data.

        Args:
            symbol: Symbol in canonical format (e.g., EUR/USD)
            timeframe: Timeframe (e.g., "M1", "H1", "D1")
            count: Number of candles to fetch

        Returns:
            List of OHLCV candles, newest first

        Raises:
            MT5ConnectionError: If not connected or request fails
        """
        canonical = canonicalize_symbol(symbol)
        mt5_symbol = to_mt5_symbol(canonical)

        if isinstance(timeframe, Timeframe):
            tf_str = timeframe.value
        else:
            tf_str = timeframe.upper()

        if not self.connector.is_connected:
            raise MT5ConnectionError(
                "Not connected to MT5",
                details={"symbol": canonical, "timeframe": tf_str},
            )

        log.debug(
            "fetching_ohlcv",
            symbol=canonical,
            timeframe=tf_str,
            count=count,
        )

        # Get OHLCV from backend (mock or real)
        ohlcv_data = await self._fetch_ohlcv(mt5_symbol, tf_str, count)

        return [
            OHLCV(
                time=candle["time"],
                open=Decimal(str(candle["open"])),
                high=Decimal(str(candle["high"])),
                low=Decimal(str(candle["low"])),
                close=Decimal(str(candle["close"])),
                volume=candle["volume"],
                spread=candle.get("spread", 0),
            )
            for candle in ohlcv_data
        ]

    async def subscribe(self, callback: Callable[[Price], Any]) -> None:
        """Start tick subscription for all configured symbols.

        The callback will be called with each new Price update.

        Args:
            callback: Async or sync function to call with Price updates
        """
        self._callbacks.append(callback)

        if not self._running:
            self._running = True
            self._subscription_task = asyncio.create_task(self._tick_loop())
            log.info(
                "market_data_subscribed",
                symbols=self.symbols,
                interval=self.tick_interval,
            )

    async def unsubscribe(self) -> None:
        """Stop tick subscription."""
        self._running = False
        self._callbacks.clear()

        if self._subscription_task:
            self._subscription_task.cancel()
            try:
                await self._subscription_task
            except asyncio.CancelledError:
                pass
            self._subscription_task = None

        log.info("market_data_unsubscribed", symbols=self.symbols)

    async def _tick_loop(self) -> None:
        """Internal loop for fetching and distributing ticks."""
        while self._running:
            try:
                for symbol in self.symbols:
                    try:
                        price = await self.get_current_price(symbol)

                        # Notify all callbacks
                        for callback in self._callbacks:
                            try:
                                result = callback(price)
                                if asyncio.iscoroutine(result):
                                    await result
                            except Exception as e:
                                log.warning(
                                    "callback_error",
                                    symbol=symbol,
                                    error=str(e),
                                )
                    except MT5ConnectionError:
                        log.warning("tick_fetch_failed", symbol=symbol)

                await asyncio.sleep(self.tick_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                log.error("tick_loop_error", error=str(e))
                await asyncio.sleep(self.tick_interval)

    async def _fetch_price(self, mt5_symbol: str) -> dict:
        """Fetch price from MT5 backend.

        This method should be overridden or the backend extended
        to provide real MT5 price data.
        """
        # Use mock data for now - will be replaced with real MT5 calls
        backend = self.connector._backend
        if hasattr(backend, "get_price"):
            return await backend.get_price(mt5_symbol)

        # Default mock price
        return {
            "bid": 1.08500,
            "ask": 1.08520,
            "spread": 20,
            "time": datetime.now(UTC),
        }

    async def _fetch_ohlcv(self, mt5_symbol: str, timeframe: str, count: int) -> list[dict]:
        """Fetch OHLCV data from MT5 backend.

        This method should be overridden or the backend extended
        to provide real MT5 OHLCV data.
        """
        # Use mock data for now - will be replaced with real MT5 calls
        backend = self.connector._backend
        if hasattr(backend, "get_ohlcv"):
            return await backend.get_ohlcv(mt5_symbol, timeframe, count)

        # Default mock OHLCV
        now = datetime.now(UTC)
        return [
            {
                "time": now,
                "open": 1.08500,
                "high": 1.08600,
                "low": 1.08400,
                "close": 1.08550,
                "volume": 1000,
                "spread": 20,
            }
        ]

    def get_last_price(self, symbol: str) -> Price | None:
        """Get the last cached price for a symbol.

        Args:
            symbol: Symbol in canonical format

        Returns:
            Last Price or None if not available
        """
        canonical = canonicalize_symbol(symbol)
        return self._last_prices.get(canonical)
