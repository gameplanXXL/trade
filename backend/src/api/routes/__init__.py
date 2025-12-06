"""API routes."""

from src.api.routes.analytics import router as analytics_router
from src.api.routes.teams import router as teams_router
from src.api.routes.trades import router as trades_router

__all__ = ["analytics_router", "teams_router", "trades_router"]
