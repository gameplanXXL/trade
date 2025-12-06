"""Team API schemas for request/response models - Story 005-03."""

from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from src.db.models import TeamInstanceMode, TeamInstanceStatus


class TeamInstanceCreate(BaseModel):
    """Internal schema for creating team instances in repository layer."""

    name: str
    template_name: str
    symbols: list[str]
    initial_budget: Decimal
    mode: TeamInstanceMode = TeamInstanceMode.PAPER


class TeamCreate(BaseModel):
    """Request schema for creating a new team instance."""

    name: str = Field(..., min_length=1, max_length=100, description="Display name")
    template_name: str = Field(
        ..., min_length=1, max_length=100, description="YAML template file name"
    )
    symbols: list[str] = Field(
        ..., min_length=1, description="Trading symbols (canonical: EUR/USD)"
    )
    budget: Decimal = Field(
        ..., gt=0, description="Initial budget for the team", examples=[10000.00]
    )
    mode: TeamInstanceMode = Field(
        default=TeamInstanceMode.PAPER, description="Trading mode"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Conservative LLM Team",
                "template_name": "conservative_llm",
                "symbols": ["EUR/USD", "GBP/USD"],
                "budget": 10000.00,
                "mode": "paper",
            }
        }
    )


class TeamResponse(BaseModel):
    """Response schema for team instance basic info."""

    id: int
    name: str
    template_name: str
    status: TeamInstanceStatus
    mode: TeamInstanceMode
    symbols: list[str]
    initial_budget: Decimal
    current_budget: Decimal
    realized_pnl: Decimal
    unrealized_pnl: Decimal
    created_at: datetime
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class TeamDetailResponse(TeamResponse):
    """Extended response schema with additional details."""

    total_pnl: Decimal = Field(
        default=Decimal("0.00"), description="Total P/L (realized + unrealized)"
    )
    trade_count: int = Field(default=0, description="Number of trades executed")
    open_positions: int = Field(default=0, description="Number of open positions")

    @classmethod
    def from_team(
        cls,
        team: Any,
        trade_count: int = 0,
        open_positions: int = 0,
    ) -> "TeamDetailResponse":
        """Create detail response from team instance with computed fields.

        Args:
            team: TeamInstance model.
            trade_count: Number of trades (computed externally).
            open_positions: Number of open positions (computed externally).

        Returns:
            TeamDetailResponse with all fields populated.
        """
        return cls(
            id=team.id,
            name=team.name,
            template_name=team.template_name,
            status=team.status,
            mode=team.mode,
            symbols=team.symbols,
            initial_budget=team.initial_budget,
            current_budget=team.current_budget,
            realized_pnl=team.realized_pnl,
            unrealized_pnl=team.unrealized_pnl,
            created_at=team.created_at,
            updated_at=team.updated_at,
            total_pnl=team.realized_pnl + team.unrealized_pnl,
            trade_count=trade_count,
            open_positions=open_positions,
        )


class TeamListResponse(BaseModel):
    """Response schema for list of teams with metadata."""

    data: list[TeamResponse]
    meta: dict[str, Any] = Field(
        default_factory=lambda: {"timestamp": datetime.utcnow().isoformat() + "Z"}
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "data": [
                    {
                        "id": 1,
                        "name": "Conservative LLM Team",
                        "template_name": "conservative_llm",
                        "status": "active",
                        "mode": "paper",
                        "symbols": ["EUR/USD"],
                        "initial_budget": 10000.00,
                        "current_budget": 10250.50,
                        "realized_pnl": 250.50,
                        "unrealized_pnl": 0.00,
                        "created_at": "2025-12-01T10:00:00Z",
                        "updated_at": "2025-12-01T12:30:00Z",
                    }
                ],
                "meta": {"timestamp": "2025-12-01T12:45:00Z"},
            }
        }
    )


class ErrorResponse(BaseModel):
    """Standard error response schema."""

    error: dict[str, Any] = Field(
        ...,
        description="Error details",
        examples=[{"code": "TEAM_NOT_FOUND", "message": "Team with ID 123 not found"}],
    )
