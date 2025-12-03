"""Tests for base agent classes."""

from datetime import UTC, datetime
from typing import Any

import pytest

from src.agents.base import AgentDecision, AgentStatus, BaseAgent


class ConcreteTestAgent(BaseAgent):
    """Concrete implementation of BaseAgent for testing."""

    name = "test_agent"

    def _configure(self, params: dict[str, Any]) -> None:
        """Configure the test agent."""
        self.threshold = params.get("threshold", 0.5)

    async def execute(self, context: dict[str, Any]) -> AgentDecision:
        """Execute test agent logic."""
        return AgentDecision(
            agent_name=self.name,
            decision_type="signal",
            data={"result": "test_result"},
            confidence=self.threshold,
        )


class TestAgentStatus:
    """Tests for AgentStatus enum."""

    def test_status_values(self) -> None:
        """Test that all expected status values exist."""
        assert AgentStatus.NORMAL == "normal"
        assert AgentStatus.WARNING == "warning"
        assert AgentStatus.CRASH == "crash"

    def test_status_is_string_enum(self) -> None:
        """Test that AgentStatus is a string enum."""
        assert isinstance(AgentStatus.NORMAL, str)
        assert AgentStatus.NORMAL.value == "normal"


class TestAgentDecision:
    """Tests for AgentDecision model."""

    def test_valid_decision(self) -> None:
        """Test creating a valid agent decision."""
        decision = AgentDecision(
            agent_name="test_agent",
            decision_type="signal",
            data={"action": "buy", "symbol": "EURUSD"},
            confidence=0.85,
        )

        assert decision.agent_name == "test_agent"
        assert decision.decision_type == "signal"
        assert decision.data == {"action": "buy", "symbol": "EURUSD"}
        assert decision.confidence == 0.85
        assert isinstance(decision.timestamp, datetime)

    def test_decision_default_timestamp(self) -> None:
        """Test that timestamp defaults to current time."""
        before = datetime.now(UTC)
        decision = AgentDecision(
            agent_name="test_agent",
            decision_type="warning",
        )
        after = datetime.now(UTC)

        assert before <= decision.timestamp <= after

    def test_decision_default_data(self) -> None:
        """Test that data defaults to empty dict."""
        decision = AgentDecision(
            agent_name="test_agent",
            decision_type="action",
        )
        assert decision.data == {}

    def test_decision_default_confidence(self) -> None:
        """Test that confidence defaults to None."""
        decision = AgentDecision(
            agent_name="test_agent",
            decision_type="signal",
        )
        assert decision.confidence is None

    def test_decision_confidence_bounds(self) -> None:
        """Test that confidence must be between 0 and 1."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            AgentDecision(
                agent_name="test_agent",
                decision_type="signal",
                confidence=-0.1,
            )

        with pytest.raises(ValidationError):
            AgentDecision(
                agent_name="test_agent",
                decision_type="signal",
                confidence=1.1,
            )

    def test_decision_types(self) -> None:
        """Test different decision types are accepted."""
        for decision_type in ["signal", "warning", "rejection", "action"]:
            decision = AgentDecision(
                agent_name="test_agent",
                decision_type=decision_type,
            )
            assert decision.decision_type == decision_type


class TestBaseAgent:
    """Tests for BaseAgent abstract class."""

    @pytest.fixture
    def agent(self) -> ConcreteTestAgent:
        """Create a test agent instance."""
        return ConcreteTestAgent(params={"threshold": 0.75})

    def test_agent_initialization(self, agent: ConcreteTestAgent) -> None:
        """Test agent initializes correctly."""
        assert agent.name == "test_agent"
        assert agent.status == AgentStatus.NORMAL
        assert agent.params == {"threshold": 0.75}
        assert agent.threshold == 0.75

    def test_agent_default_status(self) -> None:
        """Test agent starts with NORMAL status."""
        agent = ConcreteTestAgent(params={})
        assert agent.status == AgentStatus.NORMAL

    def test_agent_status_change(self, agent: ConcreteTestAgent) -> None:
        """Test that status changes are tracked."""
        assert agent.status == AgentStatus.NORMAL

        agent.status = AgentStatus.WARNING
        assert agent.status == AgentStatus.WARNING

        agent.status = AgentStatus.CRASH
        assert agent.status == AgentStatus.CRASH

    def test_agent_to_dict(self, agent: ConcreteTestAgent) -> None:
        """Test agent serialization to dict."""
        result = agent.to_dict()

        assert result["name"] == "test_agent"
        assert result["status"] == "normal"
        assert result["params"] == {"threshold": 0.75}

    def test_agent_to_dict_with_changed_status(
        self, agent: ConcreteTestAgent
    ) -> None:
        """Test that to_dict reflects current status."""
        agent.status = AgentStatus.CRASH
        result = agent.to_dict()

        assert result["status"] == "crash"

    @pytest.mark.asyncio
    async def test_agent_execute(self, agent: ConcreteTestAgent) -> None:
        """Test agent execute method."""
        context = {"market_data": {"symbol": "EURUSD"}}
        decision = await agent.execute(context)

        assert isinstance(decision, AgentDecision)
        assert decision.agent_name == "test_agent"
        assert decision.decision_type == "signal"
        assert decision.data == {"result": "test_result"}
        assert decision.confidence == 0.75

    def test_agent_configure_called(self) -> None:
        """Test that _configure is called during initialization."""
        agent = ConcreteTestAgent(params={"threshold": 0.9})
        assert agent.threshold == 0.9

    def test_agent_with_empty_params(self) -> None:
        """Test agent handles empty params."""
        agent = ConcreteTestAgent(params={})
        assert agent.threshold == 0.5  # default value


class TestBaseAgentAbstract:
    """Tests to verify BaseAgent is properly abstract."""

    def test_cannot_instantiate_base_agent(self) -> None:
        """Test that BaseAgent cannot be instantiated directly."""
        with pytest.raises(TypeError) as exc_info:
            BaseAgent(params={})  # type: ignore[abstract]

        assert "abstract" in str(exc_info.value).lower()

    def test_must_implement_configure(self) -> None:
        """Test that _configure must be implemented."""

        class IncompleteAgent(BaseAgent):
            name = "incomplete"

            async def execute(self, context: dict[str, Any]) -> AgentDecision:
                return AgentDecision(
                    agent_name=self.name, decision_type="signal"
                )

        with pytest.raises(TypeError):
            IncompleteAgent(params={})  # type: ignore[abstract]

    def test_must_implement_execute(self) -> None:
        """Test that execute must be implemented."""

        class IncompleteAgent(BaseAgent):
            name = "incomplete"

            def _configure(self, params: dict[str, Any]) -> None:
                pass

        with pytest.raises(TypeError):
            IncompleteAgent(params={})  # type: ignore[abstract]
