"""FastAPI application entry point."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import socketio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.deps import RedisDep
from src.api.exception_handlers import trading_error_handler, unhandled_exception_handler
from src.api.routes import analytics_router, auth_router, teams_router, templates_router, trades_router
from src.api.websocket import sio
from src.config.settings import get_settings
from src.core.exceptions import TradingError
from src.core.logging import get_logger, setup_logging
from src.core.redis import close_redis_pool
from src.core.scheduler import start_scheduler, stop_scheduler
from src.db.session import async_session_factory

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan handler for startup and shutdown."""
    # Startup
    setup_logging(log_level=settings.log_level, log_format=settings.log_format)
    log = get_logger(__name__)
    log.info(
        "application_startup",
        app_name=settings.app_name,
        environment=settings.environment,
        debug=settings.debug,
        host=settings.api_host,
        port=settings.api_port,
    )

    # Start background scheduler for performance aggregation
    start_scheduler(async_session_factory)
    log.info("background_scheduler_started")

    yield

    # Shutdown
    stop_scheduler()
    log.info("background_scheduler_stopped")
    await close_redis_pool()
    log.info("application_shutdown")


app = FastAPI(
    title="Trade Backend",
    description="Multi-Agent Day-Trading Platform Backend",
    version="0.1.0",
    lifespan=lifespan,
)

# Register exception handlers
app.add_exception_handler(TradingError, trading_error_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

# CORS middleware for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(analytics_router)
app.include_router(auth_router)
app.include_router(teams_router)
app.include_router(templates_router)
app.include_router(trades_router)


@app.get("/health")
async def health_check(redis: RedisDep) -> dict[str, str | dict[str, str]]:
    """Health check endpoint with Redis connectivity check."""
    redis_status = "ok"
    try:
        await redis.ping()
    except Exception:
        redis_status = "error"

    return {
        "status": "ok" if redis_status == "ok" else "degraded",
        "services": {
            "redis": redis_status,
        },
    }


# Wrap FastAPI app with Socket.io ASGI app
socket_app = socketio.ASGIApp(sio, other_asgi_app=app, socketio_path="/ws/socket.io")
