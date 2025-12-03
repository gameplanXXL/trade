"""Tests for Paper Trading Engine."""

from decimal import Decimal

import pytest

from src.mt5.connector import MockMT5Backend, MT5Connector
from src.mt5.market_data import MarketDataFeed
from src.mt5.orders import OrderRequest, OrderSide, OrderStatus, OrderType
from src.mt5.schemas import MT5Settings
from src.services.paper_trading import (
    PaperPosition,
    PaperTradingEngine,
    PaperTradingError,
    PositionUpdate,
    PositionUpdateType,
)


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
def market_data(connector: MT5Connector) -> MarketDataFeed:
    """Create market data feed."""
    return MarketDataFeed(
        connector=connector,
        symbols=["EUR/USD", "GBP/USD"],
        tick_interval=0.1,
    )


@pytest.fixture
def paper_engine(market_data: MarketDataFeed) -> PaperTradingEngine:
    """Create paper trading engine."""
    return PaperTradingEngine(
        market_data=market_data,
        default_spread_pips=Decimal("2"),
        update_interval=0.1,
    )


class TestPaperPosition:
    """Tests for PaperPosition model."""

    def test_create_paper_position(self) -> None:
        """Test creating a paper position."""
        position = PaperPosition(
            ticket=1,
            symbol="EUR/USD",
            side=OrderSide.BUY,
            volume=Decimal("0.1"),
            entry_price=Decimal("1.08500"),
            current_price=Decimal("1.08500"),
        )

        assert position.ticket == 1
        assert position.symbol == "EUR/USD"
        assert position.is_open is True

    def test_calculate_pnl_buy_profit(self) -> None:
        """Test P/L calculation for profitable BUY."""
        position = PaperPosition(
            ticket=1,
            symbol="EUR/USD",
            side=OrderSide.BUY,
            volume=Decimal("0.1"),  # 0.1 lot = 10,000 units
            entry_price=Decimal("1.08500"),
            current_price=Decimal("1.08600"),  # +10 pips
        )

        pnl = position.calculate_pnl(Decimal("1.08600"))

        # 0.1 lot * 100000 * 0.001 = 10 USD profit
        assert pnl == Decimal("10.00")

    def test_calculate_pnl_buy_loss(self) -> None:
        """Test P/L calculation for losing BUY."""
        position = PaperPosition(
            ticket=1,
            symbol="EUR/USD",
            side=OrderSide.BUY,
            volume=Decimal("0.1"),
            entry_price=Decimal("1.08500"),
            current_price=Decimal("1.08400"),  # -10 pips
        )

        pnl = position.calculate_pnl(Decimal("1.08400"))

        assert pnl == Decimal("-10.00")

    def test_calculate_pnl_sell_profit(self) -> None:
        """Test P/L calculation for profitable SELL."""
        position = PaperPosition(
            ticket=1,
            symbol="EUR/USD",
            side=OrderSide.SELL,
            volume=Decimal("0.1"),
            entry_price=Decimal("1.08500"),
            current_price=Decimal("1.08400"),  # -10 pips (profit for sell)
        )

        pnl = position.calculate_pnl(Decimal("1.08400"))

        assert pnl == Decimal("10.00")


class TestPaperTradingEngine:
    """Tests for PaperTradingEngine class."""

    async def test_execute_buy_order(
        self, paper_engine: PaperTradingEngine, connector: MT5Connector
    ) -> None:
        """Test executing a buy order."""
        await connector.connect()

        order = OrderRequest(
            symbol="EUR/USD",
            order_type=OrderType.MARKET_BUY,
            volume=Decimal("0.1"),
        )

        result = await paper_engine.execute_order(order, budget=Decimal("10000"))

        assert result.status == OrderStatus.FILLED
        assert result.ticket > 0
        assert result.symbol == "EUR/USD"
        assert len(paper_engine.positions) == 1

    async def test_execute_sell_order(
        self, paper_engine: PaperTradingEngine, connector: MT5Connector
    ) -> None:
        """Test executing a sell order."""
        await connector.connect()

        order = OrderRequest(
            symbol="EUR/USD",
            order_type=OrderType.MARKET_SELL,
            volume=Decimal("0.1"),
        )

        result = await paper_engine.execute_order(order, budget=Decimal("10000"))

        assert result.status == OrderStatus.FILLED
        assert result.order_type == OrderType.MARKET_SELL

    async def test_execute_order_insufficient_budget(
        self, paper_engine: PaperTradingEngine, connector: MT5Connector
    ) -> None:
        """Test order execution with insufficient budget."""
        await connector.connect()

        order = OrderRequest(
            symbol="EUR/USD",
            order_type=OrderType.MARKET_BUY,
            volume=Decimal("10.0"),  # Large position
        )

        with pytest.raises(PaperTradingError) as exc_info:
            await paper_engine.execute_order(order, budget=Decimal("100"))

        assert "Insufficient budget" in str(exc_info.value)

    async def test_execute_order_with_trailing_stop(
        self, paper_engine: PaperTradingEngine, connector: MT5Connector
    ) -> None:
        """Test order execution with trailing stop."""
        await connector.connect()

        order = OrderRequest(
            symbol="EUR/USD",
            order_type=OrderType.MARKET_BUY,
            volume=Decimal("0.1"),
            trailing_stop_pct=Decimal("1.0"),
        )

        result = await paper_engine.execute_order(order, budget=Decimal("10000"))

        assert result.stop_loss is not None
        assert result.stop_loss < result.price  # SL below entry for BUY

    async def test_execute_order_records_spread_cost(
        self, paper_engine: PaperTradingEngine, connector: MT5Connector
    ) -> None:
        """Test that spread cost is recorded."""
        await connector.connect()

        order = OrderRequest(
            symbol="EUR/USD",
            order_type=OrderType.MARKET_BUY,
            volume=Decimal("0.1"),
        )

        result = await paper_engine.execute_order(order, budget=Decimal("10000"))
        position = paper_engine.positions[result.ticket]

        assert position.spread_cost > 0


class TestClosePosition:
    """Tests for close_position method."""

    async def test_close_position(
        self, paper_engine: PaperTradingEngine, connector: MT5Connector
    ) -> None:
        """Test closing a position."""
        await connector.connect()

        order = OrderRequest(
            symbol="EUR/USD",
            order_type=OrderType.MARKET_BUY,
            volume=Decimal("0.1"),
        )
        open_result = await paper_engine.execute_order(order, budget=Decimal("10000"))

        close_result = await paper_engine.close_position(open_result.ticket)

        assert close_result.status == OrderStatus.FILLED
        assert paper_engine.positions[open_result.ticket].is_open is False

    async def test_close_nonexistent_position(
        self, paper_engine: PaperTradingEngine
    ) -> None:
        """Test closing non-existent position raises error."""
        with pytest.raises(PaperTradingError) as exc_info:
            await paper_engine.close_position(99999)

        assert "not found" in str(exc_info.value)

    async def test_close_already_closed_position(
        self, paper_engine: PaperTradingEngine, connector: MT5Connector
    ) -> None:
        """Test closing already closed position raises error."""
        await connector.connect()

        order = OrderRequest(
            symbol="EUR/USD",
            order_type=OrderType.MARKET_BUY,
            volume=Decimal("0.1"),
        )
        result = await paper_engine.execute_order(order, budget=Decimal("10000"))
        await paper_engine.close_position(result.ticket)

        with pytest.raises(PaperTradingError) as exc_info:
            await paper_engine.close_position(result.ticket)

        assert "already closed" in str(exc_info.value)


class TestUpdatePositions:
    """Tests for update_positions method."""

    async def test_update_positions_returns_updates(
        self, paper_engine: PaperTradingEngine, connector: MT5Connector
    ) -> None:
        """Test that update_positions returns position updates."""
        await connector.connect()

        order = OrderRequest(
            symbol="EUR/USD",
            order_type=OrderType.MARKET_BUY,
            volume=Decimal("0.1"),
        )
        await paper_engine.execute_order(order, budget=Decimal("10000"))

        updates = await paper_engine.update_positions()

        assert len(updates) == 1
        assert isinstance(updates[0], PositionUpdate)

    async def test_update_positions_price_change(
        self, paper_engine: PaperTradingEngine, connector: MT5Connector
    ) -> None:
        """Test position update with price change."""
        await connector.connect()

        order = OrderRequest(
            symbol="EUR/USD",
            order_type=OrderType.MARKET_BUY,
            volume=Decimal("0.1"),
        )
        result = await paper_engine.execute_order(order, budget=Decimal("10000"))

        # First update
        updates = await paper_engine.update_positions()

        assert updates[0].ticket == result.ticket
        assert updates[0].update_type == PositionUpdateType.PRICE_UPDATE


class TestGetEquity:
    """Tests for get_equity method."""

    async def test_get_equity_no_positions(
        self, paper_engine: PaperTradingEngine
    ) -> None:
        """Test equity is zero with no positions."""
        equity = paper_engine.get_equity()

        assert equity == Decimal("0")

    async def test_get_equity_with_positions(
        self, paper_engine: PaperTradingEngine, connector: MT5Connector
    ) -> None:
        """Test equity calculation with positions."""
        await connector.connect()

        for _ in range(3):
            order = OrderRequest(
                symbol="EUR/USD",
                order_type=OrderType.MARKET_BUY,
                volume=Decimal("0.1"),
            )
            await paper_engine.execute_order(order, budget=Decimal("10000"))

        equity = paper_engine.get_equity()

        # Equity should be sum of unrealized P/L (0 at start)
        assert isinstance(equity, Decimal)


class TestGetOpenPositions:
    """Tests for get_open_positions method."""

    async def test_get_open_positions_empty(
        self, paper_engine: PaperTradingEngine
    ) -> None:
        """Test getting positions when none exist."""
        positions = paper_engine.get_open_positions()

        assert positions == []

    async def test_get_open_positions_excludes_closed(
        self, paper_engine: PaperTradingEngine, connector: MT5Connector
    ) -> None:
        """Test that closed positions are excluded."""
        await connector.connect()

        order = OrderRequest(
            symbol="EUR/USD",
            order_type=OrderType.MARKET_BUY,
            volume=Decimal("0.1"),
        )
        result = await paper_engine.execute_order(order, budget=Decimal("10000"))
        await paper_engine.close_position(result.ticket)

        positions = paper_engine.get_open_positions()

        assert len(positions) == 0


class TestGetPosition:
    """Tests for get_position method."""

    async def test_get_position_exists(
        self, paper_engine: PaperTradingEngine, connector: MT5Connector
    ) -> None:
        """Test getting an existing position."""
        await connector.connect()

        order = OrderRequest(
            symbol="EUR/USD",
            order_type=OrderType.MARKET_BUY,
            volume=Decimal("0.1"),
        )
        result = await paper_engine.execute_order(order, budget=Decimal("10000"))

        position = paper_engine.get_position(result.ticket)

        assert position is not None
        assert position.ticket == result.ticket

    def test_get_position_not_exists(
        self, paper_engine: PaperTradingEngine
    ) -> None:
        """Test getting non-existent position returns None."""
        position = paper_engine.get_position(99999)

        assert position is None


class TestTrailingStopCalculation:
    """Tests for trailing stop calculation."""

    def test_calculate_trailing_sl_buy(
        self, paper_engine: PaperTradingEngine
    ) -> None:
        """Test trailing SL calculation for BUY."""
        sl = paper_engine._calculate_trailing_sl(
            Decimal("1.10000"),
            Decimal("1.0"),
            OrderSide.BUY,
        )

        assert sl == Decimal("1.089")

    def test_calculate_trailing_sl_sell(
        self, paper_engine: PaperTradingEngine
    ) -> None:
        """Test trailing SL calculation for SELL."""
        sl = paper_engine._calculate_trailing_sl(
            Decimal("1.10000"),
            Decimal("1.0"),
            OrderSide.SELL,
        )

        assert sl == Decimal("1.111")


class TestPipsToPrice:
    """Tests for pips to price conversion."""

    def test_pips_to_price_standard(
        self, paper_engine: PaperTradingEngine
    ) -> None:
        """Test pip conversion for standard pairs."""
        price = paper_engine._pips_to_price(Decimal("10"), "EUR/USD")

        assert price == Decimal("0.001")

    def test_pips_to_price_jpy(
        self, paper_engine: PaperTradingEngine
    ) -> None:
        """Test pip conversion for JPY pairs."""
        price = paper_engine._pips_to_price(Decimal("10"), "USD/JPY")

        assert price == Decimal("0.1")


class TestPositionUpdate:
    """Tests for PositionUpdate model."""

    def test_create_position_update(self) -> None:
        """Test creating a position update."""
        update = PositionUpdate(
            ticket=1,
            symbol="EUR/USD",
            update_type=PositionUpdateType.PRICE_UPDATE,
            previous_price=Decimal("1.08500"),
            current_price=Decimal("1.08600"),
            previous_pnl=Decimal("0"),
            current_pnl=Decimal("10.00"),
        )

        assert update.ticket == 1
        assert update.update_type == PositionUpdateType.PRICE_UPDATE
        assert update.stop_loss_triggered is False
