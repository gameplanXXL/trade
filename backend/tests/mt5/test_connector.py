"""Tests for MT5 Connector."""

import pytest

from src.core.exceptions import MT5ConnectionError
from src.mt5.connector import MockMT5Backend, MT5Connector
from src.mt5.schemas import AccountInfo, MT5Settings


@pytest.fixture
def mt5_settings() -> MT5Settings:
    """Create test MT5 settings."""
    return MT5Settings(
        login=12345,
        password="test_password",
        server="TestServer",
        timeout=5000,
    )


@pytest.fixture
def mock_backend() -> MockMT5Backend:
    """Create mock MT5 backend."""
    return MockMT5Backend()


@pytest.fixture
def connector(mt5_settings: MT5Settings, mock_backend: MockMT5Backend) -> MT5Connector:
    """Create MT5 connector with mock backend."""
    return MT5Connector(settings=mt5_settings, backend=mock_backend)


class TestMT5Connector:
    """Tests for MT5Connector class."""

    async def test_connect_success(
        self, connector: MT5Connector, mock_backend: MockMT5Backend
    ) -> None:
        """Test successful connection."""
        result = await connector.connect()

        assert result is True
        assert connector.is_connected is True
        assert mock_backend.is_connected() is True

    async def test_connect_failure(
        self, connector: MT5Connector, mock_backend: MockMT5Backend
    ) -> None:
        """Test connection failure."""
        mock_backend.set_should_fail(True)

        result = await connector.connect()

        assert result is False
        assert connector.is_connected is False

    async def test_disconnect(
        self, connector: MT5Connector, mock_backend: MockMT5Backend
    ) -> None:
        """Test disconnection."""
        await connector.connect()
        assert connector.is_connected is True

        await connector.disconnect()

        assert connector.is_connected is False
        assert mock_backend.is_connected() is False

    async def test_is_connected_property(
        self, connector: MT5Connector, mock_backend: MockMT5Backend
    ) -> None:
        """Test is_connected property reflects actual state."""
        assert connector.is_connected is False

        await connector.connect()
        assert connector.is_connected is True

        mock_backend.simulate_disconnect()
        assert connector.is_connected is False

    async def test_get_account_info_success(self, connector: MT5Connector) -> None:
        """Test getting account info when connected."""
        await connector.connect()

        account_info = await connector.get_account_info()

        assert isinstance(account_info, AccountInfo)
        assert account_info.login == 12345
        assert account_info.balance == 10000.0
        assert account_info.leverage == 100
        assert account_info.trade_allowed is True

    async def test_get_account_info_not_connected(self, connector: MT5Connector) -> None:
        """Test getting account info when not connected raises error."""
        with pytest.raises(MT5ConnectionError) as exc_info:
            await connector.get_account_info()

        assert "Not connected" in str(exc_info.value)

    async def test_reconnect_success_first_attempt(
        self, connector: MT5Connector, mock_backend: MockMT5Backend
    ) -> None:
        """Test successful reconnect on first attempt."""
        await connector.connect()
        mock_backend.simulate_disconnect()
        assert connector.is_connected is False

        result = await connector.reconnect(max_attempts=3)

        assert result is True
        assert connector.is_connected is True

    async def test_reconnect_success_after_failures(
        self, connector: MT5Connector, mock_backend: MockMT5Backend
    ) -> None:
        """Test reconnect succeeds after initial failures."""
        await connector.connect()
        mock_backend.simulate_disconnect()

        # Fail first attempt, succeed on second
        attempt_count = 0
        original_initialize = mock_backend.initialize

        async def failing_then_success(settings: MT5Settings) -> bool:
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count == 1:
                return False
            return await original_initialize(settings)

        mock_backend.initialize = failing_then_success

        result = await connector.reconnect(max_attempts=3)

        assert result is True
        assert attempt_count == 2

    async def test_reconnect_exhausted(
        self, connector: MT5Connector, mock_backend: MockMT5Backend
    ) -> None:
        """Test reconnect raises error after all attempts exhausted."""
        await connector.connect()
        mock_backend.set_should_fail(True)
        mock_backend.simulate_disconnect()

        with pytest.raises(MT5ConnectionError) as exc_info:
            await connector.reconnect(max_attempts=2)

        assert "Failed to reconnect after 2 attempts" in str(exc_info.value)
        assert exc_info.value.details["attempts"] == 2

    async def test_reconnect_exponential_backoff(
        self, connector: MT5Connector, mock_backend: MockMT5Backend, monkeypatch
    ) -> None:
        """Test that reconnect uses exponential backoff timing."""
        import src.mt5.connector as connector_module

        await connector.connect()
        mock_backend.set_should_fail(True)
        mock_backend.simulate_disconnect()

        sleep_calls: list[float] = []

        async def mock_sleep(delay: float) -> None:
            sleep_calls.append(delay)
            # Don't actually sleep in tests

        monkeypatch.setattr(connector_module.asyncio, "sleep", mock_sleep)

        with pytest.raises(MT5ConnectionError):
            await connector.reconnect(max_attempts=3)

        # Check exponential backoff: 1s, 2s, 4s
        assert len(sleep_calls) == 3
        assert sleep_calls[0] == 1.0
        assert sleep_calls[1] == 2.0
        assert sleep_calls[2] == 4.0


class TestMT5Settings:
    """Tests for MT5Settings schema."""

    def test_mt5_settings_required_fields(self) -> None:
        """Test MT5Settings requires login, password, server."""
        settings = MT5Settings(
            login=12345,
            password="secret",
            server="broker.server.com",
        )

        assert settings.login == 12345
        assert settings.password == "secret"
        assert settings.server == "broker.server.com"

    def test_mt5_settings_defaults(self) -> None:
        """Test MT5Settings default values."""
        settings = MT5Settings(
            login=12345,
            password="secret",
            server="broker.server.com",
        )

        assert settings.timeout == 60000
        assert settings.path is None

    def test_mt5_settings_custom_timeout(self) -> None:
        """Test MT5Settings with custom timeout."""
        settings = MT5Settings(
            login=12345,
            password="secret",
            server="broker.server.com",
            timeout=30000,
        )

        assert settings.timeout == 30000


class TestAccountInfo:
    """Tests for AccountInfo schema."""

    def test_account_info_creation(self) -> None:
        """Test AccountInfo creation with all fields."""
        info = AccountInfo(
            login=12345,
            balance=10000.50,
            equity=10500.75,
            margin=500.00,
            free_margin=10000.75,
            leverage=100,
            currency="EUR",
            server="TestServer",
            trade_allowed=True,
        )

        assert info.login == 12345
        assert info.balance == 10000.50
        assert info.equity == 10500.75
        assert info.leverage == 100
        assert info.currency == "EUR"

    def test_account_info_defaults(self) -> None:
        """Test AccountInfo default values."""
        info = AccountInfo(
            login=12345,
            balance=10000,
            equity=10000,
            free_margin=10000,
            leverage=100,
            server="TestServer",
        )

        assert info.margin == 0
        assert info.currency == "USD"
        assert info.trade_allowed is True


class TestMockMT5Backend:
    """Tests for MockMT5Backend."""

    async def test_mock_initialize(self) -> None:
        """Test mock backend initialization."""
        backend = MockMT5Backend()
        settings = MT5Settings(login=1, password="p", server="s")

        result = await backend.initialize(settings)

        assert result is True
        assert backend.is_connected() is True

    async def test_mock_shutdown(self) -> None:
        """Test mock backend shutdown."""
        backend = MockMT5Backend()
        settings = MT5Settings(login=1, password="p", server="s")
        await backend.initialize(settings)

        await backend.shutdown()

        assert backend.is_connected() is False

    async def test_mock_account_info(self) -> None:
        """Test mock backend account info."""
        backend = MockMT5Backend()
        settings = MT5Settings(login=1, password="p", server="s")
        await backend.initialize(settings)

        info = await backend.account_info()

        assert "login" in info
        assert "balance" in info
        assert info["balance"] == 10000.0

    async def test_mock_account_info_not_connected(self) -> None:
        """Test mock backend account info when not connected."""
        backend = MockMT5Backend()

        with pytest.raises(RuntimeError, match="Not connected"):
            await backend.account_info()

    def test_mock_set_should_fail(self) -> None:
        """Test mock backend failure simulation."""
        backend = MockMT5Backend()
        backend.set_should_fail(True)

        assert backend._should_fail is True

    def test_mock_simulate_disconnect(self) -> None:
        """Test mock backend disconnect simulation."""
        backend = MockMT5Backend()
        backend._connected = True

        backend.simulate_disconnect()

        assert backend.is_connected() is False
