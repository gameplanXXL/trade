"""Order Management with Trailing Stoploss functionality."""

import asyncio
from datetime import UTC, datetime
from decimal import Decimal
from enum import Enum

import structlog
from pydantic import BaseModel, Field

from src.core.exceptions import MT5ConnectionError, TradingError
from src.mt5.connector import MT5Connector
from src.mt5.market_data import canonicalize_symbol, to_mt5_symbol

log = structlog.get_logger()


class OrderSide(str, Enum):
    """Order side (direction)."""

    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    """Order type."""

    MARKET_BUY = "MARKET_BUY"
    MARKET_SELL = "MARKET_SELL"


class OrderStatus(str, Enum):
    """Order status."""

    PENDING = "pending"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"


class PositionStatus(str, Enum):
    """Position status."""

    OPEN = "open"
    CLOSED = "closed"


class OrderRequest(BaseModel):
    """Request to place an order."""

    symbol: str = Field(..., description="Symbol in canonical format (EUR/USD)")
    order_type: OrderType = Field(..., description="Order type (MARKET_BUY, MARKET_SELL)")
    volume: Decimal = Field(..., gt=0, description="Order volume in lots")
    stop_loss: Decimal | None = Field(default=None, description="Stop loss price")
    take_profit: Decimal | None = Field(default=None, description="Take profit price")
    trailing_stop_pct: Decimal | None = Field(
        default=None,
        ge=0,
        le=100,
        description="Trailing stop percentage (0-100)",
    )
    slippage: int = Field(default=10, ge=0, description="Maximum slippage in points")
    magic_number: int = Field(default=12345, description="Magic number for order identification")
    comment: str = Field(default="", description="Order comment")

    @property
    def side(self) -> OrderSide:
        """Get order side from order type."""
        if self.order_type == OrderType.MARKET_BUY:
            return OrderSide.BUY
        return OrderSide.SELL


class OrderResult(BaseModel):
    """Result of an order operation."""

    ticket: int = Field(..., description="Order ticket ID")
    symbol: str = Field(..., description="Symbol in canonical format")
    order_type: OrderType = Field(..., description="Order type")
    volume: Decimal = Field(..., description="Filled volume")
    price: Decimal = Field(..., description="Fill price")
    stop_loss: Decimal | None = Field(default=None, description="Stop loss price")
    take_profit: Decimal | None = Field(default=None, description="Take profit price")
    status: OrderStatus = Field(..., description="Order status")
    comment: str = Field(default="", description="Order comment or error message")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Position(BaseModel):
    """Open position information."""

    ticket: int = Field(..., description="Position ticket ID")
    symbol: str = Field(..., description="Symbol in canonical format")
    side: OrderSide = Field(..., description="Position side (BUY/SELL)")
    volume: Decimal = Field(..., description="Position volume in lots")
    entry_price: Decimal = Field(..., description="Entry price")
    current_price: Decimal = Field(..., description="Current market price")
    stop_loss: Decimal | None = Field(default=None, description="Stop loss price")
    take_profit: Decimal | None = Field(default=None, description="Take profit price")
    profit: Decimal = Field(default=Decimal("0"), description="Unrealized P/L")
    status: PositionStatus = Field(default=PositionStatus.OPEN, description="Position status")
    opened_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    magic_number: int = Field(default=0, description="Magic number")


class OrderError(TradingError):
    """Order-related error."""

    code = "ORDER_ERROR"


class OrderManager:
    """Order Manager with trailing stoploss functionality.

    Handles order placement, modification, and position management
    with automatic trailing stoploss updates.
    """

    def __init__(
        self,
        connector: MT5Connector,
        default_trailing_stop_pct: Decimal = Decimal("1.0"),
    ) -> None:
        """Initialize Order Manager.

        Args:
            connector: MT5 connector instance
            default_trailing_stop_pct: Default trailing stop percentage
        """
        self.connector = connector
        self.default_trailing_stop_pct = default_trailing_stop_pct
        self._positions: dict[int, Position] = {}
        self._ticket_counter = 0
        self._trailing_task: asyncio.Task | None = None
        self._running = False

    async def place_order(self, order: OrderRequest) -> OrderResult:
        """Place an order with automatic trailing stoploss.

        Args:
            order: Order request details

        Returns:
            OrderResult with ticket_id and status

        Raises:
            MT5ConnectionError: If not connected
            OrderError: If order fails
        """
        if not self.connector.is_connected:
            raise MT5ConnectionError(
                "Not connected to MT5",
                details={"symbol": order.symbol},
            )

        canonical_symbol = canonicalize_symbol(order.symbol)
        mt5_symbol = to_mt5_symbol(canonical_symbol)

        log.info(
            "placing_order",
            symbol=canonical_symbol,
            order_type=order.order_type.value,
            volume=str(order.volume),
        )

        # Get current price for fill simulation
        fill_price = await self._get_fill_price(mt5_symbol, order.order_type)

        # Calculate initial trailing stop loss
        trailing_pct = order.trailing_stop_pct or self.default_trailing_stop_pct
        stop_loss = order.stop_loss
        if stop_loss is None and trailing_pct > 0:
            stop_loss = self._calculate_trailing_sl(
                fill_price,
                trailing_pct,
                order.side,
            )

        # Execute order via backend
        self._ticket_counter += 1
        ticket = self._ticket_counter

        result = OrderResult(
            ticket=ticket,
            symbol=canonical_symbol,
            order_type=order.order_type,
            volume=order.volume,
            price=fill_price,
            stop_loss=stop_loss,
            take_profit=order.take_profit,
            status=OrderStatus.FILLED,
            comment=order.comment,
        )

        # Track position
        position = Position(
            ticket=ticket,
            symbol=canonical_symbol,
            side=order.side,
            volume=order.volume,
            entry_price=fill_price,
            current_price=fill_price,
            stop_loss=stop_loss,
            take_profit=order.take_profit,
            profit=Decimal("0"),
            magic_number=order.magic_number,
        )
        self._positions[ticket] = position

        log.info(
            "order_filled",
            ticket=ticket,
            symbol=canonical_symbol,
            price=str(fill_price),
            stop_loss=str(stop_loss) if stop_loss else None,
        )

        return result

    async def modify_order(self, ticket: int, stop_loss: Decimal) -> bool:
        """Modify an existing order's stop loss.

        Args:
            ticket: Order ticket ID
            stop_loss: New stop loss price

        Returns:
            True if modification successful

        Raises:
            OrderError: If position not found
        """
        if ticket not in self._positions:
            raise OrderError(
                f"Position {ticket} not found",
                details={"ticket": ticket},
            )

        position = self._positions[ticket]
        old_sl = position.stop_loss
        position.stop_loss = stop_loss

        log.info(
            "order_modified",
            ticket=ticket,
            old_stop_loss=str(old_sl) if old_sl else None,
            new_stop_loss=str(stop_loss),
        )

        return True

    async def close_position(self, ticket: int) -> OrderResult:
        """Close a position.

        Args:
            ticket: Position ticket ID

        Returns:
            OrderResult with close details

        Raises:
            OrderError: If position not found
        """
        if ticket not in self._positions:
            raise OrderError(
                f"Position {ticket} not found",
                details={"ticket": ticket},
            )

        position = self._positions[ticket]
        mt5_symbol = to_mt5_symbol(position.symbol)

        # Get close price
        close_order_type = (
            OrderType.MARKET_SELL if position.side == OrderSide.BUY else OrderType.MARKET_BUY
        )
        close_price = await self._get_fill_price(mt5_symbol, close_order_type)

        # Calculate P/L
        if position.side == OrderSide.BUY:
            profit = (close_price - position.entry_price) * position.volume * Decimal("100000")
        else:
            profit = (position.entry_price - close_price) * position.volume * Decimal("100000")

        position.status = PositionStatus.CLOSED
        position.current_price = close_price
        position.profit = profit

        # Remove from active positions
        del self._positions[ticket]

        log.info(
            "position_closed",
            ticket=ticket,
            symbol=position.symbol,
            entry_price=str(position.entry_price),
            close_price=str(close_price),
            profit=str(profit),
        )

        return OrderResult(
            ticket=ticket,
            symbol=position.symbol,
            order_type=close_order_type,
            volume=position.volume,
            price=close_price,
            status=OrderStatus.FILLED,
            comment=f"Closed with P/L: {profit}",
        )

    async def close_all_positions(self, symbol: str | None = None) -> list[OrderResult]:
        """Close all positions, optionally filtered by symbol.

        Args:
            symbol: Optional symbol to filter (canonical format)

        Returns:
            List of OrderResults for closed positions
        """
        results: list[OrderResult] = []
        tickets_to_close = list(self._positions.keys())

        for ticket in tickets_to_close:
            position = self._positions.get(ticket)
            if position is None:
                continue

            if symbol is not None:
                canonical = canonicalize_symbol(symbol)
                if position.symbol != canonical:
                    continue

            try:
                result = await self.close_position(ticket)
                results.append(result)
            except OrderError as e:
                log.warning("close_position_failed", ticket=ticket, error=str(e))

        log.info(
            "closed_all_positions",
            count=len(results),
            symbol=symbol,
        )

        return results

    async def get_open_positions(self) -> list[Position]:
        """Get all open positions.

        Returns:
            List of open positions
        """
        return list(self._positions.values())

    async def update_trailing_stops(self, prices: dict[str, Decimal]) -> None:
        """Update trailing stop losses based on current prices.

        Args:
            prices: Dict of symbol -> current price
        """
        for position in self._positions.values():
            if position.stop_loss is None:
                continue

            current_price = prices.get(position.symbol)
            if current_price is None:
                continue

            position.current_price = current_price

            # Calculate new trailing SL
            # For BUY: SL follows price up
            # For SELL: SL follows price down
            if position.side == OrderSide.BUY:
                # Price went up, move SL up
                new_sl = current_price * (1 - self.default_trailing_stop_pct / 100)
                if new_sl > position.stop_loss:
                    old_sl = position.stop_loss
                    position.stop_loss = new_sl
                    log.debug(
                        "trailing_sl_updated",
                        ticket=position.ticket,
                        old_sl=str(old_sl),
                        new_sl=str(new_sl),
                    )
            else:
                # Price went down, move SL down
                new_sl = current_price * (1 + self.default_trailing_stop_pct / 100)
                if new_sl < position.stop_loss:
                    old_sl = position.stop_loss
                    position.stop_loss = new_sl
                    log.debug(
                        "trailing_sl_updated",
                        ticket=position.ticket,
                        old_sl=str(old_sl),
                        new_sl=str(new_sl),
                    )

            # Check if SL hit
            if position.side == OrderSide.BUY and current_price <= position.stop_loss:
                log.warning(
                    "stop_loss_triggered",
                    ticket=position.ticket,
                    price=str(current_price),
                    stop_loss=str(position.stop_loss),
                )
            elif position.side == OrderSide.SELL and current_price >= position.stop_loss:
                log.warning(
                    "stop_loss_triggered",
                    ticket=position.ticket,
                    price=str(current_price),
                    stop_loss=str(position.stop_loss),
                )

    async def start_trailing_monitor(self, interval: float = 1.0) -> None:
        """Start trailing stop loss monitoring.

        Args:
            interval: Check interval in seconds
        """
        self._running = True
        self._trailing_task = asyncio.create_task(self._trailing_loop(interval))
        log.info("trailing_monitor_started", interval=interval)

    async def stop_trailing_monitor(self) -> None:
        """Stop trailing stop loss monitoring."""
        self._running = False
        if self._trailing_task:
            self._trailing_task.cancel()
            try:
                await self._trailing_task
            except asyncio.CancelledError:
                pass
            self._trailing_task = None
        log.info("trailing_monitor_stopped")

    async def _trailing_loop(self, interval: float) -> None:
        """Internal trailing stop monitoring loop."""
        while self._running:
            try:
                # This would normally fetch prices from market data
                # For now, positions track their own current_price
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break

    async def _get_fill_price(self, mt5_symbol: str, order_type: OrderType) -> Decimal:
        """Get fill price for order type.

        For BUY: use ask price
        For SELL: use bid price
        """
        backend = self.connector._backend
        if hasattr(backend, "get_price"):
            price_data = await backend.get_price(mt5_symbol)
            if order_type in (OrderType.MARKET_BUY,):
                return Decimal(str(price_data["ask"]))
            return Decimal(str(price_data["bid"]))

        # Default mock prices
        if order_type in (OrderType.MARKET_BUY,):
            return Decimal("1.08520")  # Ask
        return Decimal("1.08500")  # Bid

    def _calculate_trailing_sl(
        self,
        price: Decimal,
        trailing_pct: Decimal,
        side: OrderSide,
    ) -> Decimal:
        """Calculate initial trailing stop loss.

        For BUY: SL = price - (price * pct / 100)
        For SELL: SL = price + (price * pct / 100)
        """
        offset = price * trailing_pct / 100

        if side == OrderSide.BUY:
            return price - offset
        return price + offset
