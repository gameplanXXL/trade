"""Paper Trading Engine for simulated trading without real money."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING

import structlog
from pydantic import BaseModel, Field

from src.core.exceptions import TradingError
from src.mt5.market_data import MarketDataFeed, canonicalize_symbol
from src.mt5.orders import OrderRequest, OrderResult, OrderSide, OrderStatus, OrderType

if TYPE_CHECKING:
    from src.services.budget_manager import BudgetManager

log = structlog.get_logger()


class PaperTradingError(TradingError):
    """Paper trading specific error."""

    code = "PAPER_TRADING_ERROR"


class PositionUpdateType(str, Enum):
    """Type of position update."""

    PRICE_UPDATE = "price_update"
    STOP_LOSS_HIT = "stop_loss_hit"
    TAKE_PROFIT_HIT = "take_profit_hit"
    TRAILING_SL_UPDATED = "trailing_sl_updated"


class PaperPosition(BaseModel):
    """Virtual paper trading position."""

    ticket: int = Field(..., description="Position ticket ID")
    symbol: str = Field(..., description="Symbol in canonical format")
    side: OrderSide = Field(..., description="Position side (BUY/SELL)")
    volume: Decimal = Field(..., description="Position volume in lots")
    entry_price: Decimal = Field(..., description="Entry price (with spread)")
    current_price: Decimal = Field(..., description="Current market price")
    stop_loss: Decimal | None = Field(default=None, description="Stop loss price")
    take_profit: Decimal | None = Field(default=None, description="Take profit price")
    trailing_stop_pct: Decimal | None = Field(default=None, description="Trailing stop %")
    unrealized_pnl: Decimal = Field(default=Decimal("0"), description="Unrealized P/L")
    realized_pnl: Decimal = Field(default=Decimal("0"), description="Realized P/L (if closed)")
    spread_cost: Decimal = Field(default=Decimal("0"), description="Spread cost at entry")
    is_open: bool = Field(default=True, description="Position is open")
    opened_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    closed_at: datetime | None = Field(default=None, description="Close timestamp")
    magic_number: int = Field(default=0, description="Magic number for identification")

    def calculate_pnl(self, current_price: Decimal) -> Decimal:
        """Calculate unrealized P/L based on current price.

        For forex: P/L = (exit - entry) * volume * 100000 for BUY
                   P/L = (entry - exit) * volume * 100000 for SELL
        """
        lot_size = Decimal("100000")  # Standard lot

        if self.side == OrderSide.BUY:
            pnl = (current_price - self.entry_price) * self.volume * lot_size
        else:
            pnl = (self.entry_price - current_price) * self.volume * lot_size

        return pnl.quantize(Decimal("0.01"))


class PositionUpdate(BaseModel):
    """Result of a position update."""

    ticket: int = Field(..., description="Position ticket")
    symbol: str = Field(..., description="Symbol")
    update_type: PositionUpdateType = Field(..., description="Type of update")
    previous_price: Decimal = Field(..., description="Previous price")
    current_price: Decimal = Field(..., description="Current price")
    previous_pnl: Decimal = Field(..., description="Previous P/L")
    current_pnl: Decimal = Field(..., description="Current P/L")
    stop_loss_triggered: bool = Field(default=False, description="SL was triggered")
    take_profit_triggered: bool = Field(default=False, description="TP was triggered")
    new_stop_loss: Decimal | None = Field(default=None, description="Updated SL (if trailing)")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class PaperTradingEngine:
    """Paper Trading Engine for simulated order execution.

    Simulates realistic trading without real money, including:
    - Budget validation
    - Spread-based execution
    - Trailing stop loss
    - Position updates with current prices

    H2 fix: Optional BudgetManager integration for DB persistence.
    """

    def __init__(
        self,
        market_data: MarketDataFeed,
        default_spread_pips: Decimal = Decimal("2"),
        update_interval: float = 5.0,
        budget_manager: BudgetManager | None = None,
    ) -> None:
        """Initialize Paper Trading Engine.

        Args:
            market_data: Market data feed for price updates
            default_spread_pips: Default spread in pips if not from market
            update_interval: Position update interval in seconds
            budget_manager: Optional BudgetManager for DB persistence (H2 fix)
        """
        self.market_data = market_data
        self.default_spread_pips = default_spread_pips
        self.update_interval = update_interval
        self.budget_manager = budget_manager
        self.positions: dict[int, PaperPosition] = {}
        self._ticket_counter = 0
        self._update_task: asyncio.Task | None = None
        self._running = False
        # Track trade IDs for positions (ticket -> trade.id mapping)
        self._trade_ids: dict[int, int] = {}

    async def execute_order(
        self,
        order: OrderRequest,
        budget: Decimal,
        team_instance_id: int | None = None,
    ) -> OrderResult:
        """Execute a simulated order.

        Args:
            order: Order request details
            budget: Available budget for the trade
            team_instance_id: Optional team instance ID for tracking

        Returns:
            OrderResult with execution details

        Raises:
            PaperTradingError: If budget insufficient or execution fails
        """
        canonical_symbol = canonicalize_symbol(order.symbol)

        # Get current price
        price = await self._get_price(canonical_symbol)

        # M3 fix: Clarified spread strategy
        # Priority: 1) Use spread from market data if available and valid
        #           2) Fall back to default_spread_pips converted to price
        # This ensures realistic simulation even when market data doesn't provide spread
        if price.spread and price.spread > 0:
            spread = price.spread
        else:
            spread = self._pips_to_price(self.default_spread_pips, canonical_symbol)
            log.debug(
                "paper_trading_using_default_spread",
                symbol=canonical_symbol,
                spread_pips=str(self.default_spread_pips),
                spread_price=str(spread),
            )

        if order.order_type == OrderType.MARKET_BUY:
            fill_price = price.ask  # Buy at ask
        else:
            fill_price = price.bid  # Sell at bid

        # Calculate position value (simplified)
        position_value = order.volume * Decimal("100000") * fill_price / Decimal("100")

        # Validate budget
        if position_value > budget:
            raise PaperTradingError(
                f"Insufficient budget: need {position_value}, have {budget}",
                details={"required": str(position_value), "available": str(budget)},
            )

        # Calculate spread cost
        spread_cost = order.volume * Decimal("100000") * spread

        # Calculate initial trailing SL
        stop_loss = order.stop_loss
        if stop_loss is None and order.trailing_stop_pct:
            stop_loss = self._calculate_trailing_sl(
                fill_price,
                order.trailing_stop_pct,
                order.side,
            )

        # Create position
        self._ticket_counter += 1
        ticket = self._ticket_counter

        position = PaperPosition(
            ticket=ticket,
            symbol=canonical_symbol,
            side=order.side,
            volume=order.volume,
            entry_price=fill_price,
            current_price=fill_price,
            stop_loss=stop_loss,
            take_profit=order.take_profit,
            trailing_stop_pct=order.trailing_stop_pct,
            spread_cost=spread_cost,
            magic_number=order.magic_number,
        )

        self.positions[ticket] = position

        # H2 fix: Persist trade to database if BudgetManager is available
        if self.budget_manager and team_instance_id:
            try:
                trade = await self.budget_manager.record_trade_open(
                    team_instance_id=team_instance_id,
                    ticket=ticket,
                    symbol=canonical_symbol,
                    side=order.side.value,
                    size=order.volume,
                    entry_price=fill_price,
                    stop_loss=stop_loss,
                    take_profit=order.take_profit,
                    spread_cost=spread_cost,
                    magic_number=order.magic_number,
                    comment=f"Paper trade via PaperTradingEngine",
                )
                self._trade_ids[ticket] = trade.id
                log.info(
                    "paper_trade_persisted",
                    ticket=ticket,
                    trade_id=trade.id,
                    team_instance_id=team_instance_id,
                )
            except Exception as e:
                log.warning(
                    "paper_trade_persist_failed",
                    ticket=ticket,
                    error=str(e),
                )

        log.info(
            "paper_order_executed",
            ticket=ticket,
            symbol=canonical_symbol,
            side=order.side.value,
            volume=str(order.volume),
            fill_price=str(fill_price),
            spread_cost=str(spread_cost),
            stop_loss=str(stop_loss) if stop_loss else None,
        )

        return OrderResult(
            ticket=ticket,
            symbol=canonical_symbol,
            order_type=order.order_type,
            volume=order.volume,
            price=fill_price,
            stop_loss=stop_loss,
            take_profit=order.take_profit,
            status=OrderStatus.FILLED,
            comment=f"Paper trade executed, spread cost: {spread_cost}",
        )

    async def update_positions(self) -> list[PositionUpdate]:
        """Update all open positions with current prices.

        Checks for:
        - Price changes
        - Stop loss triggers
        - Take profit triggers
        - Trailing stop updates

        Returns:
            List of position updates
        """
        updates: list[PositionUpdate] = []

        for ticket, position in list(self.positions.items()):
            if not position.is_open:
                continue

            try:
                price = await self._get_price(position.symbol)
                current_price = price.mid

                # Store previous values
                previous_price = position.current_price
                previous_pnl = position.unrealized_pnl

                # Update current price and P/L
                position.current_price = current_price
                position.unrealized_pnl = position.calculate_pnl(current_price)

                # Check stop loss
                sl_triggered = False
                if position.stop_loss:
                    if position.side == OrderSide.BUY and current_price <= position.stop_loss:
                        sl_triggered = True
                    elif position.side == OrderSide.SELL and current_price >= position.stop_loss:
                        sl_triggered = True

                # Check take profit
                tp_triggered = False
                if position.take_profit:
                    if position.side == OrderSide.BUY and current_price >= position.take_profit:
                        tp_triggered = True
                    elif position.side == OrderSide.SELL and current_price <= position.take_profit:
                        tp_triggered = True

                # Update trailing stop
                new_sl = None
                if position.trailing_stop_pct and position.stop_loss and not sl_triggered:
                    new_sl = self._update_trailing_sl(position, current_price)

                # Determine update type
                if sl_triggered:
                    update_type = PositionUpdateType.STOP_LOSS_HIT
                    await self._close_position_internal(position, current_price)
                elif tp_triggered:
                    update_type = PositionUpdateType.TAKE_PROFIT_HIT
                    await self._close_position_internal(position, current_price)
                elif new_sl:
                    update_type = PositionUpdateType.TRAILING_SL_UPDATED
                else:
                    update_type = PositionUpdateType.PRICE_UPDATE

                update = PositionUpdate(
                    ticket=ticket,
                    symbol=position.symbol,
                    update_type=update_type,
                    previous_price=previous_price,
                    current_price=current_price,
                    previous_pnl=previous_pnl,
                    current_pnl=position.unrealized_pnl,
                    stop_loss_triggered=sl_triggered,
                    take_profit_triggered=tp_triggered,
                    new_stop_loss=new_sl,
                )
                updates.append(update)

                if sl_triggered or tp_triggered:
                    log.info(
                        "paper_position_auto_closed",
                        ticket=ticket,
                        reason="stop_loss" if sl_triggered else "take_profit",
                        pnl=str(position.realized_pnl),
                    )

            except Exception as e:
                log.warning(
                    "position_update_failed",
                    ticket=ticket,
                    error=str(e),
                )

        return updates

    async def close_position(self, ticket: int) -> OrderResult:
        """Close a paper position.

        Args:
            ticket: Position ticket ID

        Returns:
            OrderResult with close details

        Raises:
            PaperTradingError: If position not found
        """
        if ticket not in self.positions:
            raise PaperTradingError(
                f"Position {ticket} not found",
                details={"ticket": ticket},
            )

        position = self.positions[ticket]
        if not position.is_open:
            raise PaperTradingError(
                f"Position {ticket} is already closed",
                details={"ticket": ticket},
            )

        # Get current price for close
        price = await self._get_price(position.symbol)
        close_price = price.mid

        await self._close_position_internal(position, close_price)

        # Determine close order type (opposite of position)
        close_order_type = (
            OrderType.MARKET_SELL if position.side == OrderSide.BUY else OrderType.MARKET_BUY
        )

        log.info(
            "paper_position_closed",
            ticket=ticket,
            symbol=position.symbol,
            pnl=str(position.realized_pnl),
        )

        return OrderResult(
            ticket=ticket,
            symbol=position.symbol,
            order_type=close_order_type,
            volume=position.volume,
            price=close_price,
            status=OrderStatus.FILLED,
            comment=f"Paper position closed, P/L: {position.realized_pnl}",
        )

    def get_equity(self, current_prices: dict[str, Decimal] | None = None) -> Decimal:
        """Calculate total equity (unrealized P/L) of all positions.

        Args:
            current_prices: Optional dict of symbol -> price for calculation

        Returns:
            Total equity (sum of all unrealized P/L)
        """
        total_equity = Decimal("0")

        for position in self.positions.values():
            if not position.is_open:
                continue

            if current_prices and position.symbol in current_prices:
                pnl = position.calculate_pnl(current_prices[position.symbol])
            else:
                pnl = position.unrealized_pnl

            total_equity += pnl

        return total_equity.quantize(Decimal("0.01"))

    def get_open_positions(self) -> list[PaperPosition]:
        """Get all open positions.

        Returns:
            List of open PaperPositions
        """
        return [p for p in self.positions.values() if p.is_open]

    def get_position(self, ticket: int) -> PaperPosition | None:
        """Get a specific position by ticket.

        Args:
            ticket: Position ticket ID

        Returns:
            PaperPosition or None
        """
        return self.positions.get(ticket)

    async def start_update_loop(self) -> None:
        """Start the position update loop."""
        self._running = True
        self._update_task = asyncio.create_task(self._update_loop())
        log.info("paper_trading_update_loop_started", interval=self.update_interval)

    async def stop_update_loop(self) -> None:
        """Stop the position update loop."""
        self._running = False
        if self._update_task:
            self._update_task.cancel()
            try:
                await self._update_task
            except asyncio.CancelledError:
                pass
            self._update_task = None
        log.info("paper_trading_update_loop_stopped")

    async def _update_loop(self) -> None:
        """Internal update loop."""
        while self._running:
            try:
                await asyncio.sleep(self.update_interval)
                if self._running:
                    await self.update_positions()
            except asyncio.CancelledError:
                break
            except Exception as e:
                log.error("paper_trading_update_error", error=str(e))

    async def _close_position_internal(
        self,
        position: PaperPosition,
        close_price: Decimal,
    ) -> None:
        """Internal method to close a position.

        H2 fix: Also updates trade in database via BudgetManager.
        """
        position.current_price = close_price
        position.realized_pnl = position.calculate_pnl(close_price) - position.spread_cost
        position.unrealized_pnl = Decimal("0")
        position.is_open = False
        position.closed_at = datetime.now(UTC)

        # H2 fix: Persist trade close to database if BudgetManager is available
        if self.budget_manager and position.ticket in self._trade_ids:
            try:
                trade_id = self._trade_ids[position.ticket]
                await self.budget_manager.record_trade_close(
                    trade_id=trade_id,
                    exit_price=close_price,
                    pnl=position.realized_pnl,
                )
                del self._trade_ids[position.ticket]
                log.info(
                    "paper_trade_close_persisted",
                    ticket=position.ticket,
                    trade_id=trade_id,
                    pnl=str(position.realized_pnl),
                )
            except Exception as e:
                log.warning(
                    "paper_trade_close_persist_failed",
                    ticket=position.ticket,
                    error=str(e),
                )

    async def _get_price(self, symbol: str):
        """Get current price from market data."""
        # Try to get from last known price first
        last = self.market_data.get_last_price(symbol)
        if last:
            return last

        # Otherwise fetch fresh
        return await self.market_data.get_current_price(symbol)

    def _calculate_trailing_sl(
        self,
        price: Decimal,
        trailing_pct: Decimal,
        side: OrderSide,
    ) -> Decimal:
        """Calculate initial trailing stop loss."""
        offset = price * trailing_pct / 100

        if side == OrderSide.BUY:
            return price - offset
        return price + offset

    def _update_trailing_sl(
        self,
        position: PaperPosition,
        current_price: Decimal,
    ) -> Decimal | None:
        """Update trailing stop loss if price moved favorably.

        Returns new SL if updated, None otherwise.
        """
        if not position.trailing_stop_pct or not position.stop_loss:
            return None

        offset = current_price * position.trailing_stop_pct / 100

        if position.side == OrderSide.BUY:
            new_sl = current_price - offset
            if new_sl > position.stop_loss:
                position.stop_loss = new_sl
                return new_sl
        else:
            new_sl = current_price + offset
            if new_sl < position.stop_loss:
                position.stop_loss = new_sl
                return new_sl

        return None

    def _pips_to_price(self, pips: Decimal, symbol: str) -> Decimal:
        """Convert pips to price value.

        For JPY pairs: 1 pip = 0.01
        For others: 1 pip = 0.0001
        """
        if "JPY" in symbol.upper():
            return pips * Decimal("0.01")
        return pips * Decimal("0.0001")
