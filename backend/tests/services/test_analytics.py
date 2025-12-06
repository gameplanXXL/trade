"""Tests for Analytics Service."""

from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.api.schemas.analytics import PerformanceSummary
from src.core.exceptions import TeamNotFoundError
from src.db.models import TeamInstance, Trade
from src.services.analytics import AnalyticsService


@pytest.fixture
def mock_session() -> AsyncMock:
    """Create mock async session."""
    return AsyncMock()


@pytest.fixture
def analytics_service(mock_session: AsyncMock) -> AnalyticsService:
    """Create analytics service with mock session."""
    return AnalyticsService(session=mock_session)


@pytest.fixture
def mock_team_instance() -> TeamInstance:
    """Create mock team instance."""
    team = MagicMock(spec=TeamInstance)
    team.id = 1
    team.name = "Test Team"
    team.initial_budget = Decimal("10000.00")
    team.current_budget = Decimal("10500.00")
    team.realized_pnl = Decimal("500.00")
    team.unrealized_pnl = Decimal("0.00")
    return team


@pytest.fixture
def mock_closed_trades() -> list[Trade]:
    """Create mock closed trades for testing."""
    trades = []

    # Winning trades
    for i in range(6):
        trade = MagicMock(spec=Trade)
        trade.id = i + 1
        trade.ticket = 1000 + i
        trade.symbol = "EUR/USD" if i < 3 else "GBP/USD"
        trade.side = "BUY"
        trade.status = "closed"
        trade.pnl = Decimal("100.00")
        trade.opened_at = datetime(2025, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        trade.closed_at = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        trades.append(trade)

    # Losing trades
    for i in range(4):
        trade = MagicMock(spec=Trade)
        trade.id = i + 7
        trade.ticket = 2000 + i
        trade.symbol = "EUR/USD" if i < 2 else "GBP/USD"
        trade.side = "SELL"
        trade.status = "closed"
        trade.pnl = Decimal("-50.00")
        trade.opened_at = datetime(2025, 1, 2, 10, 0, 0, tzinfo=timezone.utc)
        trade.closed_at = datetime(2025, 1, 2, 12, 0, 0, tzinfo=timezone.utc)
        trades.append(trade)

    return trades


class TestGetTeamInstance:
    """Tests for _get_team_instance internal method."""

    async def test_get_team_instance_found(
        self,
        analytics_service: AnalyticsService,
        mock_session: AsyncMock,
        mock_team_instance: TeamInstance,
    ) -> None:
        """Test getting existing team instance."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_team_instance
        mock_session.execute.return_value = mock_result

        team = await analytics_service._get_team_instance(1)

        assert team.id == 1
        assert team.name == "Test Team"

    async def test_get_team_instance_not_found(
        self,
        analytics_service: AnalyticsService,
        mock_session: AsyncMock,
    ) -> None:
        """Test getting non-existent team instance raises error."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        with pytest.raises(TeamNotFoundError) as exc_info:
            await analytics_service._get_team_instance(999)

        assert "Team instance with ID 999 not found" in str(exc_info.value)


class TestCalculateTotalPnl:
    """Tests for calculate_total_pnl method."""

    async def test_calculate_total_pnl(
        self,
        analytics_service: AnalyticsService,
        mock_session: AsyncMock,
        mock_team_instance: TeamInstance,
    ) -> None:
        """Test calculating total P/L."""
        mock_team_instance.realized_pnl = Decimal("400.00")
        mock_team_instance.unrealized_pnl = Decimal("100.00")
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_team_instance
        mock_session.execute.return_value = mock_result

        total_pnl = await analytics_service.calculate_total_pnl(1)

        assert total_pnl == Decimal("500.00")

    async def test_calculate_total_pnl_negative(
        self,
        analytics_service: AnalyticsService,
        mock_session: AsyncMock,
        mock_team_instance: TeamInstance,
    ) -> None:
        """Test calculating negative total P/L."""
        mock_team_instance.realized_pnl = Decimal("-300.00")
        mock_team_instance.unrealized_pnl = Decimal("-50.00")
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_team_instance
        mock_session.execute.return_value = mock_result

        total_pnl = await analytics_service.calculate_total_pnl(1)

        assert total_pnl == Decimal("-350.00")


class TestCalculatePnlBySymbol:
    """Tests for calculate_pnl_by_symbol method."""

    async def test_calculate_pnl_by_symbol(
        self,
        analytics_service: AnalyticsService,
        mock_session: AsyncMock,
        mock_closed_trades: list[Trade],
    ) -> None:
        """Test calculating P/L by symbol."""
        # EUR/USD: 3 wins (300) + 2 losses (-100) = 200
        # GBP/USD: 3 wins (300) + 2 losses (-100) = 200
        mock_result = MagicMock()
        mock_result.all.return_value = [
            ("EUR/USD", Decimal("200.00")),
            ("GBP/USD", Decimal("200.00")),
        ]
        mock_session.execute.return_value = mock_result

        pnl_by_symbol = await analytics_service.calculate_pnl_by_symbol(1)

        assert pnl_by_symbol["EUR/USD"] == Decimal("200.00")
        assert pnl_by_symbol["GBP/USD"] == Decimal("200.00")
        assert len(pnl_by_symbol) == 2

    async def test_calculate_pnl_by_symbol_empty(
        self,
        analytics_service: AnalyticsService,
        mock_session: AsyncMock,
    ) -> None:
        """Test calculating P/L by symbol with no trades."""
        mock_result = MagicMock()
        mock_result.all.return_value = []
        mock_session.execute.return_value = mock_result

        pnl_by_symbol = await analytics_service.calculate_pnl_by_symbol(1)

        assert pnl_by_symbol == {}


class TestCalculateWinRate:
    """Tests for calculate_win_rate method."""

    async def test_calculate_win_rate(
        self,
        analytics_service: AnalyticsService,
        mock_session: AsyncMock,
    ) -> None:
        """Test calculating win rate with trades."""
        # 6 winning trades out of 10 total = 60%
        mock_result = MagicMock()
        mock_result.one_or_none.return_value = (10, 6)
        mock_session.execute.return_value = mock_result

        win_rate = await analytics_service.calculate_win_rate(1)

        assert win_rate == 0.6

    async def test_calculate_win_rate_zero_trades(
        self,
        analytics_service: AnalyticsService,
        mock_session: AsyncMock,
    ) -> None:
        """Test calculating win rate with no trades returns 0."""
        mock_result = MagicMock()
        mock_result.one_or_none.return_value = (0, 0)
        mock_session.execute.return_value = mock_result

        win_rate = await analytics_service.calculate_win_rate(1)

        assert win_rate == 0.0

    async def test_calculate_win_rate_all_wins(
        self,
        analytics_service: AnalyticsService,
        mock_session: AsyncMock,
    ) -> None:
        """Test calculating win rate with all winning trades."""
        mock_result = MagicMock()
        mock_result.one_or_none.return_value = (5, 5)
        mock_session.execute.return_value = mock_result

        win_rate = await analytics_service.calculate_win_rate(1)

        assert win_rate == 1.0


class TestCalculateSharpeRatio:
    """Tests for calculate_sharpe_ratio method."""

    async def test_calculate_sharpe_ratio(
        self,
        analytics_service: AnalyticsService,
        mock_session: AsyncMock,
    ) -> None:
        """Test calculating Sharpe ratio with realistic data."""
        # Daily returns: 1%, 2%, -1%, 1.5%, 0.5%
        # Mean = 0.8%, Std = ~1.02%
        # Sharpe = (0.008 - 0.02/252) / 0.0102 ≈ 0.776
        mock_result = MagicMock()
        pnl_values = [
            Decimal("100.00"),
            Decimal("200.00"),
            Decimal("-100.00"),
            Decimal("150.00"),
            Decimal("50.00"),
        ]
        mock_result.scalars.return_value.all.return_value = pnl_values
        mock_session.execute.return_value = mock_result

        sharpe = await analytics_service.calculate_sharpe_ratio(1, risk_free_rate=0.02)

        # Sharpe should be positive for profitable trading
        assert sharpe > 0
        assert isinstance(sharpe, float)

    async def test_calculate_sharpe_ratio_zero_trades(
        self,
        analytics_service: AnalyticsService,
        mock_session: AsyncMock,
    ) -> None:
        """Test calculating Sharpe ratio with no trades returns 0."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        sharpe = await analytics_service.calculate_sharpe_ratio(1)

        assert sharpe == 0.0

    async def test_calculate_sharpe_ratio_zero_std(
        self,
        analytics_service: AnalyticsService,
        mock_session: AsyncMock,
    ) -> None:
        """Test calculating Sharpe ratio with zero std dev returns 0."""
        # All trades have same P/L (no volatility)
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [
            Decimal("100.00"),
            Decimal("100.00"),
            Decimal("100.00"),
        ]
        mock_session.execute.return_value = mock_result

        sharpe = await analytics_service.calculate_sharpe_ratio(1)

        assert sharpe == 0.0


class TestCalculateMaxDrawdown:
    """Tests for calculate_max_drawdown method."""

    async def test_calculate_max_drawdown(
        self,
        analytics_service: AnalyticsService,
        mock_session: AsyncMock,
    ) -> None:
        """Test calculating max drawdown with realistic equity curve."""
        # Cumulative P/L: 100, 300, 200, 350, 300
        # Peak at 350, trough at 300 after peak
        # Drawdown = (350 - 300) / 350 = 14.29%
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [
            Decimal("100.00"),
            Decimal("200.00"),
            Decimal("-100.00"),
            Decimal("150.00"),
            Decimal("-50.00"),
        ]
        mock_session.execute.return_value = mock_result

        drawdown = await analytics_service.calculate_max_drawdown(1)

        assert drawdown > 0
        assert drawdown < 1.0  # Should be less than 100%
        assert isinstance(drawdown, float)

    async def test_calculate_max_drawdown_no_trades(
        self,
        analytics_service: AnalyticsService,
        mock_session: AsyncMock,
    ) -> None:
        """Test calculating max drawdown with no trades returns 0."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        drawdown = await analytics_service.calculate_max_drawdown(1)

        assert drawdown == 0.0

    async def test_calculate_max_drawdown_only_gains(
        self,
        analytics_service: AnalyticsService,
        mock_session: AsyncMock,
    ) -> None:
        """Test calculating max drawdown with only winning trades."""
        # All positive P/L, no drawdown
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [
            Decimal("100.00"),
            Decimal("150.00"),
            Decimal("200.00"),
        ]
        mock_session.execute.return_value = mock_result

        drawdown = await analytics_service.calculate_max_drawdown(1)

        assert drawdown == 0.0


class TestGetPerformanceSummary:
    """Tests for get_performance_summary method."""

    async def test_get_performance_summary(
        self,
        analytics_service: AnalyticsService,
        mock_session: AsyncMock,
        mock_team_instance: TeamInstance,
    ) -> None:
        """Test getting complete performance summary."""
        mock_team_instance.initial_budget = Decimal("10000.00")
        mock_team_instance.realized_pnl = Decimal("400.00")
        mock_team_instance.unrealized_pnl = Decimal("100.00")

        # Mock results for different queries
        results = [
            MagicMock(),  # get_team_instance
            MagicMock(),  # win_rate query
            MagicMock(),  # sharpe ratio query
            MagicMock(),  # max drawdown query
        ]

        # Setup team instance
        results[0].scalar_one_or_none.return_value = mock_team_instance

        # Setup win rate: 6 wins out of 10 trades
        results[1].one_or_none.return_value = (10, 6)

        # Setup Sharpe ratio: sample P/L values
        results[2].scalars.return_value.all.return_value = [
            Decimal("100.00"),
            Decimal("200.00"),
            Decimal("-50.00"),
            Decimal("150.00"),
            Decimal("100.00"),
        ]

        # Setup max drawdown: sample P/L values
        results[3].scalars.return_value.all.return_value = [
            Decimal("100.00"),
            Decimal("200.00"),
            Decimal("-100.00"),
            Decimal("150.00"),
            Decimal("-50.00"),
        ]

        mock_session.execute.side_effect = results

        summary = await analytics_service.get_performance_summary(1)

        assert isinstance(summary, PerformanceSummary)
        assert summary.total_pnl == Decimal("500.00")
        assert summary.total_pnl_percent == 5.0  # 500/10000 * 100
        assert summary.win_rate == 0.6
        assert summary.total_trades == 10
        assert summary.winning_trades == 6
        assert summary.losing_trades == 4
        assert isinstance(summary.sharpe_ratio, float)
        assert isinstance(summary.max_drawdown, float)

    async def test_get_performance_summary_no_trades(
        self,
        analytics_service: AnalyticsService,
        mock_session: AsyncMock,
        mock_team_instance: TeamInstance,
    ) -> None:
        """Test getting performance summary with no trades."""
        mock_team_instance.initial_budget = Decimal("10000.00")
        mock_team_instance.realized_pnl = Decimal("0.00")
        mock_team_instance.unrealized_pnl = Decimal("0.00")

        results = [
            MagicMock(),  # get_team_instance
            MagicMock(),  # win_rate query
            MagicMock(),  # sharpe ratio query
            MagicMock(),  # max drawdown query
        ]

        results[0].scalar_one_or_none.return_value = mock_team_instance
        results[1].one_or_none.return_value = (0, 0)
        results[2].scalars.return_value.all.return_value = []
        results[3].scalars.return_value.all.return_value = []

        mock_session.execute.side_effect = results

        summary = await analytics_service.get_performance_summary(1)

        assert summary.total_pnl == Decimal("0.00")
        assert summary.total_pnl_percent == 0.0
        assert summary.win_rate == 0.0
        assert summary.total_trades == 0
        assert summary.winning_trades == 0
        assert summary.losing_trades == 0
        assert summary.sharpe_ratio == 0.0
        assert summary.max_drawdown == 0.0
