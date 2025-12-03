"""FastAPI application entry point."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.exception_handlers import trading_error_handler, unhandled_exception_handler
from src.config.settings import get_settings
from src.core.exceptions import TradingError
from src.core.logging import get_logger, setup_logging

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
        debug=settings.debug,
        host=settings.host,
        port=settings.port,
    )
    yield
    # Shutdown
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


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}
