"""LLM Signal Analyst agent for trading signal generation."""

import asyncio
from enum import Enum
from typing import Any

import structlog
from anthropic import APIStatusError, RateLimitError
from langchain_anthropic import ChatAnthropic
from pydantic import BaseModel, Field

from src.agents.base import AgentDecision, AgentStatus, BaseAgent
from src.agents.retry_utils import llm_retry_decorator
from src.core.exceptions import TradingError

log = structlog.get_logger()


class SignalAction(str, Enum):
    """Trading signal actions."""

    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class LLMSignalResponse(BaseModel):
    """Structured response from LLM signal analysis."""

    action: SignalAction = Field(..., description="Trading action: BUY, SELL, or HOLD")
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Confidence in the signal (0.0-1.0)"
    )
    reasoning: str = Field(..., description="Explanation for the trading decision")


class LLMAnalystError(TradingError):
    """Error during LLM signal analysis."""

    code = "LLM_ANALYST_ERROR"


class LLMSignalAnalyst(BaseAgent):
    """LLM-based signal analyst for generating trading signals.

    Uses Claude to analyze market data and generate trading signals
    with confidence scores and reasoning.
    """

    name = "analyst"

    def _configure(self, params: dict[str, Any]) -> None:
        """Configure the LLM analyst with parameters.

        Args:
            params: Configuration parameters including:
                - model: Claude model to use (default: claude-sonnet-4-20250514)
                - min_confidence: Minimum confidence to act (default: 0.7)
                - lookback: Days of historical data to consider (default: 14)
                - timeout: API timeout in seconds (default: 30)
                - max_retries: Max retry attempts (default: 3)
        """
        self.model = params.get("model", "claude-sonnet-4-20250514")
        self.min_confidence = params.get("min_confidence", 0.7)
        self.lookback = params.get("lookback", 14)
        self.timeout = params.get("timeout", 30)
        self.max_retries = params.get("max_retries", 3)

        # Initialize LLM - will be None if no API key is set (for testing)
        self._llm: ChatAnthropic | None = None

        log.debug(
            "llm_analyst_configured",
            model=self.model,
            min_confidence=self.min_confidence,
            lookback=self.lookback,
            timeout=self.timeout,
        )

    @property
    def llm(self) -> ChatAnthropic:
        """Lazy initialization of LLM client."""
        if self._llm is None:
            self._llm = ChatAnthropic(
                model=self.model,
                timeout=self.timeout,
                max_retries=self.max_retries,
            )
        return self._llm

    async def execute(self, context: dict[str, Any]) -> AgentDecision:
        """Execute signal analysis.

        Alias for generate_signal() to satisfy BaseAgent interface.

        Args:
            context: Execution context with market data.

        Returns:
            AgentDecision with trading signal.
        """
        return await self.generate_signal(context)

    async def generate_signal(self, context: dict[str, Any]) -> AgentDecision:
        """Analyze market data and generate trading signal.

        Args:
            context: Execution context containing:
                - market_data: Dict with price/volume information
                - indicators: Technical indicators (RSI, MA, etc.)
                - crash_detector_status: Status from CrashDetector
                - historical_performance: Past trading results

        Returns:
            AgentDecision with action (BUY/SELL/HOLD), confidence, and reasoning.
        """
        try:
            # Build the analysis prompt
            prompt = self._build_prompt(context)

            # Call LLM with retry logic
            response = await self._call_llm_with_retry(prompt)

            # Parse and validate response
            signal = self._parse_response(response)

            # Update agent status based on confidence
            self._update_status(signal)

            log.info(
                "signal_generated",
                agent_name=self.name,
                action=signal.action.value,
                confidence=signal.confidence,
                min_confidence=self.min_confidence,
            )

            return AgentDecision(
                agent_name=self.name,
                decision_type="signal",
                data={
                    "action": signal.action.value,
                    "confidence": signal.confidence,
                    "reasoning": signal.reasoning,
                    "meets_threshold": signal.confidence >= self.min_confidence,
                    "min_confidence": self.min_confidence,
                },
                confidence=signal.confidence,
            )

        except LLMAnalystError as e:
            log.error(
                "signal_generation_failed",
                agent_name=self.name,
                error=str(e),
                error_type=type(e).__name__,
            )
            self.status = AgentStatus.WARNING

            # Fallback after all retries: HOLD signal with warning
            return AgentDecision(
                agent_name=self.name,
                decision_type="warning",
                data={
                    "action": SignalAction.HOLD.value,
                    "confidence": 0.0,
                    "reasoning": f"LLM API failed after {self.max_retries} retries. Defaulting to HOLD for safety.",
                    "error": str(e),
                    "fallback": True,
                },
                confidence=0.0,
            )
        except Exception as e:
            log.error(
                "signal_generation_failed_unexpected",
                agent_name=self.name,
                error=str(e),
                error_type=type(e).__name__,
            )
            self.status = AgentStatus.WARNING

            return AgentDecision(
                agent_name=self.name,
                decision_type="warning",
                data={
                    "action": SignalAction.HOLD.value,
                    "confidence": 0.0,
                    "reasoning": f"Unexpected error during signal generation: {e!s}",
                    "error": str(e),
                },
                confidence=0.0,
            )

    def _build_prompt(self, context: dict[str, Any]) -> str:
        """Build the analysis prompt from context.

        Args:
            context: Execution context with market data.

        Returns:
            Formatted prompt string.
        """
        market_data = context.get("market_data", {})
        indicators = context.get("indicators", {})
        crash_status = context.get("crash_detector_status", "unknown")
        historical = context.get("historical_performance", {})

        prompt = f"""Analyze the following market data and provide a trading signal.

## Current Market Data
Symbol: {market_data.get("symbol", "Unknown")}
Current Price: {market_data.get("current_price", "N/A")}
24h Change: {market_data.get("price_change_24h", "N/A")}%
Volume: {market_data.get("volume", "N/A")}

## Technical Indicators
RSI: {indicators.get("rsi", "N/A")}
Moving Average (20): {indicators.get("ma_20", "N/A")}
Moving Average (50): {indicators.get("ma_50", "N/A")}
MACD: {indicators.get("macd", "N/A")}

## Risk Assessment
Crash Detector Status: {crash_status}

## Historical Performance
Win Rate: {historical.get("win_rate", "N/A")}%
Recent Trades: {historical.get("recent_trades", "N/A")}

Based on this analysis, provide your trading recommendation.
You must respond with a valid JSON object containing exactly these fields:
- action: One of "BUY", "SELL", or "HOLD"
- confidence: A number between 0.0 and 1.0
- reasoning: A brief explanation for your decision

Respond ONLY with the JSON object, no additional text."""

        return prompt

    async def _call_llm_with_retry(self, prompt: str) -> str:
        """Call LLM with retry logic using tenacity.

        Args:
            prompt: The prompt to send to the LLM.

        Returns:
            LLM response text.

        Raises:
            LLMAnalystError: If all retries fail.
        """
        try:
            return await self._invoke_llm(prompt)
        except (RateLimitError, APIStatusError, TimeoutError) as e:
            # After all retries exhausted, return fallback
            log.error(
                "llm_call_failed_all_retries",
                agent_name=self.name,
                error=str(e),
                error_type=type(e).__name__,
            )
            raise LLMAnalystError(
                f"LLM call failed after {self.max_retries} attempts: {e!s}",
                details={"error_type": type(e).__name__},
            ) from e

    @llm_retry_decorator()
    async def _invoke_llm(self, prompt: str) -> str:
        """Invoke the LLM asynchronously with retry logic.

        This method is decorated with @llm_retry_decorator which provides:
        - 3 retry attempts
        - Exponential backoff: 2s, 4s, 8s
        - Retry on: RateLimitError (429), APIStatusError (5xx), TimeoutError
        - Automatic logging of retry attempts

        Args:
            prompt: The prompt to send.

        Returns:
            LLM response text.

        Raises:
            RateLimitError: If rate limit exceeded after all retries.
            APIStatusError: If server error persists after all retries.
            TimeoutError: If timeout occurs on all retry attempts.
        """
        response = await asyncio.wait_for(
            self.llm.ainvoke(prompt),
            timeout=self.timeout,
        )
        return str(response.content)

    def _parse_response(self, response: str) -> LLMSignalResponse:
        """Parse LLM response into structured signal.

        Args:
            response: Raw LLM response text.

        Returns:
            Parsed LLMSignalResponse.

        Raises:
            LLMAnalystError: If parsing fails.
        """
        import json

        try:
            # Try to extract JSON from response
            response = response.strip()

            # Handle markdown code blocks
            if response.startswith("```"):
                lines = response.split("\n")
                json_lines = []
                in_json = False
                for line in lines:
                    if line.startswith("```") and not in_json:
                        in_json = True
                        continue
                    elif line.startswith("```") and in_json:
                        break
                    elif in_json:
                        json_lines.append(line)
                response = "\n".join(json_lines)

            data = json.loads(response)
            return LLMSignalResponse(**data)

        except (json.JSONDecodeError, ValueError) as e:
            raise LLMAnalystError(
                "Failed to parse LLM response",
                details={"response": response[:200], "error": str(e)},
            ) from e

    def _update_status(self, signal: LLMSignalResponse) -> None:
        """Update agent status based on signal.

        Args:
            signal: The parsed signal response.
        """
        if signal.confidence >= self.min_confidence:
            self.status = AgentStatus.NORMAL
        elif signal.confidence >= 0.5:
            self.status = AgentStatus.WARNING
        else:
            self.status = AgentStatus.WARNING
