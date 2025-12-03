"""Tests for Trader agent."""

import pytest

from src.agents.base import AgentDecision, AgentStatus
from src.agents.trader import (
    Order,
    OrderSide,
    PositionSizing,
    SIZING_PERCENTAGES,
    Trader,
    TraderMode,
)


class TestTraderEnums:
    """Tests for Trader enums."""

    def test_trader_mode_values(self) -> None:
        """Test TraderMode enum values."""
        assert TraderMode.ACTIVE == "active"
        assert TraderMode.HOLD == "hold"

    def test_position_sizing_values(self) -> None:
        """Test PositionSizing enum values."""
        assert PositionSizing.CONSERVATIVE == "conservative"
        assert PositionSizing.MODERATE == "moderate"
        assert PositionSizing.AGGRESSIVE == "aggressive"

    def test_sizing_percentages(self) -> None:
        """Test sizing percentages mapping."""
        assert SIZING_PERCENTAGES[PositionSizing.CONSERVATIVE] == 0.01
        assert SIZING_PERCENTAGES[PositionSizing.MODERATE] == 0.02
        assert SIZING_PERCENTAGES[PositionSizing.AGGRESSIVE] == 0.05

    def test_order_side_values(self) -> None:
        """Test OrderSide enum values."""
        assert OrderSide.BUY == "BUY"
        assert OrderSide.SELL == "SELL"


class TestOrder:
    """Tests for Order model."""

    def test_valid_order(self) -> None:
        """Test creating a valid order."""
        order = Order(
            symbol="EURUSD",
            side=OrderSide.BUY,
            size=0.1,
            entry_price=1.085,
            stop_loss=1.065,
            take_profit=1.105,
            trailing_stop_pct=2.0,
        )

        assert order.symbol == "EURUSD"
        assert order.side == OrderSide.BUY
        assert order.size == 0.1
        assert order.entry_price == 1.085
        assert order.stop_loss == 1.065
        assert order.take_profit == 1.105
        assert order.trailing_stop_pct == 2.0

    def test_order_optional_fields(self) -> None:
        """Test order with optional fields."""
        order = Order(
            symbol="EURUSD",
            side=OrderSide.SELL,
            size=0.5,
            entry_price=1.085,
            stop_loss=1.105,
        )

        assert order.take_profit is None
        assert order.trailing_stop_pct is None

    def test_order_invalid_size(self) -> None:
        """Test that order requires positive size."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            Order(
                symbol="EURUSD",
                side=OrderSide.BUY,
                size=0,
                entry_price=1.085,
                stop_loss=1.065,
            )

        with pytest.raises(ValidationError):
            Order(
                symbol="EURUSD",
                side=OrderSide.BUY,
                size=-0.1,
                entry_price=1.085,
                stop_loss=1.065,
            )


class TestTraderConfiguration:
    """Tests for Trader configuration."""

    def test_default_configuration(self) -> None:
        """Test default configuration values."""
        trader = Trader(params={})

        assert trader.position_sizing == PositionSizing.CONSERVATIVE
        assert trader.max_positions == 3
        assert trader.trailing_stop_pct == 2.0
        assert trader.budget == 10000.0
        assert trader.mode == TraderMode.ACTIVE

    def test_custom_configuration(self) -> None:
        """Test custom configuration values."""
        trader = Trader(
            params={
                "position_sizing": "aggressive",
                "max_positions": 5,
                "trailing_stop_pct": 3.0,
                "budget": 50000.0,
            }
        )

        assert trader.position_sizing == PositionSizing.AGGRESSIVE
        assert trader.max_positions == 5
        assert trader.trailing_stop_pct == 3.0
        assert trader.budget == 50000.0

    def test_invalid_position_sizing_fallback(self) -> None:
        """Test fallback for invalid position sizing."""
        trader = Trader(params={"position_sizing": "invalid"})

        assert trader.position_sizing == PositionSizing.CONSERVATIVE

    def test_agent_name(self) -> None:
        """Test that agent name is set correctly."""
        trader = Trader(params={})
        assert trader.name == "trader"

    def test_initial_status(self) -> None:
        """Test that agent starts with NORMAL status."""
        trader = Trader(params={})
        assert trader.status == AgentStatus.NORMAL


class TestTraderPrepareOrder:
    """Tests for Trader.prepare_order method."""

    @pytest.fixture
    def trader(self) -> Trader:
        """Create a Trader with default config."""
        return Trader(params={"budget": 10000.0})

    @pytest.mark.asyncio
    async def test_prepare_buy_order(self, trader: Trader) -> None:
        """Test preparing a BUY order."""
        context = {
            "signal": "BUY",
            "market_data": {
                "symbol": "EURUSD",
                "current_price": 1.085,
            },
            "confidence": 0.85,
        }

        result = await trader.prepare_order(context)

        assert isinstance(result, AgentDecision)
        assert result.decision_type == "action"
        assert result.data["action"] == "order_prepared"
        assert result.data["order"]["side"] == "BUY"
        assert result.data["order"]["symbol"] == "EURUSD"

    @pytest.mark.asyncio
    async def test_prepare_sell_order(self, trader: Trader) -> None:
        """Test preparing a SELL order."""
        context = {
            "signal": "SELL",
            "market_data": {
                "symbol": "GBPUSD",
                "current_price": 1.25,
            },
        }

        result = await trader.prepare_order(context)

        assert result.data["order"]["side"] == "SELL"
        assert result.data["order"]["symbol"] == "GBPUSD"

    @pytest.mark.asyncio
    async def test_prepare_order_hold_signal(self, trader: Trader) -> None:
        """Test that HOLD signal returns no order."""
        context = {
            "signal": "HOLD",
            "market_data": {"symbol": "EURUSD", "current_price": 1.085},
        }

        result = await trader.prepare_order(context)

        assert result.data["action"] == "no_order"
        assert result.data["reason"] == "Signal is HOLD"

    @pytest.mark.asyncio
    async def test_prepare_order_missing_price(self, trader: Trader) -> None:
        """Test rejection when price is missing."""
        context = {
            "signal": "BUY",
            "market_data": {"symbol": "EURUSD"},
        }

        result = await trader.prepare_order(context)

        assert result.decision_type == "rejection"
        assert "current_price" in result.data["reason"]

    @pytest.mark.asyncio
    async def test_prepare_order_hold_mode(self, trader: Trader) -> None:
        """Test rejection in HOLD mode."""
        trader.set_mode(TraderMode.HOLD)
        context = {
            "signal": "BUY",
            "market_data": {"symbol": "EURUSD", "current_price": 1.085},
        }

        result = await trader.prepare_order(context)

        assert result.decision_type == "rejection"
        assert "HOLD mode" in result.data["reason"]

    @pytest.mark.asyncio
    async def test_position_sizing_conservative(self) -> None:
        """Test conservative position sizing (1%)."""
        trader = Trader(params={"budget": 10000.0, "position_sizing": "conservative"})
        context = {
            "signal": "BUY",
            "market_data": {"symbol": "EURUSD", "current_price": 1.0},
        }

        result = await trader.prepare_order(context)

        # 1% of 10000 = 100, at price 1.0 = size 100
        assert result.data["order"]["size"] == 100.0

    @pytest.mark.asyncio
    async def test_position_sizing_aggressive(self) -> None:
        """Test aggressive position sizing (5%)."""
        trader = Trader(params={"budget": 10000.0, "position_sizing": "aggressive"})
        context = {
            "signal": "BUY",
            "market_data": {"symbol": "EURUSD", "current_price": 1.0},
        }

        result = await trader.prepare_order(context)

        # 5% of 10000 = 500, at price 1.0 = size 500
        assert result.data["order"]["size"] == 500.0

    @pytest.mark.asyncio
    async def test_stop_loss_calculation_buy(self, trader: Trader) -> None:
        """Test stop loss calculation for BUY order."""
        trader.trailing_stop_pct = 2.0
        context = {
            "signal": "BUY",
            "market_data": {"symbol": "EURUSD", "current_price": 100.0},
        }

        result = await trader.prepare_order(context)

        # Stop loss for BUY: 100 * (1 - 0.02) = 98
        assert result.data["order"]["stop_loss"] == 98.0

    @pytest.mark.asyncio
    async def test_stop_loss_calculation_sell(self, trader: Trader) -> None:
        """Test stop loss calculation for SELL order."""
        trader.trailing_stop_pct = 2.0
        context = {
            "signal": "SELL",
            "market_data": {"symbol": "EURUSD", "current_price": 100.0},
        }

        result = await trader.prepare_order(context)

        # Stop loss for SELL: 100 * (1 + 0.02) = 102
        assert result.data["order"]["stop_loss"] == 102.0

    @pytest.mark.asyncio
    async def test_prepare_order_adds_to_pending(self, trader: Trader) -> None:
        """Test that prepared orders are added to pending list."""
        assert len(trader.get_pending_orders()) == 0

        context = {
            "signal": "BUY",
            "market_data": {"symbol": "EURUSD", "current_price": 1.085},
        }

        await trader.prepare_order(context)

        assert len(trader.get_pending_orders()) == 1


class TestTraderExecute:
    """Tests for Trader.execute method."""

    @pytest.fixture
    def trader(self) -> Trader:
        """Create a Trader with default config."""
        return Trader(params={})

    @pytest.mark.asyncio
    async def test_execute_pending_order(self, trader: Trader) -> None:
        """Test executing a pending order."""
        # Prepare an order first
        await trader.prepare_order({
            "signal": "BUY",
            "market_data": {"symbol": "EURUSD", "current_price": 1.085},
        })

        result = await trader.execute({})

        assert result.decision_type == "action"
        assert result.data["action"] == "executed"
        assert result.data["order"]["symbol"] == "EURUSD"
        assert result.data["paper_trading"] is True

    @pytest.mark.asyncio
    async def test_execute_order_from_context(self, trader: Trader) -> None:
        """Test executing order provided in context."""
        context = {
            "order": {
                "symbol": "GBPUSD",
                "side": "SELL",
                "size": 0.5,
                "entry_price": 1.25,
                "stop_loss": 1.27,
            }
        }

        result = await trader.execute(context)

        assert result.data["action"] == "executed"
        assert result.data["order"]["symbol"] == "GBPUSD"

    @pytest.mark.asyncio
    async def test_execute_no_orders(self, trader: Trader) -> None:
        """Test execution with no pending orders."""
        result = await trader.execute({})

        assert result.data["action"] == "no_action"
        assert result.data["reason"] == "No orders to execute"

    @pytest.mark.asyncio
    async def test_execute_hold_mode_queues_order(self, trader: Trader) -> None:
        """Test that orders are queued in HOLD mode."""
        trader.set_mode(TraderMode.HOLD)
        context = {
            "order": {
                "symbol": "EURUSD",
                "side": "BUY",
                "size": 0.1,
                "entry_price": 1.085,
                "stop_loss": 1.065,
            }
        }

        result = await trader.execute(context)

        assert result.data["action"] == "queued"
        assert "HOLD mode" in result.data["reason"]
        assert len(trader.get_pending_orders()) == 1

    @pytest.mark.asyncio
    async def test_execute_invalid_order_data(self, trader: Trader) -> None:
        """Test execution with invalid order data."""
        context = {"order": {"invalid": "data"}}

        result = await trader.execute(context)

        assert result.decision_type == "rejection"
        assert "Invalid order data" in result.data["reason"]


class TestTraderCloseAllPositions:
    """Tests for Trader.close_all_positions method."""

    @pytest.fixture
    def trader(self) -> Trader:
        """Create a Trader with default config."""
        return Trader(params={})

    @pytest.mark.asyncio
    async def test_close_all_positions(self, trader: Trader) -> None:
        """Test emergency close all positions."""
        # Add some pending orders
        await trader.prepare_order({
            "signal": "BUY",
            "market_data": {"symbol": "EURUSD", "current_price": 1.085},
        })
        await trader.prepare_order({
            "signal": "SELL",
            "market_data": {"symbol": "GBPUSD", "current_price": 1.25},
        })

        result = await trader.close_all_positions()

        assert result.data["action"] == "close_all"
        assert result.data["pending_orders_cleared"] == 2
        assert result.data["mode_changed_to"] == "hold"

    @pytest.mark.asyncio
    async def test_close_all_sets_hold_mode(self, trader: Trader) -> None:
        """Test that close_all sets HOLD mode."""
        assert trader.mode == TraderMode.ACTIVE

        await trader.close_all_positions()

        assert trader.mode == TraderMode.HOLD

    @pytest.mark.asyncio
    async def test_close_all_sets_warning_status(self, trader: Trader) -> None:
        """Test that close_all sets WARNING status."""
        await trader.close_all_positions()

        assert trader.status == AgentStatus.WARNING


class TestTraderModeManagement:
    """Tests for Trader mode management."""

    @pytest.fixture
    def trader(self) -> Trader:
        """Create a Trader with default config."""
        return Trader(params={})

    def test_set_mode_active(self, trader: Trader) -> None:
        """Test setting ACTIVE mode."""
        trader.set_mode(TraderMode.HOLD)
        trader.set_mode(TraderMode.ACTIVE)

        assert trader.mode == TraderMode.ACTIVE

    def test_set_mode_hold(self, trader: Trader) -> None:
        """Test setting HOLD mode."""
        trader.set_mode(TraderMode.HOLD)

        assert trader.mode == TraderMode.HOLD


class TestTraderSerialization:
    """Tests for Trader serialization."""

    def test_to_dict(self) -> None:
        """Test trader to_dict serialization."""
        trader = Trader(
            params={
                "position_sizing": "moderate",
                "max_positions": 5,
                "trailing_stop_pct": 3.0,
            }
        )

        result = trader.to_dict()

        assert result["name"] == "trader"
        assert result["status"] == "normal"
        assert result["mode"] == "active"
        assert result["position_sizing"] == "moderate"
        assert result["max_positions"] == 5
        assert result["trailing_stop_pct"] == 3.0
        assert result["pending_orders"] == 0

    @pytest.mark.asyncio
    async def test_to_dict_with_pending_orders(self) -> None:
        """Test to_dict includes pending order count."""
        trader = Trader(params={})
        await trader.prepare_order({
            "signal": "BUY",
            "market_data": {"symbol": "EURUSD", "current_price": 1.085},
        })

        result = trader.to_dict()

        assert result["pending_orders"] == 1
