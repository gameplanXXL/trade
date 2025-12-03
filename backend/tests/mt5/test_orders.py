"""Tests for Order Management."""

from decimal import Decimal

import pytest

from src.core.exceptions import MT5ConnectionError
from src.mt5.connector import MockMT5Backend, MT5Connector
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
from src.mt5.schemas import MT5Settings


@pytest.fixture
def mt5_settings() -> MT5Settings:
    """Create test MT5 settings."""
    return MT5Settings(
        login=12345,
        password="test_password",
        server="TestServer",
    )


@pytest.fixture
def mock_backend() -> MockMT5Backend:
    """Create mock MT5 backend."""
    return MockMT5Backend()


@pytest.fixture
def connector(mt5_settings: MT5Settings, mock_backend: MockMT5Backend) -> MT5Connector:
    """Create MT5 connector."""
    return MT5Connector(settings=mt5_settings, backend=mock_backend)


@pytest.fixture
def order_manager(connector: MT5Connector) -> OrderManager:
    """Create order manager."""
    return OrderManager(connector=connector, default_trailing_stop_pct=Decimal("1.0"))


class TestOrderRequest:
    """Tests for OrderRequest model."""

    def test_create_buy_order(self) -> None:
        """Test creating a buy order request."""
        order = OrderRequest(
            symbol="EUR/USD",
            order_type=OrderType.MARKET_BUY,
            volume=Decimal("0.1"),
        )

        assert order.symbol == "EUR/USD"
        assert order.order_type == OrderType.MARKET_BUY
        assert order.volume == Decimal("0.1")
        assert order.side == OrderSide.BUY

    def test_create_sell_order(self) -> None:
        """Test creating a sell order request."""
        order = OrderRequest(
            symbol="EUR/USD",
            order_type=OrderType.MARKET_SELL,
            volume=Decimal("0.5"),
        )

        assert order.order_type == OrderType.MARKET_SELL
        assert order.side == OrderSide.SELL

    def test_order_with_stop_loss(self) -> None:
        """Test order with explicit stop loss."""
        order = OrderRequest(
            symbol="EUR/USD",
            order_type=OrderType.MARKET_BUY,
            volume=Decimal("0.1"),
            stop_loss=Decimal("1.08000"),
        )

        assert order.stop_loss == Decimal("1.08000")

    def test_order_with_trailing_stop(self) -> None:
        """Test order with trailing stop percentage."""
        order = OrderRequest(
            symbol="EUR/USD",
            order_type=OrderType.MARKET_BUY,
            volume=Decimal("0.1"),
            trailing_stop_pct=Decimal("1.5"),
        )

        assert order.trailing_stop_pct == Decimal("1.5")

    def test_order_defaults(self) -> None:
        """Test order default values."""
        order = OrderRequest(
            symbol="EUR/USD",
            order_type=OrderType.MARKET_BUY,
            volume=Decimal("0.1"),
        )

        assert order.stop_loss is None
        assert order.take_profit is None
        assert order.trailing_stop_pct is None
        assert order.slippage == 10
        assert order.magic_number == 12345

    def test_order_volume_must_be_positive(self) -> None:
        """Test that volume must be positive."""
        with pytest.raises(ValueError):
            OrderRequest(
                symbol="EUR/USD",
                order_type=OrderType.MARKET_BUY,
                volume=Decimal("0"),
            )


class TestOrderManager:
    """Tests for OrderManager class."""

    async def test_place_buy_order(
        self, order_manager: OrderManager, connector: MT5Connector
    ) -> None:
        """Test placing a buy order."""
        await connector.connect()

        order = OrderRequest(
            symbol="EUR/USD",
            order_type=OrderType.MARKET_BUY,
            volume=Decimal("0.1"),
        )

        result = await order_manager.place_order(order)

        assert isinstance(result, OrderResult)
        assert result.ticket > 0
        assert result.symbol == "EUR/USD"
        assert result.status == OrderStatus.FILLED
        assert result.volume == Decimal("0.1")

    async def test_place_sell_order(
        self, order_manager: OrderManager, connector: MT5Connector
    ) -> None:
        """Test placing a sell order."""
        await connector.connect()

        order = OrderRequest(
            symbol="EUR/USD",
            order_type=OrderType.MARKET_SELL,
            volume=Decimal("0.2"),
        )

        result = await order_manager.place_order(order)

        assert result.order_type == OrderType.MARKET_SELL
        assert result.status == OrderStatus.FILLED

    async def test_place_order_not_connected(self, order_manager: OrderManager) -> None:
        """Test placing order when not connected raises error."""
        order = OrderRequest(
            symbol="EUR/USD",
            order_type=OrderType.MARKET_BUY,
            volume=Decimal("0.1"),
        )

        with pytest.raises(MT5ConnectionError) as exc_info:
            await order_manager.place_order(order)

        assert "Not connected" in str(exc_info.value)

    async def test_place_order_with_trailing_stop(
        self, order_manager: OrderManager, connector: MT5Connector
    ) -> None:
        """Test placing order with trailing stop."""
        await connector.connect()

        order = OrderRequest(
            symbol="EUR/USD",
            order_type=OrderType.MARKET_BUY,
            volume=Decimal("0.1"),
            trailing_stop_pct=Decimal("1.0"),
        )

        result = await order_manager.place_order(order)

        assert result.stop_loss is not None
        # SL should be below entry price for BUY
        assert result.stop_loss < result.price

    async def test_place_order_creates_position(
        self, order_manager: OrderManager, connector: MT5Connector
    ) -> None:
        """Test that placing order creates a tracked position."""
        await connector.connect()

        order = OrderRequest(
            symbol="EUR/USD",
            order_type=OrderType.MARKET_BUY,
            volume=Decimal("0.1"),
        )

        result = await order_manager.place_order(order)
        positions = await order_manager.get_open_positions()

        assert len(positions) == 1
        assert positions[0].ticket == result.ticket


class TestModifyOrder:
    """Tests for modify_order method."""

    async def test_modify_stop_loss(
        self, order_manager: OrderManager, connector: MT5Connector
    ) -> None:
        """Test modifying stop loss."""
        await connector.connect()

        order = OrderRequest(
            symbol="EUR/USD",
            order_type=OrderType.MARKET_BUY,
            volume=Decimal("0.1"),
            stop_loss=Decimal("1.08000"),
        )
        result = await order_manager.place_order(order)

        success = await order_manager.modify_order(result.ticket, Decimal("1.08100"))

        assert success is True
        positions = await order_manager.get_open_positions()
        assert positions[0].stop_loss == Decimal("1.08100")

    async def test_modify_nonexistent_order(self, order_manager: OrderManager) -> None:
        """Test modifying non-existent order raises error."""
        with pytest.raises(OrderError) as exc_info:
            await order_manager.modify_order(99999, Decimal("1.08000"))

        assert "not found" in str(exc_info.value)


class TestClosePosition:
    """Tests for close_position method."""

    async def test_close_position(
        self, order_manager: OrderManager, connector: MT5Connector
    ) -> None:
        """Test closing a position."""
        await connector.connect()

        order = OrderRequest(
            symbol="EUR/USD",
            order_type=OrderType.MARKET_BUY,
            volume=Decimal("0.1"),
        )
        open_result = await order_manager.place_order(order)

        close_result = await order_manager.close_position(open_result.ticket)

        assert close_result.status == OrderStatus.FILLED
        assert close_result.ticket == open_result.ticket

        positions = await order_manager.get_open_positions()
        assert len(positions) == 0

    async def test_close_nonexistent_position(self, order_manager: OrderManager) -> None:
        """Test closing non-existent position raises error."""
        with pytest.raises(OrderError) as exc_info:
            await order_manager.close_position(99999)

        assert "not found" in str(exc_info.value)

    async def test_close_position_calculates_profit(
        self, order_manager: OrderManager, connector: MT5Connector
    ) -> None:
        """Test that closing position calculates P/L."""
        await connector.connect()

        order = OrderRequest(
            symbol="EUR/USD",
            order_type=OrderType.MARKET_BUY,
            volume=Decimal("0.1"),
        )
        await order_manager.place_order(order)

        # Close should have a P/L in the comment
        result = await order_manager.close_position(1)

        assert "P/L" in result.comment


class TestCloseAllPositions:
    """Tests for close_all_positions method."""

    async def test_close_all_positions(
        self, order_manager: OrderManager, connector: MT5Connector
    ) -> None:
        """Test closing all positions."""
        await connector.connect()

        # Open multiple positions
        for _ in range(3):
            order = OrderRequest(
                symbol="EUR/USD",
                order_type=OrderType.MARKET_BUY,
                volume=Decimal("0.1"),
            )
            await order_manager.place_order(order)

        results = await order_manager.close_all_positions()

        assert len(results) == 3
        positions = await order_manager.get_open_positions()
        assert len(positions) == 0

    async def test_close_all_positions_filtered_by_symbol(
        self, order_manager: OrderManager, connector: MT5Connector
    ) -> None:
        """Test closing positions filtered by symbol."""
        await connector.connect()

        # Open positions for different symbols
        for symbol in ["EUR/USD", "EUR/USD", "GBP/USD"]:
            order = OrderRequest(
                symbol=symbol,
                order_type=OrderType.MARKET_BUY,
                volume=Decimal("0.1"),
            )
            await order_manager.place_order(order)

        results = await order_manager.close_all_positions(symbol="EUR/USD")

        assert len(results) == 2
        positions = await order_manager.get_open_positions()
        assert len(positions) == 1
        assert positions[0].symbol == "GBP/USD"


class TestGetOpenPositions:
    """Tests for get_open_positions method."""

    async def test_get_open_positions_empty(self, order_manager: OrderManager) -> None:
        """Test getting positions when none exist."""
        positions = await order_manager.get_open_positions()

        assert positions == []

    async def test_get_open_positions_returns_all(
        self, order_manager: OrderManager, connector: MT5Connector
    ) -> None:
        """Test getting all open positions."""
        await connector.connect()

        for i in range(5):
            order = OrderRequest(
                symbol="EUR/USD",
                order_type=OrderType.MARKET_BUY,
                volume=Decimal("0.1"),
            )
            await order_manager.place_order(order)

        positions = await order_manager.get_open_positions()

        assert len(positions) == 5


class TestTrailingStopCalculation:
    """Tests for trailing stop loss calculation."""

    def test_trailing_sl_buy_order(self, order_manager: OrderManager) -> None:
        """Test trailing SL calculation for BUY order."""
        price = Decimal("1.10000")
        trailing_pct = Decimal("1.0")

        sl = order_manager._calculate_trailing_sl(price, trailing_pct, OrderSide.BUY)

        # SL should be price - 1%
        expected = Decimal("1.08900")
        assert sl == expected

    def test_trailing_sl_sell_order(self, order_manager: OrderManager) -> None:
        """Test trailing SL calculation for SELL order."""
        price = Decimal("1.10000")
        trailing_pct = Decimal("1.0")

        sl = order_manager._calculate_trailing_sl(price, trailing_pct, OrderSide.SELL)

        # SL should be price + 1%
        expected = Decimal("1.11100")
        assert sl == expected


class TestUpdateTrailingStops:
    """Tests for update_trailing_stops method."""

    async def test_update_trailing_sl_buy_position_price_up(
        self, order_manager: OrderManager, connector: MT5Connector
    ) -> None:
        """Test trailing SL moves up when price goes up for BUY."""
        await connector.connect()

        order = OrderRequest(
            symbol="EUR/USD",
            order_type=OrderType.MARKET_BUY,
            volume=Decimal("0.1"),
            trailing_stop_pct=Decimal("1.0"),
        )
        result = await order_manager.place_order(order)
        original_sl = order_manager._positions[result.ticket].stop_loss

        # Simulate price increase
        new_price = result.price + Decimal("0.01")  # +100 pips
        await order_manager.update_trailing_stops({"EUR/USD": new_price})

        new_sl = order_manager._positions[result.ticket].stop_loss
        assert new_sl > original_sl

    async def test_trailing_sl_does_not_move_down_for_buy(
        self, order_manager: OrderManager, connector: MT5Connector
    ) -> None:
        """Test trailing SL does not move down for BUY position."""
        await connector.connect()

        order = OrderRequest(
            symbol="EUR/USD",
            order_type=OrderType.MARKET_BUY,
            volume=Decimal("0.1"),
            trailing_stop_pct=Decimal("1.0"),
        )
        result = await order_manager.place_order(order)
        original_sl = order_manager._positions[result.ticket].stop_loss

        # Simulate price decrease
        new_price = result.price - Decimal("0.01")  # -100 pips
        await order_manager.update_trailing_stops({"EUR/USD": new_price})

        new_sl = order_manager._positions[result.ticket].stop_loss
        assert new_sl == original_sl  # SL should not move down


class TestPosition:
    """Tests for Position model."""

    def test_create_position(self) -> None:
        """Test creating a position."""
        position = Position(
            ticket=1,
            symbol="EUR/USD",
            side=OrderSide.BUY,
            volume=Decimal("0.1"),
            entry_price=Decimal("1.08500"),
            current_price=Decimal("1.08600"),
        )

        assert position.ticket == 1
        assert position.status == PositionStatus.OPEN
        assert position.profit == Decimal("0")

    def test_position_defaults(self) -> None:
        """Test position default values."""
        position = Position(
            ticket=1,
            symbol="EUR/USD",
            side=OrderSide.BUY,
            volume=Decimal("0.1"),
            entry_price=Decimal("1.08500"),
            current_price=Decimal("1.08500"),
        )

        assert position.stop_loss is None
        assert position.take_profit is None
        assert position.magic_number == 0


class TestOrderResult:
    """Tests for OrderResult model."""

    def test_create_order_result(self) -> None:
        """Test creating an order result."""
        result = OrderResult(
            ticket=123,
            symbol="EUR/USD",
            order_type=OrderType.MARKET_BUY,
            volume=Decimal("0.1"),
            price=Decimal("1.08500"),
            status=OrderStatus.FILLED,
        )

        assert result.ticket == 123
        assert result.status == OrderStatus.FILLED
        assert result.timestamp is not None
