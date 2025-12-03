"""Trader agent for order preparation and execution."""

from enum import Enum
from typing import Any

import structlog
from pydantic import BaseModel, Field

from src.agents.base import AgentDecision, AgentStatus, BaseAgent

log = structlog.get_logger()


class TraderMode(str, Enum):
    """Trading mode of the Trader agent."""

    ACTIVE = "active"
    HOLD = "hold"


class PositionSizing(str, Enum):
    """Position sizing strategy."""

    CONSERVATIVE = "conservative"  # 1% of budget per trade
    MODERATE = "moderate"  # 2% of budget per trade
    AGGRESSIVE = "aggressive"  # 5% of budget per trade


# Position sizing percentages
SIZING_PERCENTAGES = {
    PositionSizing.CONSERVATIVE: 0.01,
    PositionSizing.MODERATE: 0.02,
    PositionSizing.AGGRESSIVE: 0.05,
}


class OrderSide(str, Enum):
    """Order side."""

    BUY = "BUY"
    SELL = "SELL"


class Order(BaseModel):
    """Order to be executed."""

    symbol: str = Field(..., description="Trading symbol")
    side: OrderSide = Field(..., description="Order side (BUY/SELL)")
    size: float = Field(..., gt=0, description="Position size")
    entry_price: float = Field(..., gt=0, description="Entry price")
    stop_loss: float = Field(..., gt=0, description="Stop loss price")
    take_profit: float | None = Field(None, gt=0, description="Take profit price")
    trailing_stop_pct: float | None = Field(
        None, ge=0, le=100, description="Trailing stop percentage"
    )


class Trader(BaseAgent):
    """Trader agent for preparing and executing orders.

    Handles order preparation based on signals, position sizing,
    and order execution (paper or live trading).
    """

    name = "trader"

    def __init__(self, params: dict[str, Any]) -> None:
        """Initialize the Trader agent."""
        self.mode = TraderMode.ACTIVE
        self._pending_orders: list[Order] = []
        super().__init__(params)

    def _configure(self, params: dict[str, Any]) -> None:
        """Configure the Trader with parameters.

        Args:
            params: Configuration parameters including:
                - position_sizing: Strategy (conservative/moderate/aggressive)
                - max_positions: Maximum concurrent positions (default: 3)
                - trailing_stop_pct: Trailing stop percentage (default: 2.0)
                - budget: Trading budget (default: 10000)
        """
        sizing_str = params.get("position_sizing", "conservative")
        try:
            self.position_sizing = PositionSizing(sizing_str)
        except ValueError:
            self.position_sizing = PositionSizing.CONSERVATIVE
            log.warning(
                "invalid_position_sizing",
                provided=sizing_str,
                using="conservative",
            )

        self.max_positions = params.get("max_positions", 3)
        self.trailing_stop_pct = params.get("trailing_stop_pct", 2.0)
        self.budget = params.get("budget", 10000.0)

        log.debug(
            "trader_configured",
            position_sizing=self.position_sizing.value,
            max_positions=self.max_positions,
            trailing_stop_pct=self.trailing_stop_pct,
            budget=self.budget,
        )

    async def execute(self, context: dict[str, Any]) -> AgentDecision:
        """Execute pending orders.

        Args:
            context: Execution context containing:
                - order: Order to execute (optional, uses pending if not provided)
                - paper_trading: Whether to use paper trading (default: True)

        Returns:
            AgentDecision with execution results.
        """
        paper_trading = context.get("paper_trading", True)

        # Get order from context or use first pending order
        order_data = context.get("order")
        if order_data:
            try:
                order = Order(**order_data) if isinstance(order_data, dict) else order_data
            except Exception as e:
                return AgentDecision(
                    agent_name=self.name,
                    decision_type="rejection",
                    data={
                        "reason": f"Invalid order data: {e!s}",
                        "error": str(e),
                    },
                    confidence=0.0,
                )
        elif self._pending_orders:
            order = self._pending_orders.pop(0)
        else:
            return AgentDecision(
                agent_name=self.name,
                decision_type="action",
                data={
                    "action": "no_action",
                    "reason": "No orders to execute",
                },
                confidence=1.0,
            )

        # Check mode
        if self.mode == TraderMode.HOLD:
            # Queue order for later
            self._pending_orders.append(order)
            return AgentDecision(
                agent_name=self.name,
                decision_type="action",
                data={
                    "action": "queued",
                    "reason": "Trader in HOLD mode",
                    "order": order.model_dump(),
                    "pending_count": len(self._pending_orders),
                },
                confidence=0.5,
            )

        # Execute order (paper trading for now)
        log.info(
            "order_executed",
            agent_name=self.name,
            symbol=order.symbol,
            side=order.side.value,
            size=order.size,
            entry_price=order.entry_price,
            stop_loss=order.stop_loss,
            paper_trading=paper_trading,
        )

        return AgentDecision(
            agent_name=self.name,
            decision_type="action",
            data={
                "action": "executed",
                "order": order.model_dump(),
                "paper_trading": paper_trading,
                "mode": self.mode.value,
            },
            confidence=1.0,
        )

    async def prepare_order(self, context: dict[str, Any]) -> AgentDecision:
        """Prepare an order based on trading signal.

        Args:
            context: Execution context containing:
                - signal: Trading signal (BUY/SELL/HOLD) from analyst
                - market_data: Current market data with price info
                - confidence: Signal confidence (optional)

        Returns:
            AgentDecision with prepared order or rejection.
        """
        signal = context.get("signal", "HOLD")
        market_data = context.get("market_data", {})
        signal_confidence = context.get("confidence", 1.0)

        # Check mode
        if self.mode == TraderMode.HOLD:
            return AgentDecision(
                agent_name=self.name,
                decision_type="rejection",
                data={
                    "reason": "Trader in HOLD mode - no new orders",
                    "signal": signal,
                },
                confidence=0.0,
            )

        # HOLD signal = no order
        if signal == "HOLD":
            return AgentDecision(
                agent_name=self.name,
                decision_type="action",
                data={
                    "action": "no_order",
                    "reason": "Signal is HOLD",
                },
                confidence=1.0,
            )

        # Get market data
        symbol = market_data.get("symbol", "UNKNOWN")
        current_price = market_data.get("current_price")

        if not current_price:
            return AgentDecision(
                agent_name=self.name,
                decision_type="rejection",
                data={
                    "reason": "Missing current_price in market_data",
                    "signal": signal,
                },
                confidence=0.0,
            )

        # Calculate position size
        sizing_pct = SIZING_PERCENTAGES[self.position_sizing]
        position_value = self.budget * sizing_pct
        size = position_value / current_price

        # Determine order side
        side = OrderSide.BUY if signal == "BUY" else OrderSide.SELL

        # Calculate stop loss
        if side == OrderSide.BUY:
            stop_loss = current_price * (1 - self.trailing_stop_pct / 100)
        else:
            stop_loss = current_price * (1 + self.trailing_stop_pct / 100)

        # Create order
        order = Order(
            symbol=symbol,
            side=side,
            size=round(size, 4),
            entry_price=current_price,
            stop_loss=round(stop_loss, 5),
            trailing_stop_pct=self.trailing_stop_pct,
        )

        # Add to pending orders
        self._pending_orders.append(order)

        log.info(
            "order_prepared",
            agent_name=self.name,
            symbol=symbol,
            side=side.value,
            size=order.size,
            entry_price=current_price,
            stop_loss=order.stop_loss,
            position_sizing=self.position_sizing.value,
        )

        return AgentDecision(
            agent_name=self.name,
            decision_type="action",
            data={
                "action": "order_prepared",
                "order": order.model_dump(),
                "position_sizing": self.position_sizing.value,
                "signal_confidence": signal_confidence,
            },
            confidence=signal_confidence,
        )

    async def close_all_positions(
        self, context: dict[str, Any] | None = None
    ) -> AgentDecision:
        """Emergency close all open positions.

        Args:
            context: Optional execution context (ignored, for override compatibility).

        Returns:
            AgentDecision with close action.
        """
        # Clear pending orders
        pending_count = len(self._pending_orders)
        self._pending_orders.clear()

        # Set to HOLD mode during emergency
        old_mode = self.mode
        self.mode = TraderMode.HOLD
        self.status = AgentStatus.WARNING

        log.warning(
            "emergency_close_all",
            agent_name=self.name,
            pending_orders_cleared=pending_count,
            old_mode=old_mode.value,
            new_mode=self.mode.value,
        )

        return AgentDecision(
            agent_name=self.name,
            decision_type="action",
            data={
                "action": "close_all",
                "pending_orders_cleared": pending_count,
                "mode_changed_to": self.mode.value,
                "note": "MT5 position close will be implemented in Epic 4",
            },
            confidence=1.0,
        )

    def set_mode(self, mode: TraderMode) -> None:
        """Set the trading mode.

        Args:
            mode: New trading mode (ACTIVE/HOLD).
        """
        old_mode = self.mode
        self.mode = mode

        if old_mode != mode:
            log.info(
                "trader_mode_changed",
                agent_name=self.name,
                old_mode=old_mode.value,
                new_mode=mode.value,
            )

    def get_pending_orders(self) -> list[Order]:
        """Get list of pending orders.

        Returns:
            List of pending Order objects.
        """
        return list(self._pending_orders)

    def to_dict(self) -> dict[str, Any]:
        """Serialize trader state for logging/API.

        Returns:
            Dictionary representation of trader state.
        """
        base = super().to_dict()
        base.update({
            "mode": self.mode.value,
            "position_sizing": self.position_sizing.value,
            "max_positions": self.max_positions,
            "trailing_stop_pct": self.trailing_stop_pct,
            "pending_orders": len(self._pending_orders),
        })
        return base
