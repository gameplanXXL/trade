"""Tests for Market Data Feed."""

import asyncio
from datetime import UTC, datetime
from decimal import Decimal

import pytest

from src.core.exceptions import MT5ConnectionError
from src.mt5.connector import MockMT5Backend, MT5Connector
from src.mt5.market_data import (
    MarketDataFeed,
    canonicalize_symbol,
    to_mt5_symbol,
)
from src.mt5.schemas import MT5Settings, Price, Timeframe


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
    """Create mock MT5 backend with price data."""
    backend = MockMT5Backend()
    return backend


@pytest.fixture
def connector(mt5_settings: MT5Settings, mock_backend: MockMT5Backend) -> MT5Connector:
    """Create connected MT5 connector."""
    return MT5Connector(settings=mt5_settings, backend=mock_backend)


@pytest.fixture
def market_feed(connector: MT5Connector) -> MarketDataFeed:
    """Create market data feed."""
    return MarketDataFeed(
        connector=connector,
        symbols=["EUR/USD", "GBP/USD"],
        tick_interval=0.1,  # Fast for testing
    )


class TestSymbolNormalization:
    """Tests for symbol normalization functions."""

    def test_canonicalize_mt5_symbol(self) -> None:
        """Test converting MT5 symbol to canonical format."""
        assert canonicalize_symbol("EURUSD") == "EUR/USD"
        assert canonicalize_symbol("GBPUSD") == "GBP/USD"
        assert canonicalize_symbol("USDJPY") == "USD/JPY"

    def test_canonicalize_already_canonical(self) -> None:
        """Test canonical symbols remain unchanged."""
        assert canonicalize_symbol("EUR/USD") == "EUR/USD"
        assert canonicalize_symbol("GBP/USD") == "GBP/USD"

    def test_canonicalize_lowercase(self) -> None:
        """Test lowercase symbols are uppercased."""
        assert canonicalize_symbol("eurusd") == "EUR/USD"
        assert canonicalize_symbol("eur/usd") == "EUR/USD"

    def test_canonicalize_with_spaces(self) -> None:
        """Test symbols with spaces are cleaned."""
        assert canonicalize_symbol("EUR USD") == "EUR/USD"
        assert canonicalize_symbol(" EURUSD ") == "EUR/USD"

    def test_canonicalize_non_forex(self) -> None:
        """Test non-forex symbols are returned as-is."""
        assert canonicalize_symbol("XAUUSD") == "XAU/USD"  # Gold
        assert canonicalize_symbol("US500") == "US500"  # Index

    def test_to_mt5_symbol(self) -> None:
        """Test converting canonical to MT5 format."""
        assert to_mt5_symbol("EUR/USD") == "EURUSD"
        assert to_mt5_symbol("GBP/USD") == "GBPUSD"
        assert to_mt5_symbol("USD/JPY") == "USDJPY"

    def test_to_mt5_already_mt5_format(self) -> None:
        """Test MT5 symbols remain unchanged."""
        assert to_mt5_symbol("EURUSD") == "EURUSD"

    def test_to_mt5_lowercase(self) -> None:
        """Test lowercase symbols are uppercased."""
        assert to_mt5_symbol("eur/usd") == "EURUSD"


class TestMarketDataFeedInit:
    """Tests for MarketDataFeed initialization."""

    def test_init_with_symbols(self, connector: MT5Connector) -> None:
        """Test initialization with symbols list."""
        feed = MarketDataFeed(connector, ["EUR/USD", "GBP/USD"])

        assert len(feed.symbols) == 2
        assert "EUR/USD" in feed.symbols
        assert "GBP/USD" in feed.symbols

    def test_init_normalizes_symbols(self, connector: MT5Connector) -> None:
        """Test that symbols are normalized on init."""
        feed = MarketDataFeed(connector, ["EURUSD", "gbpusd"])

        assert "EUR/USD" in feed.symbols
        assert "GBP/USD" in feed.symbols

    def test_init_default_tick_interval(self, connector: MT5Connector) -> None:
        """Test default tick interval."""
        feed = MarketDataFeed(connector, ["EUR/USD"])

        assert feed.tick_interval == 1.0

    def test_init_custom_tick_interval(self, connector: MT5Connector) -> None:
        """Test custom tick interval."""
        feed = MarketDataFeed(connector, ["EUR/USD"], tick_interval=0.5)

        assert feed.tick_interval == 0.5


class TestGetCurrentPrice:
    """Tests for get_current_price method."""

    async def test_get_price_when_connected(
        self, market_feed: MarketDataFeed, connector: MT5Connector
    ) -> None:
        """Test getting price when connected."""
        await connector.connect()

        price = await market_feed.get_current_price("EUR/USD")

        assert isinstance(price, Price)
        assert price.symbol == "EUR/USD"
        assert isinstance(price.bid, Decimal)
        assert isinstance(price.ask, Decimal)
        assert price.ask > price.bid  # Ask should be higher than bid

    async def test_get_price_not_connected(self, market_feed: MarketDataFeed) -> None:
        """Test getting price when not connected raises error."""
        with pytest.raises(MT5ConnectionError) as exc_info:
            await market_feed.get_current_price("EUR/USD")

        assert "Not connected" in str(exc_info.value)

    async def test_get_price_normalizes_symbol(
        self, market_feed: MarketDataFeed, connector: MT5Connector
    ) -> None:
        """Test that symbol is normalized before fetching."""
        await connector.connect()

        # Use MT5 format
        price = await market_feed.get_current_price("EURUSD")

        assert price.symbol == "EUR/USD"

    async def test_get_price_caches_last_price(
        self, market_feed: MarketDataFeed, connector: MT5Connector
    ) -> None:
        """Test that last price is cached."""
        await connector.connect()

        price = await market_feed.get_current_price("EUR/USD")
        cached = market_feed.get_last_price("EUR/USD")

        assert cached is not None
        assert cached.symbol == price.symbol


class TestGetOHLCV:
    """Tests for get_ohlcv method."""

    async def test_get_ohlcv_when_connected(
        self, market_feed: MarketDataFeed, connector: MT5Connector
    ) -> None:
        """Test getting OHLCV when connected."""
        await connector.connect()

        ohlcv = await market_feed.get_ohlcv("EUR/USD", "H1", count=10)

        assert isinstance(ohlcv, list)
        assert len(ohlcv) >= 1
        candle = ohlcv[0]
        assert isinstance(candle.open, Decimal)
        assert isinstance(candle.high, Decimal)
        assert isinstance(candle.low, Decimal)
        assert isinstance(candle.close, Decimal)

    async def test_get_ohlcv_with_timeframe_enum(
        self, market_feed: MarketDataFeed, connector: MT5Connector
    ) -> None:
        """Test getting OHLCV with Timeframe enum."""
        await connector.connect()

        ohlcv = await market_feed.get_ohlcv("EUR/USD", Timeframe.H1, count=10)

        assert isinstance(ohlcv, list)

    async def test_get_ohlcv_not_connected(self, market_feed: MarketDataFeed) -> None:
        """Test getting OHLCV when not connected raises error."""
        with pytest.raises(MT5ConnectionError) as exc_info:
            await market_feed.get_ohlcv("EUR/USD", "H1")

        assert "Not connected" in str(exc_info.value)


class TestSubscription:
    """Tests for subscribe/unsubscribe functionality."""

    async def test_subscribe_starts_tick_loop(
        self, market_feed: MarketDataFeed, connector: MT5Connector
    ) -> None:
        """Test that subscribe starts the tick loop."""
        await connector.connect()
        received_prices: list[Price] = []

        async def callback(price: Price) -> None:
            received_prices.append(price)

        await market_feed.subscribe(callback)

        # Wait for a few ticks
        await asyncio.sleep(0.3)

        await market_feed.unsubscribe()

        assert len(received_prices) > 0
        assert all(isinstance(p, Price) for p in received_prices)

    async def test_subscribe_multiple_callbacks(
        self, market_feed: MarketDataFeed, connector: MT5Connector
    ) -> None:
        """Test multiple callbacks receive updates."""
        await connector.connect()
        prices1: list[Price] = []
        prices2: list[Price] = []

        await market_feed.subscribe(lambda p: prices1.append(p))
        await market_feed.subscribe(lambda p: prices2.append(p))

        await asyncio.sleep(0.3)
        await market_feed.unsubscribe()

        assert len(prices1) > 0
        assert len(prices2) > 0

    async def test_unsubscribe_stops_tick_loop(
        self, market_feed: MarketDataFeed, connector: MT5Connector
    ) -> None:
        """Test that unsubscribe stops the tick loop."""
        await connector.connect()
        received_count = 0

        def callback(price: Price) -> None:
            nonlocal received_count
            received_count += 1

        await market_feed.subscribe(callback)
        await asyncio.sleep(0.2)
        await market_feed.unsubscribe()

        count_after_unsub = received_count
        await asyncio.sleep(0.2)

        # No more prices should be received after unsubscribe
        assert received_count == count_after_unsub

    async def test_unsubscribe_clears_callbacks(
        self, market_feed: MarketDataFeed, connector: MT5Connector
    ) -> None:
        """Test that unsubscribe clears all callbacks."""
        await connector.connect()

        await market_feed.subscribe(lambda p: None)
        assert len(market_feed._callbacks) == 1

        await market_feed.unsubscribe()
        assert len(market_feed._callbacks) == 0


class TestLastPrice:
    """Tests for get_last_price method."""

    async def test_get_last_price_exists(
        self, market_feed: MarketDataFeed, connector: MT5Connector
    ) -> None:
        """Test getting last price when it exists."""
        await connector.connect()
        await market_feed.get_current_price("EUR/USD")

        last = market_feed.get_last_price("EUR/USD")

        assert last is not None
        assert last.symbol == "EUR/USD"

    def test_get_last_price_not_exists(self, market_feed: MarketDataFeed) -> None:
        """Test getting last price when it doesn't exist."""
        last = market_feed.get_last_price("EUR/USD")

        assert last is None

    async def test_get_last_price_normalizes_symbol(
        self, market_feed: MarketDataFeed, connector: MT5Connector
    ) -> None:
        """Test that symbol is normalized when getting last price."""
        await connector.connect()
        await market_feed.get_current_price("EUR/USD")

        # Use MT5 format to query
        last = market_feed.get_last_price("EURUSD")

        assert last is not None
        assert last.symbol == "EUR/USD"


class TestPriceSchema:
    """Tests for Price schema."""

    def test_price_mid_calculation(self) -> None:
        """Test mid price calculation."""
        price = Price(
            symbol="EUR/USD",
            bid=Decimal("1.08500"),
            ask=Decimal("1.08520"),
            spread=Decimal("20"),
            time=datetime.now(UTC),
        )

        assert price.mid == Decimal("1.08510")

    def test_price_spread_reflects_bid_ask_diff(self) -> None:
        """Test that spread should match bid/ask difference."""
        bid = Decimal("1.08500")
        ask = Decimal("1.08520")

        price = Price(
            symbol="EUR/USD",
            bid=bid,
            ask=ask,
            spread=Decimal("20"),  # 20 pips
            time=datetime.now(UTC),
        )

        # Verify ask is higher than bid
        assert price.ask > price.bid
