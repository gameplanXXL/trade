"""Custom exception hierarchy for the trading platform."""


class TradingError(Exception):
    """Base exception for all trading-related errors."""

    code: str = "TRADING_ERROR"

    def __init__(self, message: str, details: dict | None = None) -> None:
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class MT5ConnectionError(TradingError):
    """Error connecting to MetaTrader 5."""

    code = "MT5_CONNECTION_ERROR"


class PipelineError(TradingError):
    """Error in agent pipeline execution."""

    code = "PIPELINE_ERROR"


class TeamNotFoundError(TradingError):
    """Team not found in database."""

    code = "TEAM_NOT_FOUND"


class ValidationError(TradingError):
    """Input validation error."""

    code = "VALIDATION_ERROR"


class ConfigurationError(TradingError):
    """Configuration error."""

    code = "CONFIGURATION_ERROR"
