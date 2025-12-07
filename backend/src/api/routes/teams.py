"""Teams REST API endpoints - Story 005-03."""

from datetime import UTC, datetime
from typing import Annotated, Any

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select

from src.api.deps import DbDep
from src.api.schemas.team import (
    TeamCreate,
    TeamDetailResponse,
    TeamDetailWrapper,
    TeamInstanceCreate,
    TeamListResponse,
    TeamResponse,
)
from src.db.models import TeamInstance, TeamInstanceStatus, Trade
from src.db.repositories.team_repo import TeamRepository
from src.db.repositories.trade_repo import TradeRepository

log = structlog.get_logger()

router = APIRouter(prefix="/api/teams", tags=["teams"])


async def get_team_repo(db: DbDep) -> TeamRepository:
    """Dependency to get team repository."""
    return TeamRepository(db)


TeamRepoDep = Annotated[TeamRepository, Depends(get_team_repo)]


@router.post("/", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(data: TeamCreate, repo: TeamRepoDep, db: DbDep) -> TeamInstance:
    """Create a new team instance.

    Creates a team in STOPPED status, ready to be started.
    """
    # Convert API schema to repository schema
    repo_data = TeamInstanceCreate(
        name=data.name,
        template_name=data.template_name,
        symbols=data.symbols,
        initial_budget=data.budget,
        mode=data.mode,
    )
    team = await repo.create(repo_data)
    await db.commit()
    return team


@router.get("/", response_model=TeamListResponse)
async def list_teams(
    repo: TeamRepoDep,
    status_filter: TeamInstanceStatus | None = None,
) -> dict[str, Any]:
    """List all team instances.

    Optionally filter by status (active, paused, stopped).
    """
    teams = await repo.get_all(status=status_filter)
    return {
        "data": teams,
        "meta": {"timestamp": datetime.now(UTC).isoformat()},
    }


@router.get("/{team_id}", response_model=TeamDetailWrapper)
async def get_team(team_id: int, repo: TeamRepoDep, db: DbDep) -> dict[str, Any]:
    """Get detailed information about a team instance.

    Includes trade count and open position count.
    """
    team = await repo.get_by_id(team_id)
    if team is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "TEAM_NOT_FOUND", "message": f"Team with ID {team_id} not found"},
        )

    # Count trades
    trade_count_result = await db.execute(
        select(func.count(Trade.id)).where(Trade.team_instance_id == team_id)
    )
    trade_count = trade_count_result.scalar() or 0

    # Count open positions
    open_positions_result = await db.execute(
        select(func.count(Trade.id)).where(
            Trade.team_instance_id == team_id, Trade.status == "open"
        )
    )
    open_positions = open_positions_result.scalar() or 0

    team_detail = TeamDetailResponse.from_team(
        team, trade_count=trade_count, open_positions=open_positions
    )

    return {
        "data": team_detail,
        "meta": {"timestamp": datetime.now(UTC).isoformat()},
    }


@router.patch("/{team_id}/start", response_model=TeamResponse)
async def start_team(team_id: int, repo: TeamRepoDep, db: DbDep) -> TeamInstance:
    """Start a team instance.

    Transitions from STOPPED or PAUSED to ACTIVE.
    Initiates the trading pipeline.
    """
    team = await repo.get_by_id(team_id)
    if team is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "TEAM_NOT_FOUND", "message": f"Team with ID {team_id} not found"},
        )

    if team.status == TeamInstanceStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "ALREADY_ACTIVE", "message": "Team is already active"},
        )

    team = await repo.update_status(team_id, TeamInstanceStatus.ACTIVE)
    await db.commit()

    log.info("team_started", team_id=team_id, name=team.name)
    return team


@router.patch("/{team_id}/pause", response_model=TeamResponse)
async def pause_team(team_id: int, repo: TeamRepoDep, db: DbDep) -> TeamInstance:
    """Pause a team instance.

    Transitions from ACTIVE to PAUSED.
    Keeps positions open but stops new trades.
    """
    team = await repo.get_by_id(team_id)
    if team is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "TEAM_NOT_FOUND", "message": f"Team with ID {team_id} not found"},
        )

    if team.status != TeamInstanceStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "NOT_ACTIVE", "message": "Can only pause active teams"},
        )

    team = await repo.update_status(team_id, TeamInstanceStatus.PAUSED)
    await db.commit()

    log.info("team_paused", team_id=team_id, name=team.name)
    return team


@router.patch("/{team_id}/stop", response_model=TeamResponse)
async def stop_team(team_id: int, repo: TeamRepoDep, db: DbDep) -> TeamInstance:
    """Stop a team instance.

    Transitions to STOPPED status.
    Note: Does not close positions automatically (done by lifecycle manager).
    """
    team = await repo.get_by_id(team_id)
    if team is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "TEAM_NOT_FOUND", "message": f"Team with ID {team_id} not found"},
        )

    if team.status == TeamInstanceStatus.STOPPED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "ALREADY_STOPPED", "message": "Team is already stopped"},
        )

    team = await repo.update_status(team_id, TeamInstanceStatus.STOPPED)
    await db.commit()

    log.info("team_stopped", team_id=team_id, name=team.name)
    return team


@router.post("/{team_id}/positions/close", status_code=status.HTTP_200_OK)
async def close_positions(team_id: int, repo: TeamRepoDep, db: DbDep) -> dict[str, Any]:
    """Close all open positions for a team.

    Does not stop the team - it continues running but with no open positions.
    """
    team = await repo.get_by_id(team_id)
    if team is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "TEAM_NOT_FOUND", "message": f"Team with ID {team_id} not found"},
        )

    # Get all open trades for the team
    trade_repo = TradeRepository(db)
    open_trades = await trade_repo.get_open_trades(team_id)

    if not open_trades:
        log.info("no_open_positions_to_close", team_id=team_id)
        return {
            "data": {"closed_count": 0},
            "meta": {"timestamp": datetime.now(UTC).isoformat()},
        }

    log.info(
        "closing_all_positions",
        team_id=team_id,
        open_position_count=len(open_trades),
    )

    # Close each position
    # TODO: Replace with actual MT5 position closing when MT5 integration is ready
    # For now, we just mark them as closed in the database
    for trade in open_trades:
        trade.status = "closed"
        trade.closed_at = datetime.now(UTC)
        # Set exit_price to entry_price for now (will be replaced with actual market price)
        if trade.exit_price is None:
            trade.exit_price = trade.entry_price
            trade.pnl = 0  # Zero P/L for manual closes

    await db.commit()

    log.info(
        "positions_closed",
        team_id=team_id,
        closed_count=len(open_trades),
    )

    return {
        "data": {"closed_count": len(open_trades)},
        "meta": {"timestamp": datetime.now(UTC).isoformat()},
    }


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(team_id: int, repo: TeamRepoDep, db: DbDep) -> None:
    """Stop and delete a team instance permanently.

    Automatically stops the team if it's not already stopped, then deletes it.
    This is a destructive operation that cannot be undone.
    """
    team = await repo.get_by_id(team_id)
    if team is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "TEAM_NOT_FOUND", "message": f"Team with ID {team_id} not found"},
        )

    # Stop the team first if it's not already stopped
    if team.status != TeamInstanceStatus.STOPPED:
        await repo.update_status(team_id, TeamInstanceStatus.STOPPED)
        log.info("team_stopped_for_deletion", team_id=team_id, name=team.name)

    await repo.delete(team_id)
    await db.commit()
    log.info("team_deleted", team_id=team_id)
