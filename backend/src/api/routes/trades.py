"""Trades REST API endpoints - Story 008-02."""

from datetime import UTC, datetime
from typing import Annotated, Any

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi import status as http_status

from src.api.deps import DbDep
from src.api.schemas.trade import TradeListResponse
from src.db.repositories.team_repo import TeamRepository
from src.db.repositories.trade_repo import TradeRepository

log = structlog.get_logger()

router = APIRouter(prefix="/api/teams", tags=["trades"])


async def get_trade_repo(db: DbDep) -> TradeRepository:
    """Dependency to get trade repository."""
    return TradeRepository(db)


async def get_team_repo(db: DbDep) -> TeamRepository:
    """Dependency to get team repository."""
    return TeamRepository(db)


TradeRepoDep = Annotated[TradeRepository, Depends(get_trade_repo)]
TeamRepoDep = Annotated[TeamRepository, Depends(get_team_repo)]


@router.get("/{team_id}/trades", response_model=TradeListResponse)
async def get_team_trades(
    team_id: int,
    trade_repo: TradeRepoDep,
    team_repo: TeamRepoDep,
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Number of items per page"),
    status: str | None = Query(None, description="Filter by status (open, closed)"),
    symbol: str | None = Query(None, description="Filter by symbol (e.g., EUR/USD)"),
) -> dict[str, Any]:
    """Get paginated list of trades for a team instance.

    Supports filtering by status and symbol, with server-side pagination.
    """
    # Verify team exists
    team = await team_repo.get_by_id(team_id)
    if team is None:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail={"code": "TEAM_NOT_FOUND", "message": f"Team with ID {team_id} not found"},
        )

    # Calculate offset
    offset = (page - 1) * page_size

    # Fetch trades
    trades, total = await trade_repo.get_by_team_id(
        team_id=team_id,
        limit=page_size,
        offset=offset,
        status=status,
        symbol=symbol,
    )

    return {
        "data": trades,
        "meta": {
            "timestamp": datetime.now(UTC).isoformat(),
            "total": total,
            "page": page,
            "page_size": page_size,
        },
    }
