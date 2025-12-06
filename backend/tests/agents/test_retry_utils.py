"""Tests for retry_utils module."""

from unittest.mock import MagicMock, patch

import pytest
from anthropic import APIConnectionError, APIStatusError, RateLimitError
from tenacity import RetryCallState

from src.agents.retry_utils import llm_retry_decorator, log_retry_attempt


class TestLogRetryAttempt:
    """Tests for log_retry_attempt function."""

    def test_log_retry_attempt_with_exception(self) -> None:
        """Test logging a retry attempt with an exception."""
        # Create a mock retry state
        retry_state = MagicMock()
        retry_state.attempt_number = 2

        # Create a mock outcome with an exception
        exception = RateLimitError("Rate limit exceeded", response=MagicMock(), body={})
        mock_outcome = MagicMock()
        mock_outcome.exception.return_value = exception
        retry_state.outcome = mock_outcome

        with patch("src.agents.retry_utils.log") as mock_log:
            log_retry_attempt(retry_state)

            mock_log.warning.assert_called_once()
            call_args = mock_log.warning.call_args

            # Check that correct event and attributes were logged
            assert call_args[0][0] == "llm_retry"
            assert call_args[1]["attempt"] == 2
            assert "Rate limit exceeded" in call_args[1]["error"]
            assert call_args[1]["error_type"] == "RateLimitError"

    def test_log_retry_attempt_without_exception(self) -> None:
        """Test logging when outcome has no exception."""
        retry_state = MagicMock(spec=RetryCallState)
        retry_state.attempt_number = 1
        retry_state.outcome = None

        with patch("src.agents.retry_utils.log") as mock_log:
            log_retry_attempt(retry_state)

            mock_log.warning.assert_called_once()
            call_args = mock_log.warning.call_args

            assert call_args[1]["error"] == "unknown"
            assert call_args[1]["error_type"] == "unknown"


class TestLLMRetryDecorator:
    """Tests for llm_retry_decorator function."""

    def test_decorator_defaults(self) -> None:
        """Test that decorator is created with default values."""
        decorator = llm_retry_decorator()

        assert decorator is not None
        # Decorator should be configured (we can't easily test internals)

    def test_decorator_custom_values(self) -> None:
        """Test decorator with custom retry configuration."""
        decorator = llm_retry_decorator(
            max_attempts=5,
            multiplier=2,
            min_wait=1,
            max_wait=20,
        )

        assert decorator is not None

    @pytest.mark.asyncio
    async def test_decorator_retries_on_rate_limit(self) -> None:
        """Test that decorator retries on RateLimitError."""
        call_count = 0

        @llm_retry_decorator()
        async def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise RateLimitError("Rate limit", response=MagicMock(), body={})
            return "success"

        result = await failing_function()

        assert result == "success"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_decorator_retries_on_api_status_error(self) -> None:
        """Test that decorator retries on APIStatusError."""
        call_count = 0

        @llm_retry_decorator()
        async def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise APIStatusError("Server error", response=MagicMock(), body={})
            return "success"

        result = await failing_function()

        assert result == "success"
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_decorator_retries_on_connection_error(self) -> None:
        """Test that decorator retries on APIConnectionError."""
        call_count = 0

        @llm_retry_decorator()
        async def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise APIConnectionError(request=MagicMock())
            return "success"

        result = await failing_function()

        assert result == "success"
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_decorator_retries_on_timeout(self) -> None:
        """Test that decorator retries on TimeoutError."""
        call_count = 0

        @llm_retry_decorator()
        async def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise TimeoutError("Timeout")
            return "success"

        result = await failing_function()

        assert result == "success"
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_decorator_fails_after_max_attempts(self) -> None:
        """Test that decorator raises error after max attempts."""

        @llm_retry_decorator(max_attempts=2)
        async def always_failing_function():
            raise RateLimitError("Rate limit", response=MagicMock(), body={})

        with pytest.raises(RateLimitError):
            await always_failing_function()

    @pytest.mark.asyncio
    async def test_decorator_does_not_retry_other_errors(self) -> None:
        """Test that decorator does not retry non-retryable errors."""
        call_count = 0

        @llm_retry_decorator()
        async def failing_function():
            nonlocal call_count
            call_count += 1
            raise ValueError("Not retryable")

        with pytest.raises(ValueError):
            await failing_function()

        # Should only be called once (no retries)
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_decorator_logs_retries(self) -> None:
        """Test that decorator logs retry attempts."""
        call_count = 0

        @llm_retry_decorator()
        async def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise RateLimitError("Rate limit", response=MagicMock(), body={})
            return "success"

        with patch("src.agents.retry_utils.log") as mock_log:
            result = await failing_function()

            assert result == "success"
            # Should have logged the retry
            mock_log.warning.assert_called()
