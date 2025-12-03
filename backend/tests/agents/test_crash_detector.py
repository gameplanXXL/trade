"""Tests for CrashDetector agent."""

import pytest

from src.agents.base import AgentDecision, AgentStatus
from src.agents.crash_detector import CrashDetector


class TestCrashDetectorConfiguration:
    """Tests for CrashDetector configuration."""

    def test_default_configuration(self) -> None:
        """Test default configuration values."""
        detector = CrashDetector(params={})

        assert detector.threshold == 0.9
        assert detector.window_days == 30
        assert detector.indicators == ["volatility", "rsi"]

    def test_custom_configuration(self) -> None:
        """Test custom configuration values."""
        detector = CrashDetector(
            params={
                "threshold": 0.8,
                "window_days": 14,
                "indicators": ["volatility"],
            }
        )

        assert detector.threshold == 0.8
        assert detector.window_days == 14
        assert detector.indicators == ["volatility"]

    def test_agent_name(self) -> None:
        """Test that agent name is set correctly."""
        detector = CrashDetector(params={})
        assert detector.name == "crash_detector"

    def test_initial_status(self) -> None:
        """Test that agent starts with NORMAL status."""
        detector = CrashDetector(params={})
        assert detector.status == AgentStatus.NORMAL


class TestCrashDetectorCheck:
    """Tests for CrashDetector.check method."""

    @pytest.fixture
    def detector(self) -> CrashDetector:
        """Create a CrashDetector with default config."""
        return CrashDetector(params={"threshold": 0.9})

    @pytest.mark.asyncio
    async def test_check_returns_agent_decision(
        self, detector: CrashDetector
    ) -> None:
        """Test that check returns an AgentDecision."""
        context = {"market_data": {}}
        result = await detector.check(context)

        assert isinstance(result, AgentDecision)
        assert result.agent_name == "crash_detector"

    @pytest.mark.asyncio
    async def test_check_includes_crash_probability(
        self, detector: CrashDetector
    ) -> None:
        """Test that decision includes crash_probability."""
        context = {"market_data": {}}
        result = await detector.check(context)

        assert "crash_probability" in result.data
        assert 0.0 <= result.data["crash_probability"] <= 1.0

    @pytest.mark.asyncio
    async def test_check_includes_triggered_indicators(
        self, detector: CrashDetector
    ) -> None:
        """Test that decision includes triggered_indicators."""
        context = {"market_data": {}}
        result = await detector.check(context)

        assert "triggered_indicators" in result.data
        assert isinstance(result.data["triggered_indicators"], list)

    @pytest.mark.asyncio
    async def test_check_includes_status(
        self, detector: CrashDetector
    ) -> None:
        """Test that decision includes status."""
        context = {"market_data": {}}
        result = await detector.check(context)

        assert "status" in result.data
        assert result.data["status"] in ["normal", "warning", "crash"]

    @pytest.mark.asyncio
    async def test_execute_calls_check(
        self, detector: CrashDetector
    ) -> None:
        """Test that execute() is an alias for check()."""
        context = {"market_data": {}}
        result = await detector.execute(context)

        assert isinstance(result, AgentDecision)
        assert result.agent_name == "crash_detector"


class TestCrashDetectorStatusMapping:
    """Tests for crash probability to status mapping."""

    @pytest.fixture
    def detector(self) -> CrashDetector:
        """Create a CrashDetector with threshold 0.9."""
        return CrashDetector(params={"threshold": 0.9})

    @pytest.mark.asyncio
    async def test_normal_status_low_probability(
        self, detector: CrashDetector
    ) -> None:
        """Test NORMAL status with low crash probability."""
        # Volatility 0.2 = probability 0.4, RSI not provided = 0
        # Average = 0.2
        context = {"volatility": 0.2, "market_data": {}}
        await detector.check(context)

        assert detector.status == AgentStatus.NORMAL

    @pytest.mark.asyncio
    async def test_warning_status_medium_probability(
        self, detector: CrashDetector
    ) -> None:
        """Test WARNING status with 0.5 <= probability < threshold.

        Per Story 003-03 AC:
        - NORMAL: crash_probability < 0.5
        - WARNING: 0.5 <= crash_probability < threshold (0.9)
        - CRASH: crash_probability >= threshold
        """
        # Need probability >= 0.5 and < 0.9
        # Volatility 0.3 = probability 0.6, RSI 50 = probability 0
        # Average = 0.3 which is < 0.5, not enough
        # Use volatility 0.35 -> 0.7, rsi 50 -> 0
        # Average = 0.35 -> too low
        # Use only volatility indicator for clearer control
        detector_single = CrashDetector(params={"threshold": 0.9, "indicators": ["volatility"]})
        context = {"volatility": 0.35, "market_data": {}}  # 0.35 * 2 = 0.7
        await detector_single.check(context)

        # probability = 0.7, which is >= 0.5 and < 0.9
        assert detector_single.status == AgentStatus.WARNING

    @pytest.mark.asyncio
    async def test_crash_status_high_probability(
        self, detector: CrashDetector
    ) -> None:
        """Test CRASH status with probability >= threshold."""
        # High volatility and extreme RSI
        context = {"volatility": 0.6, "rsi": 5, "market_data": {}}
        await detector.check(context)

        # volatility 0.6 * 2 = 1.0 (capped), rsi 5 -> (30-5)/30 = 0.83
        # average = (1.0 + 0.83) / 2 = 0.915 >= 0.9
        assert detector.status == AgentStatus.CRASH

    @pytest.mark.asyncio
    async def test_status_updated_on_each_check(
        self, detector: CrashDetector
    ) -> None:
        """Test that status is updated on each check."""
        # Start with high risk
        context_crash = {"volatility": 0.6, "rsi": 5, "market_data": {}}
        await detector.check(context_crash)
        assert detector.status == AgentStatus.CRASH

        # Then check with low risk
        context_normal = {"volatility": 0.1, "rsi": 50, "market_data": {}}
        await detector.check(context_normal)
        assert detector.status == AgentStatus.NORMAL


class TestCrashDetectorStatusThresholds:
    """Tests for Story 003-03 status threshold requirements."""

    @pytest.mark.asyncio
    async def test_normal_below_0_5(self) -> None:
        """Test NORMAL status when probability < 0.5."""
        detector = CrashDetector(params={"threshold": 0.9, "indicators": ["volatility"]})
        # volatility 0.2 * 2 = 0.4 < 0.5
        context = {"volatility": 0.2, "market_data": {}}
        await detector.check(context)
        assert detector.status == AgentStatus.NORMAL

    @pytest.mark.asyncio
    async def test_warning_at_exactly_0_5(self) -> None:
        """Test WARNING status when probability == 0.5."""
        detector = CrashDetector(params={"threshold": 0.9, "indicators": ["volatility"]})
        # volatility 0.25 * 2 = 0.5
        context = {"volatility": 0.25, "market_data": {}}
        await detector.check(context)
        assert detector.status == AgentStatus.WARNING

    @pytest.mark.asyncio
    async def test_warning_between_0_5_and_threshold(self) -> None:
        """Test WARNING status when 0.5 <= probability < threshold."""
        detector = CrashDetector(params={"threshold": 0.9, "indicators": ["volatility"]})
        # volatility 0.4 * 2 = 0.8 (>= 0.5, < 0.9)
        context = {"volatility": 0.4, "market_data": {}}
        await detector.check(context)
        assert detector.status == AgentStatus.WARNING

    @pytest.mark.asyncio
    async def test_crash_at_threshold(self) -> None:
        """Test CRASH status when probability == threshold."""
        detector = CrashDetector(params={"threshold": 0.9, "indicators": ["volatility"]})
        # volatility 0.45 * 2 = 0.9 == threshold
        context = {"volatility": 0.45, "market_data": {}}
        await detector.check(context)
        assert detector.status == AgentStatus.CRASH

    @pytest.mark.asyncio
    async def test_crash_above_threshold(self) -> None:
        """Test CRASH status when probability > threshold."""
        detector = CrashDetector(params={"threshold": 0.9, "indicators": ["volatility"]})
        # volatility 0.5 * 2 = 1.0 > 0.9
        context = {"volatility": 0.5, "market_data": {}}
        await detector.check(context)
        assert detector.status == AgentStatus.CRASH

    @pytest.mark.asyncio
    async def test_custom_threshold(self) -> None:
        """Test that custom threshold is respected."""
        detector = CrashDetector(params={"threshold": 0.7, "indicators": ["volatility"]})
        # volatility 0.35 * 2 = 0.7 == threshold
        context = {"volatility": 0.35, "market_data": {}}
        await detector.check(context)
        assert detector.status == AgentStatus.CRASH


class TestCrashDetectorIndicators:
    """Tests for individual indicator analysis."""

    @pytest.mark.asyncio
    async def test_volatility_indicator(self) -> None:
        """Test volatility indicator calculation."""
        detector = CrashDetector(params={"indicators": ["volatility"]})
        context = {"volatility": 0.5, "market_data": {}}

        result = await detector.check(context)

        assert result.data["crash_probability"] == 1.0  # 0.5 * 2 = 1.0

    @pytest.mark.asyncio
    async def test_volatility_from_price_change(self) -> None:
        """Test volatility fallback to price_change_pct."""
        detector = CrashDetector(params={"indicators": ["volatility"]})
        context = {"market_data": {"price_change_pct": 5.0}}

        result = await detector.check(context)

        assert result.data["crash_probability"] == 0.5  # 5% / 10 = 0.5

    @pytest.mark.asyncio
    async def test_rsi_oversold(self) -> None:
        """Test RSI indicator with oversold condition."""
        detector = CrashDetector(params={"indicators": ["rsi"]})
        context = {"rsi": 10, "market_data": {}}

        result = await detector.check(context)

        # (30 - 10) / 30 = 0.67
        expected_prob = (30 - 10) / 30
        assert abs(result.data["crash_probability"] - expected_prob) < 0.01
        assert "rsi" in result.data["triggered_indicators"]

    @pytest.mark.asyncio
    async def test_rsi_normal(self) -> None:
        """Test RSI indicator with normal range."""
        detector = CrashDetector(params={"indicators": ["rsi"]})
        context = {"rsi": 50, "market_data": {}}

        result = await detector.check(context)

        assert result.data["crash_probability"] == 0.0
        assert "rsi" not in result.data["triggered_indicators"]

    @pytest.mark.asyncio
    async def test_rsi_overbought(self) -> None:
        """Test RSI indicator with overbought condition."""
        detector = CrashDetector(params={"indicators": ["rsi"]})
        context = {"rsi": 80, "market_data": {}}

        result = await detector.check(context)

        # (80 - 70) / 30 * 0.5 = 0.167
        assert 0.1 <= result.data["crash_probability"] <= 0.2

    @pytest.mark.asyncio
    async def test_multiple_indicators_averaged(self) -> None:
        """Test that multiple indicators are averaged."""
        detector = CrashDetector(params={"indicators": ["volatility", "rsi"]})
        context = {"volatility": 0.5, "rsi": 15, "market_data": {}}

        result = await detector.check(context)

        # volatility: 0.5 * 2 = 1.0
        # rsi: (30 - 15) / 30 = 0.5
        # average: (1.0 + 0.5) / 2 = 0.75
        assert result.data["crash_probability"] == 0.75

    @pytest.mark.asyncio
    async def test_empty_indicators(self) -> None:
        """Test with no indicators configured."""
        detector = CrashDetector(params={"indicators": []})
        context = {"volatility": 0.9, "rsi": 5, "market_data": {}}

        result = await detector.check(context)

        assert result.data["crash_probability"] == 0.0
        assert result.data["triggered_indicators"] == []


class TestCrashDetectorDecisionType:
    """Tests for decision type based on status."""

    @pytest.mark.asyncio
    async def test_decision_type_normal(self) -> None:
        """Test decision type for NORMAL status."""
        detector = CrashDetector(params={"indicators": ["volatility"]})
        context = {"volatility": 0.1, "market_data": {}}

        result = await detector.check(context)

        assert result.decision_type == "signal"
        assert detector.status == AgentStatus.NORMAL

    @pytest.mark.asyncio
    async def test_decision_type_warning(self) -> None:
        """Test decision type for WARNING status.

        Per Story 003-03: WARNING when 0.5 <= probability < threshold.
        """
        detector = CrashDetector(params={"threshold": 0.9, "indicators": ["volatility"]})
        context = {"volatility": 0.35, "market_data": {}}  # 0.35 * 2 = 0.7 >= 0.5, < 0.9

        result = await detector.check(context)

        assert result.decision_type == "warning"
        assert detector.status == AgentStatus.WARNING

    @pytest.mark.asyncio
    async def test_decision_type_crash(self) -> None:
        """Test decision type for CRASH status."""
        detector = CrashDetector(params={"threshold": 0.9, "indicators": ["volatility"]})
        context = {"volatility": 0.5, "market_data": {}}  # 0.5 * 2 = 1.0 >= 0.9

        result = await detector.check(context)

        assert result.decision_type == "signal"
        assert detector.status == AgentStatus.CRASH


class TestCrashDetectorConfidence:
    """Tests for confidence calculation."""

    @pytest.mark.asyncio
    async def test_confidence_normal_status(self) -> None:
        """Test confidence for NORMAL status."""
        detector = CrashDetector(params={"indicators": ["volatility"]})
        context = {"volatility": 0.1, "market_data": {}}

        result = await detector.check(context)

        # confidence = 1.0 - probability for NORMAL
        # probability = 0.1 * 2 = 0.2
        # confidence = 1.0 - 0.2 = 0.8
        assert result.confidence == 0.8

    @pytest.mark.asyncio
    async def test_confidence_crash_status(self) -> None:
        """Test confidence for CRASH status."""
        detector = CrashDetector(params={"threshold": 0.9, "indicators": ["volatility"]})
        context = {"volatility": 0.5, "market_data": {}}

        result = await detector.check(context)

        # confidence = probability for non-NORMAL
        assert result.confidence == 1.0  # probability capped at 1.0
