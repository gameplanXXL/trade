"""Background scheduler for periodic tasks."""

from datetime import datetime

import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.db.models import TeamInstance, TeamInstanceStatus
from src.services.analytics import AnalyticsService

log = structlog.get_logger()

# Global scheduler instance
scheduler: AsyncIOScheduler | None = None


async def aggregate_all_teams(session_factory: async_sessionmaker) -> None:
    """Aggregate performance metrics for all active teams.

    This job runs hourly to create performance snapshots for all active teams.
    Each hourly aggregation is stored in the performance_metrics table.

    Args:
        session_factory: SQLAlchemy async session factory
    """
    log.info("performance_aggregation_started", period="hourly")

    async with session_factory() as session:
        # Get all active team instances
        stmt = select(TeamInstance).where(TeamInstance.status == TeamInstanceStatus.ACTIVE)
        result = await session.execute(stmt)
        teams = result.scalars().all()

        success_count = 0
        error_count = 0

        for team in teams:
            try:
                analytics = AnalyticsService(session)
                metric = await analytics.aggregate_performance(
                    team_id=team.id, period="hourly"
                )

                log.info(
                    "team_performance_aggregated",
                    team_id=team.id,
                    team_name=team.name,
                    metric_id=metric.id,
                    pnl=str(metric.pnl),
                    trade_count=metric.trade_count,
                )
                success_count += 1

            except Exception as e:
                log.error(
                    "team_performance_aggregation_failed",
                    team_id=team.id,
                    team_name=team.name,
                    error=str(e),
                    exc_info=True,
                )
                error_count += 1

        log.info(
            "performance_aggregation_completed",
            period="hourly",
            total_teams=len(teams),
            success_count=success_count,
            error_count=error_count,
            timestamp=datetime.now().isoformat(),
        )


def start_scheduler(session_factory: async_sessionmaker) -> AsyncIOScheduler:
    """Start the background scheduler with all scheduled jobs.

    Jobs configured:
    - Hourly performance aggregation (runs at minute 0 of every hour)

    Args:
        session_factory: SQLAlchemy async session factory

    Returns:
        Started scheduler instance
    """
    global scheduler

    if scheduler is not None:
        log.warning("scheduler_already_running")
        return scheduler

    scheduler = AsyncIOScheduler()

    # Add hourly performance aggregation job
    # Runs at the start of every hour (e.g., 00:00, 01:00, 02:00)
    scheduler.add_job(
        func=aggregate_all_teams,
        trigger=CronTrigger(minute=0),  # Every hour at minute 0
        args=[session_factory],
        id="aggregate_performance_hourly",
        name="Aggregate Performance Metrics (Hourly)",
        replace_existing=True,
        misfire_grace_time=300,  # Allow 5 minutes grace for misfired jobs
    )

    scheduler.start()

    log.info(
        "scheduler_started",
        jobs=[
            {
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
            }
            for job in scheduler.get_jobs()
        ],
    )

    return scheduler


def stop_scheduler() -> None:
    """Stop the background scheduler gracefully."""
    global scheduler

    if scheduler is None:
        log.warning("scheduler_not_running")
        return

    scheduler.shutdown(wait=True)
    scheduler = None

    log.info("scheduler_stopped")


def get_scheduler() -> AsyncIOScheduler | None:
    """Get the current scheduler instance.

    Returns:
        Current scheduler instance or None if not started
    """
    return scheduler
