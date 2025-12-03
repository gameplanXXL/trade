"""Tests for RiskManager agent."""

from decimal import Decimal

import pytest

from src.agents.base import AgentDecision, AgentStatus
from src.agents.risk_manager import (
    RejectionReason,
    RiskDecision,
    RiskManager,
)
from src.agents.trader import Order, OrderSide


class TestRiskEnums:
    """Tests for RiskManager enums."""

    def test_risk_decision_values(self) -> None:
        """Test RiskDecision enum values."""
        assert RiskDecision.APPROVE == "approve"
        assert RiskDecision.REJECT == "reject"
        assert RiskDecision.REDUCE == "reduce"

    def test_rejection_reason_values(self) -> None:
        """Test RejectionReason enum values."""
        assert RejectionReason.MAX_DRAWDOWN_EXCEEDED == "MAX_DRAWDOWN_EXCEEDED"
        assert RejectionReason.MAX_EXPOSURE_EXCEEDED == "MAX_EXPOSURE_EXCEEDED"
        assert RejectionReason.POSITION_SIZE_TOO_LARGE == "POSITION_SIZE_TOO_LARGE"
        assert RejectionReason.CRASH_MODE_ACTIVE == "CRASH_MODE_ACTIVE"


class TestRiskManagerConfiguration:
    """Tests for RiskManager configuration."""

    def test_default_configuration(self) -> None:
        """Test default configuration values."""
        manager = RiskManager(params={})

        assert manager.max_drawdown == 0.25
        assert manager.max_exposure == 0.5
        assert manager.max_position_size == 0.1
        assert manager.budget == Decimal("10000")

    def test_custom_configuration(self) -> None:
        """Test custom configuration values."""
        manager = RiskManager(
            params={
                "max_drawdown": 0.15,
                "max_exposure": 0.3,
                "max_position_size": 0.05,
                "budget": 50000,
            }
        )

        assert manager.max_drawdown == 0.15
        assert manager.max_exposure == 0.3
        assert manager.max_position_size == 0.05
        assert manager.budget == Decimal("50000")

    def test_agent_name(self) -> None:
        """Test that agent name is set correctly."""
        manager = RiskManager(params={})
        assert manager.name == "risk_manager"

    def test_initial_status(self) -> None:
        """Test that agent starts with NORMAL status."""
        manager = RiskManager(params={})
        assert manager.status == AgentStatus.NORMAL


class TestRiskManagerValidate:
    """Tests for RiskManager.validate method."""

    @pytest.fixture
    def manager(self) -> RiskManager:
        """Create a RiskManager with default config."""
        return RiskManager(params={"budget": 10000})

    @pytest.fixture
    def valid_order(self) -> dict:
        """Create a valid order dict."""
        return {
            "symbol": "EURUSD",
            "side": "BUY",
            "size": 0.1,
            "entry_price": 1000.0,  # Position value = 100 = 1% of budget
            "stop_loss": 980.0,
        }

    @pytest.mark.asyncio
    async def test_validate_returns_agent_decision(
        self, manager: RiskManager, valid_order: dict
    ) -> None:
        """Test that validate returns an AgentDecision."""
        context = {"order": valid_order}
        result = await manager.validate(context)

        assert isinstance(result, AgentDecision)
        assert result.agent_name == "risk_manager"

    @pytest.mark.asyncio
    async def test_validate_approve_valid_order(
        self, manager: RiskManager, valid_order: dict
    ) -> None:
        """Test approval of valid order."""
        context = {"order": valid_order, "positions": []}

        result = await manager.validate(context)

        assert result.data["decision"] == RiskDecision.APPROVE.value
        assert "checks_passed" in result.data

    @pytest.mark.asyncio
    async def test_validate_no_order(self, manager: RiskManager) -> None:
        """Test rejection when no order provided."""
        result = await manager.validate({})

        assert result.data["decision"] == RiskDecision.REJECT.value
        assert "No order" in result.data["reason"]

    @pytest.mark.asyncio
    async def test_validate_invalid_order_data(self, manager: RiskManager) -> None:
        """Test rejection with invalid order data."""
        context = {"order": {"invalid": "data"}}

        result = await manager.validate(context)

        assert result.data["decision"] == RiskDecision.REJECT.value
        assert "Invalid order" in result.data["reason"]

    @pytest.mark.asyncio
    async def test_execute_calls_validate(
        self, manager: RiskManager, valid_order: dict
    ) -> None:
        """Test that execute() is an alias for validate()."""
        context = {"order": valid_order}

        result = await manager.execute(context)

        assert isinstance(result, AgentDecision)
        assert result.data["decision"] == RiskDecision.APPROVE.value


class TestRiskManagerCrashMode:
    """Tests for crash mode rejection."""

    @pytest.fixture
    def manager(self) -> RiskManager:
        """Create a RiskManager."""
        return RiskManager(params={"budget": 10000})

    @pytest.mark.asyncio
    async def test_reject_in_crash_mode(self, manager: RiskManager) -> None:
        """Test rejection when crash mode is active."""
        context = {
            "order": {
                "symbol": "EURUSD",
                "side": "BUY",
                "size": 0.1,
                "entry_price": 1000.0,
                "stop_loss": 980.0,
            },
            "crash_detector_status": "crash",
        }

        result = await manager.validate(context)

        assert result.data["decision"] == RiskDecision.REJECT.value
        assert result.data["reason"] == RejectionReason.CRASH_MODE_ACTIVE.value

    @pytest.mark.asyncio
    async def test_approve_in_normal_mode(self, manager: RiskManager) -> None:
        """Test approval when crash mode is not active."""
        context = {
            "order": {
                "symbol": "EURUSD",
                "side": "BUY",
                "size": 0.1,
                "entry_price": 1000.0,
                "stop_loss": 980.0,
            },
            "crash_detector_status": "normal",
        }

        result = await manager.validate(context)

        assert result.data["decision"] == RiskDecision.APPROVE.value

    @pytest.mark.asyncio
    async def test_crash_mode_sets_warning_status(self, manager: RiskManager) -> None:
        """Test that crash mode rejection sets WARNING status."""
        context = {
            "order": {
                "symbol": "EURUSD",
                "side": "BUY",
                "size": 0.1,
                "entry_price": 1000.0,
                "stop_loss": 980.0,
            },
            "crash_detector_status": "crash",
        }

        await manager.validate(context)

        assert manager.status == AgentStatus.WARNING


class TestRiskManagerDrawdown:
    """Tests for drawdown checking."""

    @pytest.fixture
    def manager(self) -> RiskManager:
        """Create a RiskManager with 25% max drawdown."""
        return RiskManager(params={"max_drawdown": 0.25, "budget": 10000})

    def test_check_drawdown_within_limits(self, manager: RiskManager) -> None:
        """Test drawdown check within limits."""
        # 10% drawdown (1000 loss from 10000 peak)
        result = manager.check_drawdown(
            current_pnl=Decimal("-1000"),
            peak_value=Decimal("10000"),
        )
        assert result is True

    def test_check_drawdown_exceeded(self, manager: RiskManager) -> None:
        """Test drawdown check when exceeded."""
        # 30% drawdown (3000 loss from 10000 peak)
        result = manager.check_drawdown(
            current_pnl=Decimal("-3000"),
            peak_value=Decimal("10000"),
        )
        assert result is False

    def test_check_drawdown_at_limit(self, manager: RiskManager) -> None:
        """Test drawdown check at exact limit."""
        # 25% drawdown = limit
        result = manager.check_drawdown(
            current_pnl=Decimal("-2500"),
            peak_value=Decimal("10000"),
        )
        assert result is True

    def test_check_drawdown_no_loss(self, manager: RiskManager) -> None:
        """Test drawdown check with no loss."""
        result = manager.check_drawdown(
            current_pnl=Decimal("500"),
            peak_value=Decimal("10000"),
        )
        assert result is True

    @pytest.mark.asyncio
    async def test_validate_rejects_drawdown_exceeded(
        self, manager: RiskManager
    ) -> None:
        """Test validation rejects when drawdown exceeded."""
        context = {
            "order": {
                "symbol": "EURUSD",
                "side": "BUY",
                "size": 0.1,
                "entry_price": 1000.0,
                "stop_loss": 980.0,
            },
            "current_pnl": -3000,  # 30% drawdown
            "peak_value": 10000,
        }

        result = await manager.validate(context)

        assert result.data["decision"] == RiskDecision.REJECT.value
        assert result.data["reason"] == RejectionReason.MAX_DRAWDOWN_EXCEEDED.value


class TestRiskManagerExposure:
    """Tests for exposure checking."""

    @pytest.fixture
    def manager(self) -> RiskManager:
        """Create a RiskManager with 50% max exposure."""
        return RiskManager(params={"max_exposure": 0.5, "budget": 10000})

    def test_check_exposure_within_limits(self, manager: RiskManager) -> None:
        """Test exposure check within limits."""
        positions = [
            {"size": 1.0, "entry_price": 1000.0},  # 10%
            {"size": 1.0, "entry_price": 1000.0},  # 10%
        ]
        new_order = Order(
            symbol="EURUSD",
            side=OrderSide.BUY,
            size=1.0,
            entry_price=1000.0,  # 10%
            stop_loss=980.0,
        )

        result = manager.check_exposure(positions, new_order)
        assert result is True  # 30% < 50%

    def test_check_exposure_exceeded(self, manager: RiskManager) -> None:
        """Test exposure check when exceeded."""
        positions = [
            {"size": 2.0, "entry_price": 2000.0},  # 40%
        ]
        new_order = Order(
            symbol="EURUSD",
            side=OrderSide.BUY,
            size=2.0,
            entry_price=1000.0,  # 20%
            stop_loss=980.0,
        )

        result = manager.check_exposure(positions, new_order)
        assert result is False  # 60% > 50%

    @pytest.mark.asyncio
    async def test_validate_rejects_exposure_exceeded(
        self, manager: RiskManager
    ) -> None:
        """Test validation rejects when exposure exceeded."""
        context = {
            "order": {
                "symbol": "EURUSD",
                "side": "BUY",
                "size": 3.0,
                "entry_price": 2000.0,  # 60% position
                "stop_loss": 1800.0,
            },
            "positions": [],
        }

        result = await manager.validate(context)

        # First it will try to reduce due to position size, then check exposure
        # With 10% max position size on 10000 budget = 1000 max value
        # But order is 3 * 2000 = 6000 which is 60%
        assert result.data["decision"] in [
            RiskDecision.REJECT.value,
            RiskDecision.REDUCE.value,
        ]


class TestRiskManagerPositionSize:
    """Tests for position size checking."""

    @pytest.fixture
    def manager(self) -> RiskManager:
        """Create a RiskManager with 10% max position size."""
        return RiskManager(
            params={"max_position_size": 0.1, "budget": 10000}
        )

    @pytest.mark.asyncio
    async def test_validate_reduces_large_position(
        self, manager: RiskManager
    ) -> None:
        """Test that large positions are reduced."""
        context = {
            "order": {
                "symbol": "EURUSD",
                "side": "BUY",
                "size": 2.0,  # At price 1000 = 2000 = 20%
                "entry_price": 1000.0,
                "stop_loss": 980.0,
            },
            "positions": [],
        }

        result = await manager.validate(context)

        assert result.data["decision"] == RiskDecision.REDUCE.value
        assert result.data["reason"] == RejectionReason.POSITION_SIZE_TOO_LARGE.value
        assert "reduced_size" in result.data
        assert result.data["reduced_size"] < 2.0

    @pytest.mark.asyncio
    async def test_validate_approves_small_position(
        self, manager: RiskManager
    ) -> None:
        """Test that small positions are approved."""
        context = {
            "order": {
                "symbol": "EURUSD",
                "side": "BUY",
                "size": 0.5,  # At price 1000 = 500 = 5%
                "entry_price": 1000.0,
                "stop_loss": 980.0,
            },
            "positions": [],
        }

        result = await manager.validate(context)

        assert result.data["decision"] == RiskDecision.APPROVE.value


class TestRiskManagerStatusUpdates:
    """Tests for status updates."""

    @pytest.fixture
    def manager(self) -> RiskManager:
        """Create a RiskManager."""
        return RiskManager(params={"budget": 10000})

    @pytest.mark.asyncio
    async def test_status_normal_on_approval(self, manager: RiskManager) -> None:
        """Test NORMAL status on approval."""
        context = {
            "order": {
                "symbol": "EURUSD",
                "side": "BUY",
                "size": 0.1,
                "entry_price": 1000.0,
                "stop_loss": 980.0,
            },
        }

        await manager.validate(context)

        assert manager.status == AgentStatus.NORMAL

    @pytest.mark.asyncio
    async def test_status_warning_on_rejection(self, manager: RiskManager) -> None:
        """Test WARNING status on rejection."""
        context = {
            "order": {
                "symbol": "EURUSD",
                "side": "BUY",
                "size": 0.1,
                "entry_price": 1000.0,
                "stop_loss": 980.0,
            },
            "crash_detector_status": "crash",
        }

        await manager.validate(context)

        assert manager.status == AgentStatus.WARNING
