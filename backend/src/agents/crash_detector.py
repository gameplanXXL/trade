"""CrashDetector agent for market crash detection."""

from typing import Any

import structlog

from src.agents.base import AgentDecision, AgentStatus, BaseAgent

log = structlog.get_logger()


class CrashDetector(BaseAgent):
    """Agent that detects potential market crash conditions.

    Analyzes market data to determine if crash conditions are present
    based on configurable indicators and thresholds.
    """

    name = "crash_detector"

    def _configure(self, params: dict[str, Any]) -> None:
        """Configure the crash detector with parameters.

        Args:
            params: Configuration parameters including:
                - threshold: Crash probability threshold (0.0-1.0, default 0.9)
                - window_days: Analysis window in days (default 30)
                - indicators: List of indicators to check (default ["volatility", "rsi"])
        """
        self.threshold = params.get("threshold", 0.9)
        self.window_days = params.get("window_days", 30)
        self.indicators = params.get("indicators", ["volatility", "rsi"])

        log.debug(
            "crash_detector_configured",
            threshold=self.threshold,
            window_days=self.window_days,
            indicators=self.indicators,
        )

    async def execute(self, context: dict[str, Any]) -> AgentDecision:
        """Execute crash detection analysis.

        Alias for check() to satisfy BaseAgent interface.

        Args:
            context: Execution context with market data.

        Returns:
            AgentDecision with crash analysis results.
        """
        return await self.check(context)

    async def check(self, context: dict[str, Any]) -> AgentDecision:
        """Check market data for crash indicators.

        Analyzes the provided market data and sets agent status
        based on the crash probability.

        Args:
            context: Execution context containing:
                - market_data: Dict with price/volume information
                - volatility: Current market volatility (optional)
                - rsi: RSI indicator value (optional)

        Returns:
            AgentDecision with crash analysis including:
                - crash_probability: Calculated crash probability (0.0-1.0)
                - triggered_indicators: List of indicators that triggered
                - status: Current agent status
        """
        market_data = context.get("market_data", {})

        # Calculate crash probability based on indicators
        crash_probability, triggered_indicators = self._analyze_indicators(
            context, market_data
        )

        # Update agent status based on probability
        self._update_status(crash_probability)

        log.info(
            "crash_detection_complete",
            agent_name=self.name,
            crash_probability=crash_probability,
            triggered_indicators=triggered_indicators,
            status=self.status.value,
        )

        return AgentDecision(
            agent_name=self.name,
            decision_type="signal" if self.status == AgentStatus.CRASH else "warning"
            if self.status == AgentStatus.WARNING else "signal",
            data={
                "crash_probability": crash_probability,
                "triggered_indicators": triggered_indicators,
                "status": self.status.value,
                "threshold": self.threshold,
                "window_days": self.window_days,
            },
            confidence=(
                1.0 - crash_probability
                if self.status == AgentStatus.NORMAL
                else crash_probability
            ),
        )

    def _analyze_indicators(
        self, context: dict[str, Any], market_data: dict[str, Any]
    ) -> tuple[float, list[str]]:
        """Analyze configured indicators for crash signals.

        Args:
            context: Full execution context.
            market_data: Market data from context.

        Returns:
            Tuple of (crash_probability, triggered_indicators).
        """
        triggered = []
        probabilities = []

        for indicator in self.indicators:
            if indicator == "volatility":
                prob = self._check_volatility(context, market_data)
                if prob > 0.5:
                    triggered.append("volatility")
                probabilities.append(prob)

            elif indicator == "rsi":
                prob = self._check_rsi(context, market_data)
                if prob > 0.5:
                    triggered.append("rsi")
                probabilities.append(prob)

        # Calculate overall probability (average of all indicators)
        if probabilities:
            crash_probability = sum(probabilities) / len(probabilities)
        else:
            crash_probability = 0.0

        return crash_probability, triggered

    def _check_volatility(
        self, context: dict[str, Any], market_data: dict[str, Any]
    ) -> float:
        """Check volatility indicator.

        MVP implementation: Uses provided volatility value or calculates
        a simple measure from market data.

        Args:
            context: Full execution context.
            market_data: Market data from context.

        Returns:
            Probability based on volatility (0.0-1.0).
        """
        # Use provided volatility if available
        if "volatility" in context:
            volatility = context["volatility"]
            # Normalize: assume high volatility > 0.5 indicates potential crash
            return min(1.0, volatility * 2)

        # Fallback: check for price change in market data
        if "price_change_pct" in market_data:
            change = abs(market_data["price_change_pct"])
            # Large price drops indicate crash potential
            return min(1.0, change / 10.0)  # 10% change = 1.0 probability

        return 0.0

    def _check_rsi(
        self, context: dict[str, Any], market_data: dict[str, Any]
    ) -> float:
        """Check RSI indicator.

        MVP implementation: Uses provided RSI value.
        RSI < 30 indicates oversold (potential crash).

        Args:
            context: Full execution context.
            market_data: Market data from context.

        Returns:
            Probability based on RSI (0.0-1.0).
        """
        if "rsi" in context:
            rsi = context["rsi"]
            # RSI < 30 is oversold, map to crash probability
            if rsi < 30:
                return (30 - rsi) / 30  # 0 RSI = 1.0 probability
            elif rsi > 70:
                # Overbought can also indicate instability
                return (rsi - 70) / 30 * 0.5  # Lower weight for overbought
        return 0.0

    def _update_status(self, crash_probability: float) -> None:
        """Update agent status based on crash probability.

        Status mapping:
        - probability > threshold: CRASH
        - probability > 0.7: WARNING
        - otherwise: NORMAL

        Args:
            crash_probability: Calculated crash probability (0.0-1.0).
        """
        if crash_probability >= self.threshold:
            self.status = AgentStatus.CRASH
        elif crash_probability >= 0.7:
            self.status = AgentStatus.WARNING
        else:
            self.status = AgentStatus.NORMAL
