"""Retry utilities for LLM API calls."""

from typing import Any

import structlog
from anthropic import APIConnectionError, APIStatusError, RateLimitError
from tenacity import (
    RetryCallState,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

log = structlog.get_logger()


def log_retry_attempt(retry_state: RetryCallState) -> None:
    """Log retry attempts with structured logging.

    Args:
        retry_state: State of the retry attempt from tenacity.
    """
    exception = retry_state.outcome.exception() if retry_state.outcome else None
    log.warning(
        "llm_retry",
        attempt=retry_state.attempt_number,
        error=str(exception) if exception else "unknown",
        error_type=type(exception).__name__ if exception else "unknown",
    )


def llm_retry_decorator(**kwargs: Any):
    """Create a retry decorator for LLM API calls.

    Retry configuration:
    - 3 attempts maximum
    - Exponential backoff: 2s, 4s, 8s (multiplier=1, min=2, max=10)
    - Retry on: Rate limiting (429), Server errors (5xx), Connection errors, Timeouts

    Args:
        **kwargs: Additional arguments to pass to the retry decorator.

    Returns:
        Configured retry decorator.
    """
    return retry(
        stop=stop_after_attempt(kwargs.get("max_attempts", 3)),
        wait=wait_exponential(
            multiplier=kwargs.get("multiplier", 1),
            min=kwargs.get("min_wait", 2),
            max=kwargs.get("max_wait", 10),
        ),
        retry=retry_if_exception_type(
            (
                RateLimitError,  # 429 Too Many Requests
                APIStatusError,  # 5xx Server Errors
                APIConnectionError,  # Connection issues
                TimeoutError,  # Timeout errors
            )
        ),
        before_sleep=log_retry_attempt,
        reraise=True,
    )
