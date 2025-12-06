"""API routes."""

from src.api.routes.analytics import router as analytics_router
from src.api.routes.auth import router as auth_router
from src.api.routes.teams import router as teams_router
from src.api.routes.templates import router as templates_router
from src.api.routes.trades import router as trades_router

__all__ = ["analytics_router", "auth_router", "teams_router", "templates_router", "trades_router"]
