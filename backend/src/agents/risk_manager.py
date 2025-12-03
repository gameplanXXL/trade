"""RiskManager agent for order validation."""

from decimal import Decimal
from enum import Enum
from typing import Any

import structlog

from src.agents.base import AgentDecision, AgentStatus, BaseAgent
from src.agents.trader import Order

log = structlog.get_logger()


class RiskDecision(str, Enum):
    """Risk validation decision."""

    APPROVE = "approve"
    REJECT = "reject"
    REDUCE = "reduce"


class RejectionReason(str, Enum):
    """Reasons for order rejection."""

    MAX_DRAWDOWN_EXCEEDED = "MAX_DRAWDOWN_EXCEEDED"
    MAX_EXPOSURE_EXCEEDED = "MAX_EXPOSURE_EXCEEDED"
    POSITION_SIZE_TOO_LARGE = "POSITION_SIZE_TOO_LARGE"
    CRASH_MODE_ACTIVE = "CRASH_MODE_ACTIVE"


class RiskManager(BaseAgent):
    """RiskManager agent for validating orders against risk rules.

    Evaluates orders against drawdown limits, exposure limits,
    and position size constraints before execution.
    """

    name = "risk_manager"

    def _configure(self, params: dict[str, Any]) -> None:
        """Configure the RiskManager with parameters.

        Args:
            params: Configuration parameters including:
                - max_drawdown: Maximum allowed drawdown (default: 0.25 = 25%)
                - max_exposure: Maximum total exposure (default: 0.5 = 50%)
                - max_position_size: Max single position size (default: 0.1 = 10%)
                - budget: Trading budget for calculations (default: 10000)
        """
        self.max_drawdown = params.get("max_drawdown", 0.25)
        self.max_exposure = params.get("max_exposure", 0.5)
        self.max_position_size = params.get("max_position_size", 0.1)
        self.budget = Decimal(str(params.get("budget", 10000)))

        log.debug(
            "risk_manager_configured",
            max_drawdown=self.max_drawdown,
            max_exposure=self.max_exposure,
            max_position_size=self.max_position_size,
            budget=float(self.budget),
        )

    async def execute(self, context: dict[str, Any]) -> AgentDecision:
        """Execute risk validation.

        Alias for validate() to satisfy BaseAgent interface.

        Args:
            context: Execution context with order and portfolio data.

        Returns:
            AgentDecision with validation results.
        """
        return await self.validate(context)

    async def validate(self, context: dict[str, Any]) -> AgentDecision:
        """Validate an order against risk rules.

        Args:
            context: Execution context containing:
                - order: Order to validate (dict or Order object)
                - current_pnl: Current profit/loss
                - peak_value: Peak portfolio value
                - positions: List of current positions
                - crash_detector_status: Status from CrashDetector

        Returns:
            AgentDecision with APPROVE, REJECT, or REDUCE decision.
        """
        # Extract context data
        order_data = context.get("order")
        current_pnl = Decimal(str(context.get("current_pnl", 0)))
        peak_value = Decimal(str(context.get("peak_value", self.budget)))
        positions = context.get("positions", [])
        crash_status = context.get("crash_detector_status", "normal")

        # Parse order
        if order_data is None:
            return AgentDecision(
                agent_name=self.name,
                decision_type="rejection",
                data={
                    "decision": RiskDecision.REJECT.value,
                    "reason": "No order provided for validation",
                },
                confidence=1.0,
            )

        try:
            order = Order(**order_data) if isinstance(order_data, dict) else order_data
        except Exception as e:
            return AgentDecision(
                agent_name=self.name,
                decision_type="rejection",
                data={
                    "decision": RiskDecision.REJECT.value,
                    "reason": f"Invalid order data: {e!s}",
                },
                confidence=1.0,
            )

        # Check crash mode
        if crash_status == "crash":
            self.status = AgentStatus.WARNING
            log.warning(
                "order_rejected_crash_mode",
                agent_name=self.name,
                reason=RejectionReason.CRASH_MODE_ACTIVE.value,
            )
            return AgentDecision(
                agent_name=self.name,
                decision_type="rejection",
                data={
                    "decision": RiskDecision.REJECT.value,
                    "reason": RejectionReason.CRASH_MODE_ACTIVE.value,
                    "crash_status": crash_status,
                },
                confidence=1.0,
            )

        # Check drawdown
        if not self.check_drawdown(current_pnl, peak_value):
            self.status = AgentStatus.WARNING
            log.warning(
                "order_rejected_drawdown",
                agent_name=self.name,
                reason=RejectionReason.MAX_DRAWDOWN_EXCEEDED.value,
                current_drawdown=self._calculate_drawdown(current_pnl, peak_value),
                max_drawdown=self.max_drawdown,
            )
            return AgentDecision(
                agent_name=self.name,
                decision_type="rejection",
                data={
                    "decision": RiskDecision.REJECT.value,
                    "reason": RejectionReason.MAX_DRAWDOWN_EXCEEDED.value,
                    "current_drawdown": float(
                        self._calculate_drawdown(current_pnl, peak_value)
                    ),
                    "max_drawdown": self.max_drawdown,
                },
                confidence=1.0,
            )

        # Check position size
        position_value = Decimal(str(order.size * order.entry_price))
        position_pct = float(position_value / self.budget)

        if position_pct > self.max_position_size:
            # Try to reduce position
            max_value = float(self.budget * Decimal(str(self.max_position_size)))
            reduced_size = round(max_value / order.entry_price, 4)

            log.info(
                "order_reduced",
                agent_name=self.name,
                reason=RejectionReason.POSITION_SIZE_TOO_LARGE.value,
                original_size=order.size,
                reduced_size=reduced_size,
            )

            return AgentDecision(
                agent_name=self.name,
                decision_type="action",
                data={
                    "decision": RiskDecision.REDUCE.value,
                    "reason": RejectionReason.POSITION_SIZE_TOO_LARGE.value,
                    "original_size": order.size,
                    "reduced_size": reduced_size,
                    "max_position_size_pct": self.max_position_size,
                    "order": order.model_dump(),
                },
                confidence=0.8,
            )

        # Check total exposure
        if not self.check_exposure(positions, order):
            self.status = AgentStatus.WARNING
            total_exposure = self._calculate_exposure(positions, order)
            log.warning(
                "order_rejected_exposure",
                agent_name=self.name,
                reason=RejectionReason.MAX_EXPOSURE_EXCEEDED.value,
                total_exposure=total_exposure,
                max_exposure=self.max_exposure,
            )
            return AgentDecision(
                agent_name=self.name,
                decision_type="rejection",
                data={
                    "decision": RiskDecision.REJECT.value,
                    "reason": RejectionReason.MAX_EXPOSURE_EXCEEDED.value,
                    "total_exposure": total_exposure,
                    "max_exposure": self.max_exposure,
                },
                confidence=1.0,
            )

        # All checks passed
        self.status = AgentStatus.NORMAL
        log.info(
            "order_approved",
            agent_name=self.name,
            symbol=order.symbol,
            size=order.size,
        )

        return AgentDecision(
            agent_name=self.name,
            decision_type="action",
            data={
                "decision": RiskDecision.APPROVE.value,
                "order": order.model_dump(),
                "checks_passed": [
                    "drawdown",
                    "exposure",
                    "position_size",
                    "crash_mode",
                ],
            },
            confidence=1.0,
        )

    def check_drawdown(self, current_pnl: Decimal, peak_value: Decimal) -> bool:
        """Check if drawdown is within limits.

        Drawdown = (Peak - Current) / Peak

        Args:
            current_pnl: Current profit/loss from peak.
            peak_value: Peak portfolio value.

        Returns:
            True if drawdown is acceptable, False if exceeded.
        """
        if peak_value <= 0:
            return True

        drawdown = self._calculate_drawdown(current_pnl, peak_value)
        return float(drawdown) <= self.max_drawdown

    def _calculate_drawdown(self, current_pnl: Decimal, peak_value: Decimal) -> Decimal:
        """Calculate current drawdown percentage.

        Args:
            current_pnl: Current profit/loss (negative = loss).
            peak_value: Peak portfolio value.

        Returns:
            Drawdown as decimal (0.25 = 25%).
        """
        if peak_value <= 0:
            return Decimal("0")

        current_value = peak_value + current_pnl
        if current_value >= peak_value:
            return Decimal("0")

        drawdown = (peak_value - current_value) / peak_value
        return drawdown

    def check_exposure(self, positions: list[dict[str, Any]], new_order: Order) -> bool:
        """Check if total exposure is within limits.

        Exposure = Sum of all position values / Budget

        Args:
            positions: List of current positions with 'size' and 'entry_price'.
            new_order: New order to add.

        Returns:
            True if exposure is acceptable, False if exceeded.
        """
        total_exposure = self._calculate_exposure(positions, new_order)
        return total_exposure <= self.max_exposure

    def _calculate_exposure(
        self, positions: list[dict[str, Any]], new_order: Order
    ) -> float:
        """Calculate total exposure including new order.

        Args:
            positions: List of current positions.
            new_order: New order to add.

        Returns:
            Total exposure as decimal (0.5 = 50%).
        """
        total_value = Decimal("0")

        # Sum existing positions
        for pos in positions:
            size = Decimal(str(pos.get("size", 0)))
            price = Decimal(str(pos.get("entry_price", 0)))
            total_value += size * price

        # Add new order
        total_value += Decimal(str(new_order.size)) * Decimal(str(new_order.entry_price))

        if self.budget <= 0:
            return 0.0

        return float(total_value / self.budget)
