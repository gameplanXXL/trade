"""Tests for secrets filtering in structured logging."""

import json
import logging
from io import StringIO

import pytest
import structlog

from src.core.logging import (
    SENSITIVE_FIELDS,
    filter_secrets,
    get_logger,
    setup_logging,
)


@pytest.fixture
def capture_logs():
    """Capture log output for testing."""
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setLevel(logging.DEBUG)

    # Get the root logger and configure it
    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(logging.DEBUG)

    # Setup structured logging with JSON output
    setup_logging(log_level="DEBUG", log_format="json")

    yield stream

    # Cleanup
    root_logger.handlers = []


class TestSecretsFiltering:
    """Test suite for secrets filtering in logs."""

    def test_filter_password_field(self, capture_logs):
        """Test that password fields are redacted."""
        logger = get_logger(__name__)
        logger.info("user login", username="john", password="secret123")

        output = capture_logs.getvalue()
        assert "secret123" not in output
        assert "[REDACTED]" in output

    def test_filter_api_key_field(self, capture_logs):
        """Test that api_key fields are redacted."""
        logger = get_logger(__name__)
        logger.info("api call", api_key="sk-1234567890abcdef")

        output = capture_logs.getvalue()
        assert "sk-1234567890abcdef" not in output
        assert "[REDACTED]" in output

    def test_filter_apikey_field(self, capture_logs):
        """Test that apikey fields are redacted (no underscore)."""
        logger = get_logger(__name__)
        logger.info("api call", apikey="myapikey123")

        output = capture_logs.getvalue()
        assert "myapikey123" not in output
        assert "[REDACTED]" in output

    def test_filter_secret_field(self, capture_logs):
        """Test that secret fields are redacted."""
        logger = get_logger(__name__)
        logger.info("config loaded", secret="my-secret-value")

        output = capture_logs.getvalue()
        assert "my-secret-value" not in output
        assert "[REDACTED]" in output

    def test_filter_token_field(self, capture_logs):
        """Test that token fields are redacted."""
        logger = get_logger(__name__)
        logger.info("auth token", token="bearer-token-xyz")

        output = capture_logs.getvalue()
        assert "bearer-token-xyz" not in output
        assert "[REDACTED]" in output

    def test_filter_authorization_field(self, capture_logs):
        """Test that authorization fields are redacted."""
        logger = get_logger(__name__)
        logger.info("request", authorization="Bearer xyz123")

        output = capture_logs.getvalue()
        assert "Bearer xyz123" not in output
        assert "[REDACTED]" in output

    def test_filter_passwd_field(self, capture_logs):
        """Test that passwd fields are redacted."""
        logger = get_logger(__name__)
        logger.info("db connection", passwd="dbpass123")

        output = capture_logs.getvalue()
        assert "dbpass123" not in output
        assert "[REDACTED]" in output

    def test_case_insensitive_filtering(self, capture_logs):
        """Test that filtering is case-insensitive."""
        logger = get_logger(__name__)
        logger.info("test", PASSWORD="Test123", ApiKey="key123", SECRET="sec")

        output = capture_logs.getvalue()
        assert "Test123" not in output
        assert "key123" not in output
        assert "sec" not in output
        assert output.count("[REDACTED]") >= 3

    def test_nested_dict_filtering(self, capture_logs):
        """Test that nested dictionaries are filtered."""
        logger = get_logger(__name__)
        logger.info(
            "nested data",
            config={"database": {"password": "dbpass"}, "api": {"api_key": "key123"}},
        )

        output = capture_logs.getvalue()
        assert "dbpass" not in output
        assert "key123" not in output
        assert "[REDACTED]" in output

    def test_non_sensitive_fields_not_filtered(self, capture_logs):
        """Test that non-sensitive fields are not filtered."""
        logger = get_logger(__name__)
        logger.info("user data", username="john", email="john@example.com", age=30)

        output = capture_logs.getvalue()
        assert "john" in output
        assert "john@example.com" in output
        assert "30" in output

    def test_sensitive_pattern_in_string(self, capture_logs):
        """Test that sensitive patterns in strings are filtered."""
        logger = get_logger(__name__)
        logger.info("config", message="password=secret123 and api_key=abc")

        output = capture_logs.getvalue()
        assert "secret123" not in output
        assert "[REDACTED]" in output

    def test_multiple_sensitive_fields(self, capture_logs):
        """Test filtering multiple sensitive fields at once."""
        logger = get_logger(__name__)
        logger.info(
            "credentials",
            username="admin",
            password="pass123",
            api_key="key456",
            token="tok789",
        )

        output = capture_logs.getvalue()
        assert "admin" in output  # username is not sensitive
        assert "pass123" not in output
        assert "key456" not in output
        assert "tok789" not in output
        assert output.count("[REDACTED]") >= 3

    def test_empty_values(self, capture_logs):
        """Test that empty sensitive values are still filtered."""
        logger = get_logger(__name__)
        logger.info("empty", password="", api_key=None)

        output = capture_logs.getvalue()
        # Should not crash and should still redact
        assert "[REDACTED]" in output or "null" in output

    def test_sensitive_fields_constant(self):
        """Test that SENSITIVE_FIELDS contains required keys."""
        required_fields = {
            "password",
            "api_key",
            "apikey",
            "secret",
            "token",
            "authorization",
        }
        assert required_fields.issubset(SENSITIVE_FIELDS)

    def test_filter_secrets_processor(self):
        """Test the filter_secrets processor directly."""
        event_dict = {
            "event": "test",
            "password": "secret123",
            "username": "john",
            "api_key": "key456",
        }

        filtered = filter_secrets(logging.getLogger(), "info", event_dict)

        assert filtered["password"] == "[REDACTED]"
        assert filtered["api_key"] == "[REDACTED]"
        assert filtered["username"] == "john"
        assert filtered["event"] == "test"

    def test_filter_with_underscores_in_key(self, capture_logs):
        """Test filtering fields with underscores containing sensitive words."""
        logger = get_logger(__name__)
        logger.info("test", user_password="pass123", mt5_api_key="key456")

        output = capture_logs.getvalue()
        assert "pass123" not in output
        assert "key456" not in output
        assert "[REDACTED]" in output

    def test_credential_field(self, capture_logs):
        """Test that credential fields are redacted."""
        logger = get_logger(__name__)
        logger.info("auth", credential="cred123")

        output = capture_logs.getvalue()
        assert "cred123" not in output
        assert "[REDACTED]" in output

    def test_private_key_field(self, capture_logs):
        """Test that private_key fields are redacted."""
        logger = get_logger(__name__)
        logger.info("crypto", private_key="-----BEGIN PRIVATE KEY-----")

        output = capture_logs.getvalue()
        assert "-----BEGIN PRIVATE KEY-----" not in output
        assert "[REDACTED]" in output


class TestLoggingSetup:
    """Test logging configuration."""

    def test_setup_logging_json_format(self):
        """Test JSON format logging setup."""
        setup_logging(log_level="INFO", log_format="json")
        logger = get_logger(__name__)

        # Should not raise exception
        logger.info("test message")

    def test_setup_logging_console_format(self):
        """Test console format logging setup."""
        setup_logging(log_level="DEBUG", log_format="console")
        logger = get_logger(__name__)

        # Should not raise exception
        logger.info("test message")

    def test_get_logger_returns_bound_logger(self):
        """Test that get_logger returns a BoundLogger instance."""
        setup_logging()
        logger = get_logger(__name__)

        # structlog returns a BoundLoggerLazyProxy, not a direct BoundLogger
        # Just verify it has the expected logging methods
        assert hasattr(logger, "info")
        assert hasattr(logger, "error")
        assert hasattr(logger, "debug")

    def test_get_logger_with_name(self):
        """Test that get_logger accepts a name parameter."""
        setup_logging()
        logger = get_logger("test.module")

        # Should not raise exception
        logger.info("test")


class TestRealWorldScenarios:
    """Test real-world logging scenarios."""

    def test_mt5_connection_log(self, capture_logs):
        """Test MT5 connection logging with credentials."""
        logger = get_logger(__name__)
        logger.info(
            "mt5_connection",
            server="MetaQuotes-Demo",
            login="12345",
            password="MyPassword123",
        )

        output = capture_logs.getvalue()
        assert "MyPassword123" not in output
        assert "12345" in output  # login is not sensitive
        assert "MetaQuotes-Demo" in output
        assert "[REDACTED]" in output

    def test_api_request_log(self, capture_logs):
        """Test API request logging with authorization header."""
        logger = get_logger(__name__)
        logger.info(
            "api_request",
            method="POST",
            url="/api/trades",
            headers={"Authorization": "Bearer secret-token"},
        )

        output = capture_logs.getvalue()
        assert "secret-token" not in output
        assert "POST" in output
        assert "/api/trades" in output

    def test_database_config_log(self, capture_logs):
        """Test database configuration logging."""
        logger = get_logger(__name__)
        logger.info(
            "db_config",
            host="localhost",
            port=5432,
            database="trading",
            user="postgres",
            password="postgres123",
        )

        output = capture_logs.getvalue()
        assert "postgres123" not in output
        assert "localhost" in output
        assert "5432" in output
        assert "trading" in output
        assert "postgres" in output

    def test_error_with_sensitive_data(self, capture_logs):
        """Test error logging with sensitive data."""
        logger = get_logger(__name__)
        logger.error(
            "auth_failed",
            username="admin",
            password="wrong_pass",
            error="Invalid credentials",
        )

        output = capture_logs.getvalue()
        assert "wrong_pass" not in output
        assert "admin" in output
        assert "Invalid credentials" in output
