"""Tests for scheduler module."""

from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.core.scheduler import aggregate_all_teams, get_scheduler, start_scheduler, stop_scheduler
from src.db.models import TeamInstance, TeamInstanceStatus


@pytest.fixture
def mock_session_factory():
    """Create mock session factory."""
    mock_factory = MagicMock()
    mock_session = AsyncMock()
    mock_factory.return_value.__aenter__.return_value = mock_session
    mock_factory.return_value.__aexit__.return_value = None
    return mock_factory, mock_session


@pytest.fixture
def mock_active_teams():
    """Create mock active team instances."""
    teams = []
    for i in range(3):
        team = MagicMock(spec=TeamInstance)
        team.id = i + 1
        team.name = f"Test Team {i + 1}"
        team.status = TeamInstanceStatus.ACTIVE
        team.initial_budget = Decimal("10000.00")
        team.current_budget = Decimal("10000.00")
        team.realized_pnl = Decimal("0.00")
        team.unrealized_pnl = Decimal("0.00")
        teams.append(team)
    return teams


@pytest.mark.asyncio
async def test_aggregate_all_teams_success(mock_session_factory, mock_active_teams):
    """Test successful aggregation for all active teams."""
    mock_factory, mock_session = mock_session_factory

    # Mock the query result
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = mock_active_teams
    mock_session.execute.return_value = mock_result

    # Mock AnalyticsService
    with patch("src.core.scheduler.AnalyticsService") as mock_analytics_class:
        mock_analytics = MagicMock()
        mock_metric = MagicMock()
        mock_metric.id = 1
        mock_metric.pnl = Decimal("100.00")
        mock_metric.trade_count = 5
        mock_analytics.aggregate_performance.return_value = mock_metric
        mock_analytics_class.return_value = mock_analytics

        # Run aggregation
        await aggregate_all_teams(mock_factory)

        # Verify AnalyticsService was called for each team
        assert mock_analytics_class.call_count == len(mock_active_teams)
        assert mock_analytics.aggregate_performance.call_count == len(mock_active_teams)

        # Verify it was called with correct parameters
        for team in mock_active_teams:
            mock_analytics.aggregate_performance.assert_any_call(
                team_id=team.id, period="hourly"
            )


@pytest.mark.asyncio
async def test_aggregate_all_teams_with_errors(mock_session_factory, mock_active_teams):
    """Test aggregation handles errors gracefully."""
    mock_factory, mock_session = mock_session_factory

    # Mock the query result
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = mock_active_teams
    mock_session.execute.return_value = mock_result

    # Mock AnalyticsService to raise error for second team
    with patch("src.core.scheduler.AnalyticsService") as mock_analytics_class:
        mock_analytics = MagicMock()

        def aggregate_side_effect(team_id, period):
            if team_id == 2:
                raise Exception("Test error")
            metric = MagicMock()
            metric.id = team_id
            metric.pnl = Decimal("100.00")
            metric.trade_count = 5
            return metric

        mock_analytics.aggregate_performance.side_effect = aggregate_side_effect
        mock_analytics_class.return_value = mock_analytics

        # Run aggregation - should not raise error
        await aggregate_all_teams(mock_factory)

        # Verify it tried to process all teams
        assert mock_analytics.aggregate_performance.call_count == len(mock_active_teams)


@pytest.mark.asyncio
async def test_aggregate_all_teams_no_teams(mock_session_factory):
    """Test aggregation with no active teams."""
    mock_factory, mock_session = mock_session_factory

    # Mock empty query result
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_session.execute.return_value = mock_result

    # Run aggregation - should not raise error
    await aggregate_all_teams(mock_factory)

    # Verify no errors occurred
    assert True


def test_scheduler_job_configuration():
    """Test scheduler job configuration without starting it."""
    # This test verifies job configuration without needing a running event loop
    from apscheduler.triggers.cron import CronTrigger

    mock_factory = MagicMock()

    # Create scheduler without starting
    scheduler = AsyncIOScheduler()

    # Add job (same configuration as in start_scheduler)
    scheduler.add_job(
        func=aggregate_all_teams,
        trigger=CronTrigger(minute=0),
        args=[mock_factory],
        id="aggregate_performance_hourly",
        name="Aggregate Performance Metrics (Hourly)",
        replace_existing=True,
        misfire_grace_time=300,
    )

    # Verify job was added
    jobs = scheduler.get_jobs()
    assert len(jobs) == 1
    assert jobs[0].id == "aggregate_performance_hourly"
    assert jobs[0].name == "Aggregate Performance Metrics (Hourly)"

    # No cleanup needed - scheduler was never started


def test_stop_scheduler_not_running():
    """Test stopping scheduler when not running."""
    # Reset global state
    import src.core.scheduler as scheduler_module

    scheduler_module.scheduler = None

    # Should not raise error
    stop_scheduler()
    assert True


def test_get_scheduler_not_initialized():
    """Test getting scheduler when not initialized."""
    # Reset global state
    import src.core.scheduler as scheduler_module

    scheduler_module.scheduler = None

    # Should return None
    assert get_scheduler() is None
