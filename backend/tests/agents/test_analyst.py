"""Tests for LLMSignalAnalyst agent."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.agents.analyst import (
    LLMAnalystError,
    LLMSignalAnalyst,
    LLMSignalResponse,
    SignalAction,
)
from src.agents.base import AgentDecision, AgentStatus


class TestSignalAction:
    """Tests for SignalAction enum."""

    def test_signal_action_values(self) -> None:
        """Test that all expected signal actions exist."""
        assert SignalAction.BUY == "BUY"
        assert SignalAction.SELL == "SELL"
        assert SignalAction.HOLD == "HOLD"


class TestLLMSignalResponse:
    """Tests for LLMSignalResponse model."""

    def test_valid_response(self) -> None:
        """Test creating a valid signal response."""
        response = LLMSignalResponse(
            action=SignalAction.BUY,
            confidence=0.85,
            reasoning="Strong upward momentum",
        )

        assert response.action == SignalAction.BUY
        assert response.confidence == 0.85
        assert response.reasoning == "Strong upward momentum"

    def test_confidence_bounds(self) -> None:
        """Test that confidence must be between 0 and 1."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            LLMSignalResponse(
                action=SignalAction.BUY,
                confidence=1.5,
                reasoning="test",
            )

        with pytest.raises(ValidationError):
            LLMSignalResponse(
                action=SignalAction.SELL,
                confidence=-0.1,
                reasoning="test",
            )


class TestLLMSignalAnalystConfiguration:
    """Tests for LLMSignalAnalyst configuration."""

    def test_default_configuration(self) -> None:
        """Test default configuration values."""
        analyst = LLMSignalAnalyst(params={})

        assert analyst.model == "claude-sonnet-4-20250514"
        assert analyst.min_confidence == 0.7
        assert analyst.lookback == 14
        assert analyst.timeout == 30
        assert analyst.max_retries == 3

    def test_custom_configuration(self) -> None:
        """Test custom configuration values."""
        analyst = LLMSignalAnalyst(
            params={
                "model": "claude-3-opus-20240229",
                "min_confidence": 0.8,
                "lookback": 7,
                "timeout": 60,
                "max_retries": 5,
            }
        )

        assert analyst.model == "claude-3-opus-20240229"
        assert analyst.min_confidence == 0.8
        assert analyst.lookback == 7
        assert analyst.timeout == 60
        assert analyst.max_retries == 5

    def test_agent_name(self) -> None:
        """Test that agent name is set correctly."""
        analyst = LLMSignalAnalyst(params={})
        assert analyst.name == "analyst"

    def test_initial_status(self) -> None:
        """Test that agent starts with NORMAL status."""
        analyst = LLMSignalAnalyst(params={})
        assert analyst.status == AgentStatus.NORMAL


class TestLLMSignalAnalystPromptBuilding:
    """Tests for prompt building."""

    @pytest.fixture
    def analyst(self) -> LLMSignalAnalyst:
        """Create an analyst instance."""
        return LLMSignalAnalyst(params={})

    def test_build_prompt_with_full_context(self, analyst: LLMSignalAnalyst) -> None:
        """Test prompt building with full context."""
        context = {
            "market_data": {
                "symbol": "EURUSD",
                "current_price": 1.0850,
                "price_change_24h": 0.5,
                "volume": 1000000,
            },
            "indicators": {
                "rsi": 55,
                "ma_20": 1.0800,
                "ma_50": 1.0750,
                "macd": 0.0025,
            },
            "crash_detector_status": "normal",
            "historical_performance": {
                "win_rate": 65,
                "recent_trades": 10,
            },
        }

        prompt = analyst._build_prompt(context)

        assert "EURUSD" in prompt
        assert "1.085" in prompt  # Python may strip trailing zero
        assert "RSI: 55" in prompt
        assert "Crash Detector Status: normal" in prompt
        assert "Win Rate: 65" in prompt
        assert "JSON" in prompt

    def test_build_prompt_with_empty_context(self, analyst: LLMSignalAnalyst) -> None:
        """Test prompt building with empty context."""
        context = {}

        prompt = analyst._build_prompt(context)

        assert "Unknown" in prompt
        assert "N/A" in prompt


class TestLLMSignalAnalystResponseParsing:
    """Tests for response parsing."""

    @pytest.fixture
    def analyst(self) -> LLMSignalAnalyst:
        """Create an analyst instance."""
        return LLMSignalAnalyst(params={})

    def test_parse_valid_json_response(self, analyst: LLMSignalAnalyst) -> None:
        """Test parsing valid JSON response."""
        response = '{"action": "BUY", "confidence": 0.85, "reasoning": "Strong signal"}'

        result = analyst._parse_response(response)

        assert result.action == SignalAction.BUY
        assert result.confidence == 0.85
        assert result.reasoning == "Strong signal"

    def test_parse_json_in_code_block(self, analyst: LLMSignalAnalyst) -> None:
        """Test parsing JSON wrapped in markdown code block."""
        response = """```json
{"action": "SELL", "confidence": 0.75, "reasoning": "Bearish trend"}
```"""

        result = analyst._parse_response(response)

        assert result.action == SignalAction.SELL
        assert result.confidence == 0.75

    def test_parse_invalid_json_raises_error(self, analyst: LLMSignalAnalyst) -> None:
        """Test that invalid JSON raises LLMAnalystError."""
        response = "This is not valid JSON"

        with pytest.raises(LLMAnalystError) as exc_info:
            analyst._parse_response(response)

        assert "parse" in str(exc_info.value).lower()

    def test_parse_missing_fields_raises_error(self, analyst: LLMSignalAnalyst) -> None:
        """Test that missing required fields raise error."""
        response = '{"action": "BUY"}'  # Missing confidence and reasoning

        with pytest.raises(LLMAnalystError):
            analyst._parse_response(response)


class TestLLMSignalAnalystGenerateSignal:
    """Tests for generate_signal method."""

    @pytest.fixture
    def analyst(self) -> LLMSignalAnalyst:
        """Create an analyst instance."""
        return LLMSignalAnalyst(params={"min_confidence": 0.7})

    @pytest.fixture
    def mock_llm_response(self) -> str:
        """Provide a mock LLM response."""
        return '{"action": "BUY", "confidence": 0.85, "reasoning": "Strong upward momentum"}'

    @pytest.mark.asyncio
    async def test_generate_signal_returns_agent_decision(
        self, analyst: LLMSignalAnalyst, mock_llm_response: str
    ) -> None:
        """Test that generate_signal returns an AgentDecision."""
        with patch.object(
            analyst, "_call_llm_with_retry", new_callable=AsyncMock
        ) as mock_call:
            mock_call.return_value = mock_llm_response

            result = await analyst.generate_signal({"market_data": {}})

            assert isinstance(result, AgentDecision)
            assert result.agent_name == "analyst"
            assert result.decision_type == "signal"

    @pytest.mark.asyncio
    async def test_generate_signal_includes_action(
        self, analyst: LLMSignalAnalyst, mock_llm_response: str
    ) -> None:
        """Test that decision includes action."""
        with patch.object(
            analyst, "_call_llm_with_retry", new_callable=AsyncMock
        ) as mock_call:
            mock_call.return_value = mock_llm_response

            result = await analyst.generate_signal({"market_data": {}})

            assert result.data["action"] == "BUY"

    @pytest.mark.asyncio
    async def test_generate_signal_includes_confidence(
        self, analyst: LLMSignalAnalyst, mock_llm_response: str
    ) -> None:
        """Test that decision includes confidence."""
        with patch.object(
            analyst, "_call_llm_with_retry", new_callable=AsyncMock
        ) as mock_call:
            mock_call.return_value = mock_llm_response

            result = await analyst.generate_signal({"market_data": {}})

            assert result.data["confidence"] == 0.85
            assert result.confidence == 0.85

    @pytest.mark.asyncio
    async def test_generate_signal_includes_reasoning(
        self, analyst: LLMSignalAnalyst, mock_llm_response: str
    ) -> None:
        """Test that decision includes reasoning."""
        with patch.object(
            analyst, "_call_llm_with_retry", new_callable=AsyncMock
        ) as mock_call:
            mock_call.return_value = mock_llm_response

            result = await analyst.generate_signal({"market_data": {}})

            assert result.data["reasoning"] == "Strong upward momentum"

    @pytest.mark.asyncio
    async def test_generate_signal_includes_meets_threshold(
        self, analyst: LLMSignalAnalyst, mock_llm_response: str
    ) -> None:
        """Test that decision includes meets_threshold."""
        with patch.object(
            analyst, "_call_llm_with_retry", new_callable=AsyncMock
        ) as mock_call:
            mock_call.return_value = mock_llm_response

            result = await analyst.generate_signal({"market_data": {}})

            assert result.data["meets_threshold"] is True
            assert result.data["min_confidence"] == 0.7

    @pytest.mark.asyncio
    async def test_generate_signal_below_threshold(
        self, analyst: LLMSignalAnalyst
    ) -> None:
        """Test signal below confidence threshold."""
        low_confidence_response = (
            '{"action": "BUY", "confidence": 0.5, "reasoning": "Weak signal"}'
        )
        with patch.object(
            analyst, "_call_llm_with_retry", new_callable=AsyncMock
        ) as mock_call:
            mock_call.return_value = low_confidence_response

            result = await analyst.generate_signal({"market_data": {}})

            assert result.data["meets_threshold"] is False

    @pytest.mark.asyncio
    async def test_generate_signal_handles_error(
        self, analyst: LLMSignalAnalyst
    ) -> None:
        """Test that errors are handled gracefully."""
        with patch.object(
            analyst, "_call_llm_with_retry", new_callable=AsyncMock
        ) as mock_call:
            mock_call.side_effect = LLMAnalystError("API Error")

            result = await analyst.generate_signal({"market_data": {}})

            assert result.decision_type == "warning"
            assert result.data["action"] == "HOLD"
            assert result.data["confidence"] == 0.0
            assert "error" in result.data

    @pytest.mark.asyncio
    async def test_execute_calls_generate_signal(
        self, analyst: LLMSignalAnalyst, mock_llm_response: str
    ) -> None:
        """Test that execute() is an alias for generate_signal()."""
        with patch.object(
            analyst, "_call_llm_with_retry", new_callable=AsyncMock
        ) as mock_call:
            mock_call.return_value = mock_llm_response

            result = await analyst.execute({"market_data": {}})

            assert isinstance(result, AgentDecision)
            assert result.data["action"] == "BUY"


class TestLLMSignalAnalystStatusUpdates:
    """Tests for status updates based on confidence."""

    @pytest.mark.asyncio
    async def test_status_normal_high_confidence(self) -> None:
        """Test NORMAL status with high confidence."""
        analyst = LLMSignalAnalyst(params={"min_confidence": 0.7})
        response = '{"action": "BUY", "confidence": 0.85, "reasoning": "Strong"}'

        with patch.object(
            analyst, "_call_llm_with_retry", new_callable=AsyncMock
        ) as mock_call:
            mock_call.return_value = response

            await analyst.generate_signal({})

            assert analyst.status == AgentStatus.NORMAL

    @pytest.mark.asyncio
    async def test_status_warning_medium_confidence(self) -> None:
        """Test WARNING status with medium confidence."""
        analyst = LLMSignalAnalyst(params={"min_confidence": 0.7})
        response = '{"action": "HOLD", "confidence": 0.55, "reasoning": "Uncertain"}'

        with patch.object(
            analyst, "_call_llm_with_retry", new_callable=AsyncMock
        ) as mock_call:
            mock_call.return_value = response

            await analyst.generate_signal({})

            assert analyst.status == AgentStatus.WARNING

    @pytest.mark.asyncio
    async def test_status_warning_on_error(self) -> None:
        """Test WARNING status on error."""
        analyst = LLMSignalAnalyst(params={})

        with patch.object(
            analyst, "_call_llm_with_retry", new_callable=AsyncMock
        ) as mock_call:
            mock_call.side_effect = LLMAnalystError("Error")

            await analyst.generate_signal({})

            assert analyst.status == AgentStatus.WARNING


class TestLLMSignalAnalystRetryLogic:
    """Tests for retry logic."""

    @pytest.mark.asyncio
    async def test_retry_on_failure(self) -> None:
        """Test that LLM calls are retried on failure."""
        analyst = LLMSignalAnalyst(params={"max_retries": 3, "timeout": 1})

        with patch.object(analyst, "_invoke_llm", new_callable=AsyncMock) as mock_invoke:
            # First two calls fail, third succeeds
            mock_invoke.side_effect = [
                Exception("API Error"),
                Exception("Timeout"),
                '{"action": "BUY", "confidence": 0.8, "reasoning": "OK"}',
            ]

            result = await analyst._call_llm_with_retry("test prompt")

            assert mock_invoke.call_count == 3
            assert "BUY" in result

    @pytest.mark.asyncio
    async def test_all_retries_fail(self) -> None:
        """Test error when all retries fail."""
        analyst = LLMSignalAnalyst(params={"max_retries": 2, "timeout": 1})

        with patch.object(analyst, "_invoke_llm", new_callable=AsyncMock) as mock_invoke:
            mock_invoke.side_effect = Exception("Persistent Error")

            with pytest.raises(LLMAnalystError) as exc_info:
                await analyst._call_llm_with_retry("test prompt")

            assert "2 attempts" in str(exc_info.value)


class TestLLMSignalAnalystLLMInitialization:
    """Tests for LLM client initialization."""

    def test_llm_lazy_initialization(self) -> None:
        """Test that LLM is lazily initialized."""
        analyst = LLMSignalAnalyst(params={})

        assert analyst._llm is None

    def test_llm_property_creates_client(self) -> None:
        """Test that accessing llm property creates client."""
        analyst = LLMSignalAnalyst(params={"model": "claude-sonnet-4-20250514"})

        with patch("src.agents.analyst.ChatAnthropic") as mock_chat:
            mock_instance = MagicMock()
            mock_chat.return_value = mock_instance

            llm = analyst.llm

            mock_chat.assert_called_once_with(
                model="claude-sonnet-4-20250514",
                timeout=30,
                max_retries=3,
            )
            assert llm == mock_instance
