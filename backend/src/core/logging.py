"""Structured logging configuration using structlog."""

import logging
import re
import sys
from typing import Any

import structlog

# Sensitive field names that should be filtered from logs
SENSITIVE_FIELDS = frozenset({
    "password",
    "api_key",
    "apikey",
    "secret",
    "token",
    "authorization",
    "credential",
    "private_key",
})

# Pattern to match sensitive values in strings
SENSITIVE_PATTERN = re.compile(
    r'(password|api_key|apikey|secret|token|authorization|credential|private_key)'
    r'\s*[=:]\s*["\']?([^"\'\s,}]+)["\']?',
    re.IGNORECASE,
)


def _mask_value(value: str) -> str:
    """Mask a sensitive value, showing only first 2 chars."""
    if len(value) <= 4:
        return "***"
    return value[:2] + "***"


def filter_secrets(
    logger: logging.Logger, method_name: str, event_dict: dict[str, Any]
) -> dict[str, Any]:
    """Filter sensitive data from log events.

    This processor removes or masks sensitive fields like passwords,
    API keys, tokens, and secrets from log output.
    """
    for key, value in list(event_dict.items()):
        key_lower = key.lower()

        # Check if key matches sensitive field names
        if any(sensitive in key_lower for sensitive in SENSITIVE_FIELDS):
            event_dict[key] = "[REDACTED]"
        elif isinstance(value, str):
            # Check for sensitive patterns in string values
            event_dict[key] = SENSITIVE_PATTERN.sub(
                lambda m: f"{m.group(1)}=[REDACTED]", value
            )
        elif isinstance(value, dict):
            # Recursively filter nested dicts
            event_dict[key] = _filter_dict(value)

    return event_dict


def _filter_dict(d: dict[str, Any]) -> dict[str, Any]:
    """Recursively filter sensitive data from a dictionary."""
    result = {}
    for key, value in d.items():
        key_lower = key.lower()
        if any(sensitive in key_lower for sensitive in SENSITIVE_FIELDS):
            result[key] = "[REDACTED]"
        elif isinstance(value, dict):
            result[key] = _filter_dict(value)
        elif isinstance(value, str):
            result[key] = SENSITIVE_PATTERN.sub(
                lambda m: f"{m.group(1)}=[REDACTED]", value
            )
        else:
            result[key] = value
    return result


def setup_logging(log_level: str = "INFO", log_format: str = "json") -> None:
    """Configure structured logging for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Output format ("json" or "console")
    """
    # Set up standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )

    # Shared processors
    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
        filter_secrets,  # Filter sensitive data before output
    ]

    if log_format == "json":
        # JSON output for production
        processors = [
            *shared_processors,
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ]
    else:
        # Console output for development
        processors = [
            *shared_processors,
            structlog.dev.ConsoleRenderer(colors=True),
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)
