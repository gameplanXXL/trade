"""MT5 Connector with auto-reconnect functionality.

This module provides async connectivity to MetaTrader 5.
Since aiomql requires Python 3.13+ and MT5 native library only works on Windows,
this implementation uses a protocol-based approach that can be adapted for:
1. Wine-based MT5 on Linux via subprocess/socket communication
2. Mock implementation for testing
3. Future aiomql integration when Python version is upgraded
"""

import asyncio
from typing import Protocol

import structlog

from src.core.exceptions import MT5ConnectionError
from src.mt5.schemas import AccountInfo, MT5Settings

log = structlog.get_logger()


class MT5Backend(Protocol):
    """Protocol for MT5 backend implementations."""

    async def initialize(self, settings: MT5Settings) -> bool:
        """Initialize connection to MT5."""
        ...

    async def shutdown(self) -> None:
        """Shutdown MT5 connection."""
        ...

    async def account_info(self) -> dict:
        """Get account information."""
        ...

    def is_connected(self) -> bool:
        """Check if connected to MT5."""
        ...


class MT5Connector:
    """MT5 Connector with auto-reconnect functionality.

    Provides stable connection to MetaTrader 5 with automatic reconnection
    on connection loss using exponential backoff.
    """

    def __init__(self, settings: MT5Settings, backend: MT5Backend | None = None) -> None:
        """Initialize MT5 Connector.

        Args:
            settings: MT5 connection settings
            backend: Optional MT5 backend implementation (defaults to MockMT5Backend)
        """
        self.settings = settings
        self._connected = False
        self._reconnect_task: asyncio.Task | None = None
        self._health_check_task: asyncio.Task | None = None
        self._shutdown_event = asyncio.Event()

        # M1 fix: Warn if using MockMT5Backend (default)
        if backend is None:
            self._backend = MockMT5Backend()
            log.warning(
                "mt5_using_mock_backend",
                message="Using MockMT5Backend - NOT suitable for production trading!",
                hint="Provide a real MT5Backend implementation for live trading.",
            )
        else:
            self._backend = backend

    async def connect(self) -> bool:
        """Connect to MT5.

        Returns:
            True if connection successful, False otherwise.

        Raises:
            MT5ConnectionError: If connection fails after retries.
        """
        log.info("mt5_connecting", server=self.settings.server, login=self.settings.login)

        try:
            success = await self._backend.initialize(self.settings)
            if success:
                self._connected = True
                log.info(
                    "mt5_connected",
                    server=self.settings.server,
                    login=self.settings.login,
                )
                return True
            else:
                log.warning("mt5_connection_failed", server=self.settings.server)
                return False
        except Exception as e:
            log.error("mt5_connection_error", error=str(e), server=self.settings.server)
            raise MT5ConnectionError(
                f"Failed to connect to MT5: {e}",
                details={"server": self.settings.server, "login": self.settings.login},
            ) from e

    async def disconnect(self) -> None:
        """Disconnect from MT5 cleanly."""
        log.info("mt5_disconnecting", server=self.settings.server)

        self._shutdown_event.set()

        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass

        if self._reconnect_task:
            self._reconnect_task.cancel()
            try:
                await self._reconnect_task
            except asyncio.CancelledError:
                pass

        await self._backend.shutdown()
        self._connected = False

        log.info("mt5_disconnected", server=self.settings.server)

    async def reconnect(self, max_attempts: int = 3) -> bool:
        """Attempt to reconnect with exponential backoff.

        Args:
            max_attempts: Maximum number of reconnection attempts (default: 3)

        Returns:
            True if reconnection successful, False otherwise.

        Raises:
            MT5ConnectionError: If all reconnection attempts fail.
        """
        base_delay = 1.0  # Starting delay in seconds

        for attempt in range(1, max_attempts + 1):
            delay = base_delay * (2 ** (attempt - 1))  # Exponential backoff: 1s, 2s, 4s

            log.info(
                "mt5_reconnect_attempt",
                attempt=attempt,
                max_attempts=max_attempts,
                delay_seconds=delay,
            )

            await asyncio.sleep(delay)

            try:
                # First disconnect cleanly
                await self._backend.shutdown()
                self._connected = False

                # Then try to connect
                success = await self._backend.initialize(self.settings)
                if success:
                    self._connected = True
                    log.info(
                        "mt5_reconnected",
                        attempt=attempt,
                        server=self.settings.server,
                    )
                    return True
            except Exception as e:
                log.warning(
                    "mt5_reconnect_failed",
                    attempt=attempt,
                    max_attempts=max_attempts,
                    error=str(e),
                )

        # All attempts failed
        log.error(
            "mt5_reconnect_exhausted",
            max_attempts=max_attempts,
            server=self.settings.server,
        )
        raise MT5ConnectionError(
            f"Failed to reconnect after {max_attempts} attempts",
            details={
                "server": self.settings.server,
                "login": self.settings.login,
                "attempts": max_attempts,
            },
        )

    @property
    def is_connected(self) -> bool:
        """Check if currently connected to MT5.

        Returns:
            True if connected, False otherwise.
        """
        return self._connected and self._backend.is_connected()

    async def get_account_info(self) -> AccountInfo:
        """Get account information from MT5.

        Returns:
            AccountInfo with current account details.

        Raises:
            MT5ConnectionError: If not connected or request fails.
        """
        if not self.is_connected:
            raise MT5ConnectionError(
                "Not connected to MT5",
                details={"server": self.settings.server},
            )

        try:
            info = await self._backend.account_info()
            return AccountInfo(**info)
        except Exception as e:
            log.error("mt5_account_info_error", error=str(e))
            raise MT5ConnectionError(
                f"Failed to get account info: {e}",
                details={"server": self.settings.server},
            ) from e

    async def start_health_check(self, interval_seconds: int = 30) -> None:
        """Start periodic health check.

        Args:
            interval_seconds: Time between health checks (default: 30s)
        """
        self._shutdown_event.clear()
        self._health_check_task = asyncio.create_task(
            self._health_check_loop(interval_seconds)
        )
        log.info("mt5_health_check_started", interval_seconds=interval_seconds)

    async def _health_check_loop(self, interval_seconds: int) -> None:
        """Internal health check loop.

        H3 fix: Track consecutive reconnect failures and implement backoff.
        """
        consecutive_failures = 0
        max_consecutive_failures = 5
        backoff_multiplier = 2

        while not self._shutdown_event.is_set():
            try:
                # Apply backoff if we had failures
                effective_interval = interval_seconds * (backoff_multiplier ** min(consecutive_failures, 3))
                await asyncio.sleep(effective_interval)

                if self._shutdown_event.is_set():
                    break

                if not self.is_connected:
                    log.warning(
                        "mt5_health_check_disconnected",
                        consecutive_failures=consecutive_failures,
                    )
                    try:
                        await self.reconnect()
                        consecutive_failures = 0  # Reset on success
                        log.info("mt5_health_check_reconnected")
                    except MT5ConnectionError:
                        consecutive_failures += 1
                        log.error(
                            "mt5_health_check_reconnect_failed",
                            consecutive_failures=consecutive_failures,
                            max_failures=max_consecutive_failures,
                        )
                        if consecutive_failures >= max_consecutive_failures:
                            log.critical(
                                "mt5_health_check_max_failures_reached",
                                message="Connection appears permanently lost",
                            )
                else:
                    consecutive_failures = 0  # Reset on healthy check
                    log.debug("mt5_health_check_ok")

            except asyncio.CancelledError:
                break
            except Exception as e:
                log.error("mt5_health_check_error", error=str(e))


class MockMT5Backend:
    """Mock MT5 backend for testing and development."""

    def __init__(self) -> None:
        self._connected = False
        self._should_fail = False
        self._account_balance = 10000.0

    async def initialize(self, settings: MT5Settings) -> bool:
        """Mock initialization."""
        if self._should_fail:
            return False
        await asyncio.sleep(0.1)  # Simulate network delay
        self._connected = True
        return True

    async def shutdown(self) -> None:
        """Mock shutdown."""
        self._connected = False

    async def account_info(self) -> dict:
        """Mock account info."""
        if not self._connected:
            raise RuntimeError("Not connected")
        return {
            "login": 12345,
            "balance": self._account_balance,
            "equity": self._account_balance,
            "margin": 0,
            "free_margin": self._account_balance,
            "leverage": 100,
            "currency": "USD",
            "server": "Demo",
            "trade_allowed": True,
        }

    def is_connected(self) -> bool:
        """Check mock connection status."""
        return self._connected

    def set_should_fail(self, should_fail: bool) -> None:
        """Set whether connection should fail (for testing)."""
        self._should_fail = should_fail

    def simulate_disconnect(self) -> None:
        """Simulate connection loss (for testing)."""
        self._connected = False
