"""Analytics REST API endpoints - Story 006-04."""

from datetime import datetime
from decimal import Decimal
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.api.deps import DbDep
from src.api.schemas.analytics import (
    AgentDecisionResponse,
    PerformanceMetricResponse,
    PerformanceSummary,
)
from src.core.exceptions import TeamNotFoundError
from src.services.analytics import AnalyticsService

log = structlog.get_logger()

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


async def get_analytics_service(db: DbDep) -> AnalyticsService:
    """Dependency to get analytics service."""
    return AnalyticsService(db)


AnalyticsServiceDep = Annotated[AnalyticsService, Depends(get_analytics_service)]


@router.get("/teams/{team_id}/summary", response_model=PerformanceSummary)
async def get_performance_summary(
    team_id: int,
    service: AnalyticsServiceDep,
) -> PerformanceSummary:
    """Get current performance metrics for a team instance.

    Returns a comprehensive summary including P/L, win rate, Sharpe ratio,
    max drawdown, and trade counts.

    Args:
        team_id: Team instance ID

    Returns:
        PerformanceSummary with all current metrics

    Raises:
        404: Team instance not found
    """
    try:
        summary = await service.get_performance_summary(team_id)
        log.info("performance_summary_retrieved", team_id=team_id)
        return summary
    except TeamNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "TEAM_NOT_FOUND", "message": str(e)},
        ) from e


@router.get("/teams/{team_id}/history", response_model=list[PerformanceMetricResponse])
async def get_performance_history(
    team_id: int,
    service: AnalyticsServiceDep,
    period: str = Query(default="daily", description="Time period (hourly, daily, weekly)"),
    since: datetime | None = Query(default=None, description="Start time filter (ISO 8601)"),
    limit: int = Query(default=100, ge=1, le=1000, description="Maximum number of records"),
) -> list[PerformanceMetricResponse]:
    """Get historical performance metrics for a team instance.

    Returns time-series data of performance metrics aggregated by period.

    Args:
        team_id: Team instance ID
        period: Time period filter ('hourly', 'daily', 'weekly')
        since: Optional start time filter (ISO 8601 format)
        limit: Maximum number of records to return (1-1000)

    Returns:
        List of PerformanceMetricResponse instances ordered by timestamp (newest first)

    Raises:
        404: Team instance not found
    """
    try:
        metrics = await service.get_performance_history(
            team_id=team_id,
            period=period,
            start_time=since,
            limit=limit,
        )
        log.info(
            "performance_history_retrieved",
            team_id=team_id,
            period=period,
            count=len(metrics),
        )
        return metrics
    except TeamNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "TEAM_NOT_FOUND", "message": str(e)},
        ) from e


@router.get("/teams/{team_id}/pnl-by-symbol", response_model=dict[str, str])
async def get_pnl_by_symbol(
    team_id: int,
    service: AnalyticsServiceDep,
) -> dict[str, str]:
    """Get P/L breakdown by trading symbol.

    Returns total P/L for each symbol that has been traded by the team.
    Only includes closed trades.

    Args:
        team_id: Team instance ID

    Returns:
        Dictionary mapping symbol to total P/L (as string)

    Raises:
        404: Team instance not found
    """
    try:
        pnl_data = await service.calculate_pnl_by_symbol(team_id)
        # Convert Decimal to string for JSON serialization
        pnl_str = {symbol: str(pnl) for symbol, pnl in pnl_data.items()}
        log.info(
            "pnl_by_symbol_retrieved",
            team_id=team_id,
            symbol_count=len(pnl_str),
        )
        return pnl_str
    except TeamNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "TEAM_NOT_FOUND", "message": str(e)},
        ) from e


@router.get("/teams/{team_id}/activity", response_model=list[AgentDecisionResponse])
async def get_agent_activity(
    team_id: int,
    service: AnalyticsServiceDep,
    agent: str | None = Query(default=None, description="Filter by agent name"),
    type: str | None = Query(default=None, description="Filter by decision type"),
    limit: int = Query(default=100, ge=1, le=1000, description="Maximum number of records"),
) -> list[AgentDecisionResponse]:
    """Get agent decision history for a team instance.

    Returns filtered list of agent decisions including signals, warnings,
    rejections, and overrides.

    Args:
        team_id: Team instance ID
        agent: Optional filter by agent name
        type: Optional filter by decision type (e.g., 'SIGNAL', 'WARNING')
        limit: Maximum number of records to return (1-1000)

    Returns:
        List of AgentDecisionResponse instances ordered by timestamp (newest first)

    Raises:
        404: Team instance not found
    """
    try:
        decisions = await service.get_agent_activity(
            team_id=team_id,
            agent_name=agent,
            decision_type=type,
        )
        # Apply limit after fetching (service doesn't have limit parameter)
        decisions = decisions[:limit]
        log.info(
            "agent_activity_retrieved",
            team_id=team_id,
            agent=agent,
            type=type,
            count=len(decisions),
        )
        return decisions
    except TeamNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "TEAM_NOT_FOUND", "message": str(e)},
        ) from e
