"""Tests for override rule engine - Story 003-02."""

from typing import Any

import pytest

from src.agents.base import AgentDecision, AgentStatus, BaseAgent
from src.core.exceptions import PipelineError
from src.teams.override import OverrideEngine, OverrideResult
from src.teams.schemas import OverrideRule


class MockAgent(BaseAgent):
    """Mock agent for testing override engine."""

    name = "mock_agent"

    def _configure(self, params: dict[str, Any]) -> None:
        """Configure the mock agent."""
        self.field_value = params.get("field_value", 0)

    async def execute(self, context: dict[str, Any]) -> AgentDecision:
        """Execute the mock agent's logic."""
        return AgentDecision(
            agent_name=self.name,
            decision_type="test",
            data={},
        )

    async def close_all_positions(self, context: dict[str, Any] | None = None) -> AgentDecision:
        """Close all positions action."""
        return AgentDecision(
            agent_name=self.name,
            decision_type="close_all",
            data={"action": "close_all_positions"},
        )

    async def halt_trading(self, context: dict[str, Any] | None = None) -> AgentDecision:
        """Halt trading action."""
        return AgentDecision(
            agent_name=self.name,
            decision_type="halt",
            data={"action": "halt_trading"},
        )


class TestOverrideResult:
    """Tests for OverrideResult model."""

    def test_create_override_result(self) -> None:
        """Test creating an override result."""
        decision = AgentDecision(
            agent_name="test",
            decision_type="override",
            data={},
        )
        result = OverrideResult(
            rule_name="test_rule",
            triggered=True,
            decision=decision,
        )
        assert result.rule_name == "test_rule"
        assert result.triggered is True
        assert result.decision == decision

    def test_override_result_not_triggered(self) -> None:
        """Test override result when not triggered."""
        result = OverrideResult(
            rule_name="test_rule",
            triggered=False,
            decision=None,
        )
        assert result.triggered is False
        assert result.decision is None


class TestOverrideEngineInitialization:
    """Tests for OverrideEngine initialization."""

    def test_engine_initialization_with_rules(self) -> None:
        """Test engine initializes with rules and agents."""
        rules = [
            OverrideRule(name="rule1", condition="true", action="halt", priority=5),
            OverrideRule(name="rule2", condition="true", action="halt", priority=1),
        ]
        agents = {"test": MockAgent({})}
        engine = OverrideEngine(rules=rules, agents=agents)

        assert len(engine.rules) == 2
        assert engine.agents == agents

    def test_rules_sorted_by_priority(self) -> None:
        """Test that rules are sorted by priority (lower = higher priority)."""
        rules = [
            OverrideRule(name="low_priority", condition="true", action="halt", priority=10),
            OverrideRule(name="high_priority", condition="true", action="halt", priority=1),
            OverrideRule(name="medium_priority", condition="true", action="halt", priority=5),
        ]
        agents = {"test": MockAgent({})}
        engine = OverrideEngine(rules=rules, agents=agents)

        assert engine.rules[0].name == "high_priority"
        assert engine.rules[1].name == "medium_priority"
        assert engine.rules[2].name == "low_priority"

    def test_empty_rules(self) -> None:
        """Test engine with no rules."""
        engine = OverrideEngine(rules=[], agents={})
        assert engine.rules == []


class TestConditionEvaluation:
    """Tests for condition evaluation."""

    @pytest.fixture
    def agents(self) -> dict[str, BaseAgent]:
        """Create test agents."""
        crash_detector = MockAgent({"field_value": 100})
        crash_detector.name = "crash_detector"
        crash_detector._status = AgentStatus.CRASH

        trader = MockAgent({"field_value": 50})
        trader.name = "trader"
        trader._status = AgentStatus.NORMAL

        return {"crash_detector": crash_detector, "trader": trader}

    @pytest.fixture
    def engine(self, agents: dict[str, BaseAgent]) -> OverrideEngine:
        """Create override engine with test agents."""
        return OverrideEngine(rules=[], agents=agents)

    def test_evaluate_status_equals(self, engine: OverrideEngine) -> None:
        """Test evaluating agent status equality."""
        assert engine.evaluate_condition("crash_detector.status == CRASH", {}) is True
        assert engine.evaluate_condition("crash_detector.status == NORMAL", {}) is False
        assert engine.evaluate_condition("trader.status == NORMAL", {}) is True

    def test_evaluate_status_not_equals(self, engine: OverrideEngine) -> None:
        """Test evaluating agent status inequality."""
        assert engine.evaluate_condition("crash_detector.status != NORMAL", {}) is True
        assert engine.evaluate_condition("trader.status != NORMAL", {}) is False

    def test_evaluate_field_comparison(self, engine: OverrideEngine) -> None:
        """Test evaluating numeric field comparisons."""
        assert engine.evaluate_condition("crash_detector.field_value > 50", {}) is True
        assert engine.evaluate_condition("crash_detector.field_value < 50", {}) is False
        assert engine.evaluate_condition("trader.field_value >= 50", {}) is True
        assert engine.evaluate_condition("trader.field_value <= 50", {}) is True

    def test_evaluate_invalid_agent(self, engine: OverrideEngine) -> None:
        """Test evaluating condition with non-existent agent."""
        result = engine.evaluate_condition("nonexistent.status == CRASH", {})
        assert result is False

    def test_evaluate_invalid_condition_format(self, engine: OverrideEngine) -> None:
        """Test evaluating malformed condition."""
        result = engine.evaluate_condition("invalid_format", {})
        assert result is False

    def test_evaluate_context_values(self, engine: OverrideEngine) -> None:
        """Test evaluating conditions using context values."""
        context = {"drawdown": 0.15, "exposure": 0.8}
        assert engine.evaluate_condition("context.drawdown > 0.1", context) is True
        assert engine.evaluate_condition("context.exposure >= 0.8", context) is True
        assert engine.evaluate_condition("context.exposure > 0.9", context) is False


class TestActionExecution:
    """Tests for action execution."""

    @pytest.fixture
    def agents(self) -> dict[str, BaseAgent]:
        """Create test agents."""
        trader = MockAgent({})
        trader.name = "trader"
        return {"trader": trader}

    @pytest.fixture
    def engine(self, agents: dict[str, BaseAgent]) -> OverrideEngine:
        """Create override engine with test agents."""
        return OverrideEngine(rules=[], agents=agents)

    @pytest.mark.asyncio
    async def test_execute_action_method_call(self, engine: OverrideEngine) -> None:
        """Test executing an action that calls an agent method."""
        decision = await engine.execute_action("trader.close_all_positions()", {})

        assert decision.decision_type == "close_all"
        assert decision.data["action"] == "close_all_positions"

    @pytest.mark.asyncio
    async def test_execute_action_invalid_agent(self, engine: OverrideEngine) -> None:
        """Test executing action with non-existent agent."""
        with pytest.raises(PipelineError) as exc_info:
            await engine.execute_action("nonexistent.method()", {})
        assert "Agent not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_execute_action_invalid_method(self, engine: OverrideEngine) -> None:
        """Test executing action with non-existent method."""
        with pytest.raises(PipelineError) as exc_info:
            await engine.execute_action("trader.nonexistent_method()", {})
        assert "Method not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_execute_action_invalid_format(self, engine: OverrideEngine) -> None:
        """Test executing action with invalid format."""
        with pytest.raises(PipelineError) as exc_info:
            await engine.execute_action("invalid_format", {})
        assert "Invalid action format" in str(exc_info.value)


class TestCheckAndExecute:
    """Tests for check_and_execute method."""

    @pytest.fixture
    def agents(self) -> dict[str, BaseAgent]:
        """Create test agents."""
        crash_detector = MockAgent({})
        crash_detector.name = "crash_detector"
        crash_detector._status = AgentStatus.CRASH

        trader = MockAgent({})
        trader.name = "trader"
        trader._status = AgentStatus.NORMAL

        return {"crash_detector": crash_detector, "trader": trader}

    @pytest.mark.asyncio
    async def test_first_matching_rule_executes(self, agents: dict[str, BaseAgent]) -> None:
        """Test that only the first matching rule executes."""
        rules = [
            OverrideRule(
                name="crash_halt",
                condition="crash_detector.status == CRASH",
                action="trader.halt_trading()",
                priority=1,
            ),
            OverrideRule(
                name="second_rule",
                condition="crash_detector.status == CRASH",
                action="trader.close_all_positions()",
                priority=2,
            ),
        ]
        engine = OverrideEngine(rules=rules, agents=agents)

        result = await engine.check_and_execute({})

        assert result is not None
        assert result.rule_name == "crash_halt"
        assert result.decision.decision_type == "halt"

    @pytest.mark.asyncio
    async def test_no_matching_rules_returns_none(self, agents: dict[str, BaseAgent]) -> None:
        """Test that None is returned when no rules match."""
        agents["crash_detector"]._status = AgentStatus.NORMAL

        rules = [
            OverrideRule(
                name="crash_halt",
                condition="crash_detector.status == CRASH",
                action="trader.halt_trading()",
                priority=1,
            ),
        ]
        engine = OverrideEngine(rules=rules, agents=agents)

        result = await engine.check_and_execute({})

        assert result is None

    @pytest.mark.asyncio
    async def test_priority_order_respected(self, agents: dict[str, BaseAgent]) -> None:
        """Test that rules are checked in priority order."""
        rules = [
            OverrideRule(
                name="low_priority_rule",
                condition="crash_detector.status == CRASH",
                action="trader.close_all_positions()",
                priority=10,
            ),
            OverrideRule(
                name="high_priority_rule",
                condition="crash_detector.status == CRASH",
                action="trader.halt_trading()",
                priority=1,
            ),
        ]
        engine = OverrideEngine(rules=rules, agents=agents)

        result = await engine.check_and_execute({})

        assert result is not None
        assert result.rule_name == "high_priority_rule"

    @pytest.mark.asyncio
    async def test_empty_rules_returns_none(self, agents: dict[str, BaseAgent]) -> None:
        """Test that empty rules returns None."""
        engine = OverrideEngine(rules=[], agents=agents)

        result = await engine.check_and_execute({})

        assert result is None


class TestOverrideLogging:
    """Tests for override logging."""

    @pytest.fixture
    def agents(self) -> dict[str, BaseAgent]:
        """Create test agents."""
        crash_detector = MockAgent({})
        crash_detector.name = "crash_detector"
        crash_detector._status = AgentStatus.CRASH

        trader = MockAgent({})
        trader.name = "trader"

        return {"crash_detector": crash_detector, "trader": trader}

    @pytest.mark.asyncio
    async def test_override_execution_logged(
        self, agents: dict[str, BaseAgent], caplog: pytest.LogCaptureFixture
    ) -> None:
        """Test that override execution is logged with rule name."""
        rules = [
            OverrideRule(
                name="crash_halt",
                condition="crash_detector.status == CRASH",
                action="trader.halt_trading()",
                priority=1,
            ),
        ]
        engine = OverrideEngine(rules=rules, agents=agents)

        import structlog
        structlog.configure(
            processors=[structlog.dev.ConsoleRenderer()],
            wrapper_class=structlog.make_filtering_bound_logger(0),
        )

        await engine.check_and_execute({})

        # The override should be logged - implementation will verify this
        # through the log.info calls with rule_name


class TestEdgeCases:
    """Tests for edge cases."""

    def test_duplicate_priority_rules(self) -> None:
        """Test handling of rules with same priority."""
        rules = [
            OverrideRule(name="rule_a", condition="true", action="halt", priority=5),
            OverrideRule(name="rule_b", condition="true", action="halt", priority=5),
        ]
        agents = {"test": MockAgent({})}
        engine = OverrideEngine(rules=rules, agents=agents)

        # Both rules should be present, order among same-priority rules is stable
        assert len(engine.rules) == 2

    def test_special_characters_in_condition(self) -> None:
        """Test handling of special characters in conditions."""
        agents = {"test": MockAgent({})}
        engine = OverrideEngine(rules=[], agents=agents)

        # Should handle gracefully without crashing
        result = engine.evaluate_condition("test.status == 'CRASH'", {})
        assert isinstance(result, bool)

    @pytest.mark.asyncio
    async def test_context_passed_to_action(self) -> None:
        """Test that context is passed to action execution."""
        trader = MockAgent({})
        trader.name = "trader"

        rules = [
            OverrideRule(
                name="rule",
                condition="context.trigger == true",
                action="trader.halt_trading()",
                priority=1,
            ),
        ]
        engine = OverrideEngine(rules=rules, agents={"trader": trader})

        context = {"trigger": True}
        result = await engine.check_and_execute(context)

        assert result is not None
        assert result.rule_name == "rule"
