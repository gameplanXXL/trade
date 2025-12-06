"""Tests for Analytics Service."""

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.api.schemas.analytics import ActivitySummary, PerformanceSummary
from src.core.exceptions import TeamNotFoundError
from src.db.models import AgentDecisionLog, PerformanceMetric, TeamInstance, Trade
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
        trade.opened_at = datetime(2025, 1, 1, 10, 0, 0, tzinfo=UTC)
        trade.closed_at = datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC)
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
        trade.opened_at = datetime(2025, 1, 2, 10, 0, 0, tzinfo=UTC)
        trade.closed_at = datetime(2025, 1, 2, 12, 0, 0, tzinfo=UTC)
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


class TestAggregatePerformance:
    """Tests for aggregate_performance method."""

    async def test_aggregate_performance_hourly(
        self,
        analytics_service: AnalyticsService,
        mock_session: AsyncMock,
        mock_team_instance: TeamInstance,
    ) -> None:
        """Test aggregating performance metrics for hourly period."""
        # Mock get_team_instance
        team_result = MagicMock()
        team_result.scalar_one_or_none.return_value = mock_team_instance

        # Mock get_performance_summary results
        summary_result = MagicMock()
        summary_result.one_or_none.return_value = (10, 6)

        sharpe_result = MagicMock()
        sharpe_result.scalars.return_value.all.return_value = [
            Decimal("100.00"),
            Decimal("200.00"),
        ]

        drawdown_result = MagicMock()
        drawdown_result.scalars.return_value.all.return_value = [
            Decimal("100.00"),
            Decimal("200.00"),
        ]

        mock_session.execute.side_effect = [
            team_result,
            team_result,
            summary_result,
            sharpe_result,
            drawdown_result,
        ]

        metric = await analytics_service.aggregate_performance(1, period="hourly")

        assert isinstance(metric, PerformanceMetric)
        assert metric.team_instance_id == 1
        assert metric.period == "hourly"
        assert metric.pnl == Decimal("500.00")
        assert metric.trade_count == 10
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    async def test_aggregate_performance_invalid_period(
        self,
        analytics_service: AnalyticsService,
        mock_session: AsyncMock,
    ) -> None:
        """Test aggregating performance with invalid period raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            await analytics_service.aggregate_performance(1, period="invalid")

        assert "Invalid period" in str(exc_info.value)

    async def test_aggregate_performance_team_not_found(
        self,
        analytics_service: AnalyticsService,
        mock_session: AsyncMock,
    ) -> None:
        """Test aggregating performance for non-existent team raises error."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        with pytest.raises(TeamNotFoundError):
            await analytics_service.aggregate_performance(999, period="daily")


class TestGetPerformanceHistory:
    """Tests for get_performance_history method."""

    async def test_get_performance_history(
        self,
        analytics_service: AnalyticsService,
        mock_session: AsyncMock,
        mock_team_instance: TeamInstance,
    ) -> None:
        """Test getting performance history."""
        # Mock team instance check
        team_result = MagicMock()
        team_result.scalar_one_or_none.return_value = mock_team_instance

        # Mock performance metrics
        metrics = [
            MagicMock(spec=PerformanceMetric),
            MagicMock(spec=PerformanceMetric),
            MagicMock(spec=PerformanceMetric),
        ]
        for i, metric in enumerate(metrics):
            metric.id = i + 1
            metric.team_instance_id = 1
            metric.period = "hourly"
            metric.timestamp = datetime.now(UTC) - timedelta(hours=i)
            metric.pnl = Decimal("100.00") * (i + 1)

        history_result = MagicMock()
        history_result.scalars.return_value.all.return_value = metrics

        mock_session.execute.side_effect = [team_result, history_result]

        history = await analytics_service.get_performance_history(1, period="hourly")

        assert len(history) == 3
        assert all(isinstance(m, PerformanceMetric) for m in history)
        assert history[0].period == "hourly"

    async def test_get_performance_history_with_time_filter(
        self,
        analytics_service: AnalyticsService,
        mock_session: AsyncMock,
        mock_team_instance: TeamInstance,
    ) -> None:
        """Test getting performance history with time filters."""
        team_result = MagicMock()
        team_result.scalar_one_or_none.return_value = mock_team_instance

        history_result = MagicMock()
        history_result.scalars.return_value.all.return_value = []

        mock_session.execute.side_effect = [team_result, history_result]

        start_time = datetime.now(UTC) - timedelta(days=7)
        end_time = datetime.now(UTC)

        history = await analytics_service.get_performance_history(
            1, period="daily", start_time=start_time, end_time=end_time
        )

        assert isinstance(history, list)

    async def test_get_performance_history_empty(
        self,
        analytics_service: AnalyticsService,
        mock_session: AsyncMock,
        mock_team_instance: TeamInstance,
    ) -> None:
        """Test getting performance history with no records."""
        team_result = MagicMock()
        team_result.scalar_one_or_none.return_value = mock_team_instance

        history_result = MagicMock()
        history_result.scalars.return_value.all.return_value = []

        mock_session.execute.side_effect = [team_result, history_result]

        history = await analytics_service.get_performance_history(1, period="weekly")

        assert history == []


class TestGetLatestMetric:
    """Tests for get_latest_metric method."""

    async def test_get_latest_metric_found(
        self,
        analytics_service: AnalyticsService,
        mock_session: AsyncMock,
        mock_team_instance: TeamInstance,
    ) -> None:
        """Test getting latest metric when it exists."""
        team_result = MagicMock()
        team_result.scalar_one_or_none.return_value = mock_team_instance

        metric = MagicMock(spec=PerformanceMetric)
        metric.id = 1
        metric.team_instance_id = 1
        metric.period = "hourly"
        metric.timestamp = datetime.now(UTC)
        metric.pnl = Decimal("500.00")

        metric_result = MagicMock()
        metric_result.scalar_one_or_none.return_value = metric

        mock_session.execute.side_effect = [team_result, metric_result]

        latest = await analytics_service.get_latest_metric(1, period="hourly")

        assert latest is not None
        assert isinstance(latest, PerformanceMetric)
        assert latest.period == "hourly"

    async def test_get_latest_metric_not_found(
        self,
        analytics_service: AnalyticsService,
        mock_session: AsyncMock,
        mock_team_instance: TeamInstance,
    ) -> None:
        """Test getting latest metric when none exists."""
        team_result = MagicMock()
        team_result.scalar_one_or_none.return_value = mock_team_instance

        metric_result = MagicMock()
        metric_result.scalar_one_or_none.return_value = None

        mock_session.execute.side_effect = [team_result, metric_result]

        latest = await analytics_service.get_latest_metric(1, period="daily")

        assert latest is None

    async def test_get_latest_metric_team_not_found(
        self,
        analytics_service: AnalyticsService,
        mock_session: AsyncMock,
    ) -> None:
        """Test getting latest metric for non-existent team raises error."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        with pytest.raises(TeamNotFoundError):
            await analytics_service.get_latest_metric(999, period="hourly")


class TestGetAgentActivity:
    """Tests for get_agent_activity method."""

    async def test_get_agent_activity_all_decisions(
        self,
        analytics_service: AnalyticsService,
        mock_session: AsyncMock,
        mock_team_instance: TeamInstance,
    ) -> None:
        """Test getting all agent decisions for a team."""
        # Mock team instance check
        team_result = MagicMock()
        team_result.scalar_one_or_none.return_value = mock_team_instance

        # Mock agent decisions
        decisions = [
            MagicMock(spec=AgentDecisionLog),
            MagicMock(spec=AgentDecisionLog),
            MagicMock(spec=AgentDecisionLog),
        ]
        for i, decision in enumerate(decisions):
            decision.id = i + 1
            decision.team_instance_id = 1
            decision.agent_name = "MarketAnalyzer" if i < 2 else "RiskManager"
            decision.decision_type = "SIGNAL"
            decision.data = {"action": "BUY"}
            decision.created_at = datetime.now(UTC)

        activity_result = MagicMock()
        activity_result.scalars.return_value.all.return_value = decisions

        mock_session.execute.side_effect = [team_result, activity_result]

        activity = await analytics_service.get_agent_activity(1)

        assert len(activity) == 3
        assert all(isinstance(d, AgentDecisionLog) for d in activity)

    async def test_get_agent_activity_filter_by_agent_name(
        self,
        analytics_service: AnalyticsService,
        mock_session: AsyncMock,
        mock_team_instance: TeamInstance,
    ) -> None:
        """Test filtering agent decisions by agent name."""
        team_result = MagicMock()
        team_result.scalar_one_or_none.return_value = mock_team_instance

        decision = MagicMock(spec=AgentDecisionLog)
        decision.id = 1
        decision.team_instance_id = 1
        decision.agent_name = "RiskManager"
        decision.decision_type = "WARNING"
        decision.data = {"reason": "High volatility"}

        activity_result = MagicMock()
        activity_result.scalars.return_value.all.return_value = [decision]

        mock_session.execute.side_effect = [team_result, activity_result]

        activity = await analytics_service.get_agent_activity(
            1, agent_name="RiskManager"
        )

        assert len(activity) == 1
        assert activity[0].agent_name == "RiskManager"

    async def test_get_agent_activity_filter_by_decision_type(
        self,
        analytics_service: AnalyticsService,
        mock_session: AsyncMock,
        mock_team_instance: TeamInstance,
    ) -> None:
        """Test filtering agent decisions by decision type."""
        team_result = MagicMock()
        team_result.scalar_one_or_none.return_value = mock_team_instance

        decisions = [
            MagicMock(spec=AgentDecisionLog),
            MagicMock(spec=AgentDecisionLog),
        ]
        for i, decision in enumerate(decisions):
            decision.id = i + 1
            decision.team_instance_id = 1
            decision.agent_name = "MarketAnalyzer"
            decision.decision_type = "SIGNAL"
            decision.data = {"action": "BUY"}

        activity_result = MagicMock()
        activity_result.scalars.return_value.all.return_value = decisions

        mock_session.execute.side_effect = [team_result, activity_result]

        activity = await analytics_service.get_agent_activity(
            1, decision_type="SIGNAL"
        )

        assert len(activity) == 2
        assert all(d.decision_type == "SIGNAL" for d in activity)

    async def test_get_agent_activity_filter_by_time(
        self,
        analytics_service: AnalyticsService,
        mock_session: AsyncMock,
        mock_team_instance: TeamInstance,
    ) -> None:
        """Test filtering agent decisions by time."""
        team_result = MagicMock()
        team_result.scalar_one_or_none.return_value = mock_team_instance

        decision = MagicMock(spec=AgentDecisionLog)
        decision.id = 1
        decision.team_instance_id = 1
        decision.agent_name = "MarketAnalyzer"
        decision.decision_type = "SIGNAL"
        decision.created_at = datetime.now(UTC)

        activity_result = MagicMock()
        activity_result.scalars.return_value.all.return_value = [decision]

        mock_session.execute.side_effect = [team_result, activity_result]

        since = datetime.now(UTC) - timedelta(hours=1)
        activity = await analytics_service.get_agent_activity(1, since=since)

        assert len(activity) == 1

    async def test_get_agent_activity_combined_filters(
        self,
        analytics_service: AnalyticsService,
        mock_session: AsyncMock,
        mock_team_instance: TeamInstance,
    ) -> None:
        """Test combining multiple filters."""
        team_result = MagicMock()
        team_result.scalar_one_or_none.return_value = mock_team_instance

        activity_result = MagicMock()
        activity_result.scalars.return_value.all.return_value = []

        mock_session.execute.side_effect = [team_result, activity_result]

        since = datetime.now(UTC) - timedelta(hours=1)
        activity = await analytics_service.get_agent_activity(
            1,
            agent_name="RiskManager",
            decision_type="WARNING",
            since=since,
        )

        assert activity == []

    async def test_get_agent_activity_team_not_found(
        self,
        analytics_service: AnalyticsService,
        mock_session: AsyncMock,
    ) -> None:
        """Test getting agent activity for non-existent team raises error."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        with pytest.raises(TeamNotFoundError):
            await analytics_service.get_agent_activity(999)

    async def test_get_agent_activity_empty_result(
        self,
        analytics_service: AnalyticsService,
        mock_session: AsyncMock,
        mock_team_instance: TeamInstance,
    ) -> None:
        """Test getting agent activity with no matching decisions."""
        team_result = MagicMock()
        team_result.scalar_one_or_none.return_value = mock_team_instance

        activity_result = MagicMock()
        activity_result.scalars.return_value.all.return_value = []

        mock_session.execute.side_effect = [team_result, activity_result]

        activity = await analytics_service.get_agent_activity(1)

        assert activity == []


class TestGetActivitySummary:
    """Tests for get_activity_summary method."""

    async def test_get_activity_summary(
        self,
        analytics_service: AnalyticsService,
        mock_session: AsyncMock,
        mock_team_instance: TeamInstance,
    ) -> None:
        """Test getting complete activity summary."""
        # Mock team instance check
        team_result = MagicMock()
        team_result.scalar_one_or_none.return_value = mock_team_instance

        # Mock signal counts (BUY, SELL, HOLD)
        signal_result = MagicMock()
        signal_result.all.return_value = [
            ("BUY", 10),
            ("SELL", 5),
            ("HOLD", 3),
        ]

        # Mock warning/rejection/override counts
        counts_result = MagicMock()
        counts_result.one_or_none.return_value = (2, 1, 3)  # warnings, rejections, overrides

        mock_session.execute.side_effect = [team_result, signal_result, counts_result]

        summary = await analytics_service.get_activity_summary(1)

        assert isinstance(summary, ActivitySummary)
        assert summary.total_signals == 18  # 10 + 5 + 3
        assert summary.buy_signals == 10
        assert summary.sell_signals == 5
        assert summary.hold_signals == 3
        assert summary.warnings == 2
        assert summary.rejections == 1
        assert summary.overrides == 3

    async def test_get_activity_summary_only_buy_signals(
        self,
        analytics_service: AnalyticsService,
        mock_session: AsyncMock,
        mock_team_instance: TeamInstance,
    ) -> None:
        """Test activity summary with only BUY signals."""
        team_result = MagicMock()
        team_result.scalar_one_or_none.return_value = mock_team_instance

        signal_result = MagicMock()
        signal_result.all.return_value = [("BUY", 15)]

        counts_result = MagicMock()
        counts_result.one_or_none.return_value = (0, 0, 0)

        mock_session.execute.side_effect = [team_result, signal_result, counts_result]

        summary = await analytics_service.get_activity_summary(1)

        assert summary.total_signals == 15
        assert summary.buy_signals == 15
        assert summary.sell_signals == 0
        assert summary.hold_signals == 0
        assert summary.warnings == 0
        assert summary.rejections == 0
        assert summary.overrides == 0

    async def test_get_activity_summary_no_signals(
        self,
        analytics_service: AnalyticsService,
        mock_session: AsyncMock,
        mock_team_instance: TeamInstance,
    ) -> None:
        """Test activity summary with no signals but some warnings."""
        team_result = MagicMock()
        team_result.scalar_one_or_none.return_value = mock_team_instance

        signal_result = MagicMock()
        signal_result.all.return_value = []

        counts_result = MagicMock()
        counts_result.one_or_none.return_value = (5, 2, 1)

        mock_session.execute.side_effect = [team_result, signal_result, counts_result]

        summary = await analytics_service.get_activity_summary(1)

        assert summary.total_signals == 0
        assert summary.buy_signals == 0
        assert summary.sell_signals == 0
        assert summary.hold_signals == 0
        assert summary.warnings == 5
        assert summary.rejections == 2
        assert summary.overrides == 1

    async def test_get_activity_summary_no_activity(
        self,
        analytics_service: AnalyticsService,
        mock_session: AsyncMock,
        mock_team_instance: TeamInstance,
    ) -> None:
        """Test activity summary with no decisions at all."""
        team_result = MagicMock()
        team_result.scalar_one_or_none.return_value = mock_team_instance

        signal_result = MagicMock()
        signal_result.all.return_value = []

        counts_result = MagicMock()
        counts_result.one_or_none.return_value = None

        mock_session.execute.side_effect = [team_result, signal_result, counts_result]

        summary = await analytics_service.get_activity_summary(1)

        assert summary.total_signals == 0
        assert summary.buy_signals == 0
        assert summary.sell_signals == 0
        assert summary.hold_signals == 0
        assert summary.warnings == 0
        assert summary.rejections == 0
        assert summary.overrides == 0

    async def test_get_activity_summary_mixed_signals(
        self,
        analytics_service: AnalyticsService,
        mock_session: AsyncMock,
        mock_team_instance: TeamInstance,
    ) -> None:
        """Test activity summary with mixed signal types."""
        team_result = MagicMock()
        team_result.scalar_one_or_none.return_value = mock_team_instance

        signal_result = MagicMock()
        signal_result.all.return_value = [
            ("BUY", 7),
            ("SELL", 7),
        ]

        counts_result = MagicMock()
        counts_result.one_or_none.return_value = (3, 1, 0)

        mock_session.execute.side_effect = [team_result, signal_result, counts_result]

        summary = await analytics_service.get_activity_summary(1)

        assert summary.total_signals == 14
        assert summary.buy_signals == 7
        assert summary.sell_signals == 7
        assert summary.hold_signals == 0
        assert summary.warnings == 3
        assert summary.rejections == 1
        assert summary.overrides == 0

    async def test_get_activity_summary_team_not_found(
        self,
        analytics_service: AnalyticsService,
        mock_session: AsyncMock,
    ) -> None:
        """Test getting activity summary for non-existent team raises error."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        with pytest.raises(TeamNotFoundError):
            await analytics_service.get_activity_summary(999)
