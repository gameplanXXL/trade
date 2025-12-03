"""FastAPI exception handlers for consistent error responses."""

from fastapi import Request
from fastapi.responses import JSONResponse

from src.core.exceptions import TradingError
from src.core.logging import get_logger

log = get_logger(__name__)


async def trading_error_handler(request: Request, exc: TradingError) -> JSONResponse:
    """Handle TradingError and subclasses with structured JSON response."""
    log.warning(
        "trading_error",
        error_code=exc.code,
        message=exc.message,
        details=exc.details,
        path=str(request.url.path),
        method=request.method,
    )

    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                **({"details": exc.details} if exc.details else {}),
            }
        },
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions with generic error response."""
    log.exception(
        "unhandled_exception",
        exception_type=type(exc).__name__,
        message=str(exc),
        path=str(request.url.path),
        method=request.method,
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
            }
        },
    )
