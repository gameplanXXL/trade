"""Tests for pipeline executor - Story 003-01."""

from datetime import UTC, datetime
from typing import Any

import pytest

from src.agents.base import AgentDecision, BaseAgent
from src.core.exceptions import PipelineError
from src.teams.pipeline import PipelineContext, PipelineExecutor
from src.teams.schemas import PipelineStep


class MockAgent(BaseAgent):
    """Mock agent for testing pipeline execution."""

    name = "mock_agent"

    def _configure(self, params: dict[str, Any]) -> None:
        """Configure the mock agent."""
        self.decision_type = params.get("decision_type", "signal")
        self.should_fail = params.get("should_fail", False)
        self.fail_message = params.get("fail_message", "Mock failure")

    async def execute(self, context: dict[str, Any]) -> AgentDecision:
        """Execute the mock agent's logic."""
        if self.should_fail:
            raise PipelineError(self.fail_message)
        return AgentDecision(
            agent_name=self.name,
            decision_type=self.decision_type,
            data={"context_keys": list(context.keys())},
            confidence=0.8,
        )


class TestPipelineContext:
    """Tests for PipelineContext model."""

    def test_create_pipeline_context_with_required_fields(self) -> None:
        """Test creating context with required fields."""
        context = PipelineContext(
            team_id=1,
            symbols=["EURUSD", "GBPUSD"],
            market_data={"EURUSD": {"price": 1.1234}},
        )
        assert context.team_id == 1
        assert context.symbols == ["EURUSD", "GBPUSD"]
        assert context.market_data == {"EURUSD": {"price": 1.1234}}
        assert context.decisions == []
        assert context.current_step == 0

    def test_pipeline_context_decisions_default(self) -> None:
        """Test that decisions defaults to empty list."""
        context = PipelineContext(
            team_id=1,
            symbols=[],
            market_data={},
        )
        assert context.decisions == []

    def test_pipeline_context_current_step_default(self) -> None:
        """Test that current_step defaults to 0."""
        context = PipelineContext(
            team_id=1,
            symbols=[],
            market_data={},
        )
        assert context.current_step == 0

    def test_pipeline_context_with_existing_decisions(self) -> None:
        """Test creating context with pre-existing decisions."""
        decision = AgentDecision(
            agent_name="test_agent",
            decision_type="signal",
            data={},
        )
        context = PipelineContext(
            team_id=1,
            symbols=["EURUSD"],
            market_data={},
            decisions=[decision],
            current_step=1,
        )
        assert len(context.decisions) == 1
        assert context.current_step == 1

    def test_pipeline_context_model_dump(self) -> None:
        """Test that context can be serialized to dict."""
        context = PipelineContext(
            team_id=1,
            symbols=["EURUSD"],
            market_data={"EURUSD": {"price": 1.1234}},
        )
        data = context.model_dump()
        assert data["team_id"] == 1
        assert data["symbols"] == ["EURUSD"]
        assert data["market_data"] == {"EURUSD": {"price": 1.1234}}
        assert data["decisions"] == []
        assert data["current_step"] == 0


class TestPipelineExecutor:
    """Tests for PipelineExecutor."""

    @pytest.fixture
    def mock_agents(self) -> dict[str, BaseAgent]:
        """Provide a dict of mock agents."""
        return {
            "crash_detector": MockAgent({"decision_type": "warning"}),
            "analyst": MockAgent({"decision_type": "signal"}),
            "trader": MockAgent({"decision_type": "action"}),
        }

    @pytest.fixture
    def executor(self, mock_agents: dict[str, BaseAgent]) -> PipelineExecutor:
        """Provide a PipelineExecutor with mock agents."""
        return PipelineExecutor(agents=mock_agents)

    @pytest.fixture
    def initial_context(self) -> PipelineContext:
        """Provide an initial pipeline context."""
        return PipelineContext(
            team_id=1,
            symbols=["EURUSD"],
            market_data={"EURUSD": {"bid": 1.1000, "ask": 1.1002}},
        )

    def test_executor_initialization(self, mock_agents: dict[str, BaseAgent]) -> None:
        """Test that executor initializes with agents."""
        executor = PipelineExecutor(agents=mock_agents)
        assert executor.agents == mock_agents

    @pytest.mark.asyncio
    async def test_execute_single_step(
        self, executor: PipelineExecutor, initial_context: PipelineContext
    ) -> None:
        """Test executing a single pipeline step."""
        step = PipelineStep(agent="crash_detector", method="execute")
        executor.context = initial_context

        decision = await executor.execute_step(step)

        assert decision.agent_name == "mock_agent"
        assert decision.decision_type == "warning"
        assert "context_keys" in decision.data

    @pytest.mark.asyncio
    async def test_execute_full_pipeline(
        self, executor: PipelineExecutor, initial_context: PipelineContext
    ) -> None:
        """Test executing a full pipeline."""
        pipeline = [
            PipelineStep(agent="crash_detector", method="execute"),
            PipelineStep(agent="analyst", method="execute"),
            PipelineStep(agent="trader", method="execute"),
        ]
        executor.context = initial_context

        decisions = await executor.run(pipeline)

        assert len(decisions) == 3
        assert decisions[0].decision_type == "warning"
        assert decisions[1].decision_type == "signal"
        assert decisions[2].decision_type == "action"

    @pytest.mark.asyncio
    async def test_context_propagation(
        self, executor: PipelineExecutor, initial_context: PipelineContext
    ) -> None:
        """Test that context is propagated between steps."""
        pipeline = [
            PipelineStep(agent="crash_detector", method="execute"),
            PipelineStep(agent="analyst", method="execute"),
        ]
        executor.context = initial_context

        await executor.run(pipeline)

        # After execution, context should have accumulated decisions
        assert len(executor.context.decisions) == 2
        assert executor.context.current_step == 2

    @pytest.mark.asyncio
    async def test_current_step_increments(
        self, executor: PipelineExecutor, initial_context: PipelineContext
    ) -> None:
        """Test that current_step increments correctly."""
        pipeline = [
            PipelineStep(agent="crash_detector", method="execute"),
            PipelineStep(agent="analyst", method="execute"),
        ]
        executor.context = initial_context

        await executor.run(pipeline)

        assert executor.context.current_step == 2

    @pytest.mark.asyncio
    async def test_step_timestamp_logged(
        self, executor: PipelineExecutor, initial_context: PipelineContext
    ) -> None:
        """Test that each step execution has a timestamp."""
        step = PipelineStep(agent="crash_detector", method="execute")
        executor.context = initial_context

        before = datetime.now(UTC)
        decision = await executor.execute_step(step)
        after = datetime.now(UTC)

        assert before <= decision.timestamp <= after

    @pytest.mark.asyncio
    async def test_pipeline_stops_on_critical_error(
        self, initial_context: PipelineContext
    ) -> None:
        """Test that pipeline stops on critical errors."""
        agents = {
            "crash_detector": MockAgent({"decision_type": "warning"}),
            "failing_agent": MockAgent(
                {"should_fail": True, "fail_message": "Critical failure"}
            ),
            "trader": MockAgent({"decision_type": "action"}),
        }
        executor = PipelineExecutor(agents=agents)
        executor.context = initial_context

        pipeline = [
            PipelineStep(agent="crash_detector", method="execute"),
            PipelineStep(agent="failing_agent", method="execute"),
            PipelineStep(agent="trader", method="execute"),
        ]

        with pytest.raises(PipelineError) as exc_info:
            await executor.run(pipeline)

        assert "Critical failure" in str(exc_info.value)
        # Trader should NOT have been called
        assert len(executor.context.decisions) == 1

    @pytest.mark.asyncio
    async def test_invalid_agent_reference(
        self, executor: PipelineExecutor, initial_context: PipelineContext
    ) -> None:
        """Test error when referencing non-existent agent."""
        step = PipelineStep(agent="nonexistent", method="execute")
        executor.context = initial_context

        with pytest.raises(PipelineError) as exc_info:
            await executor.execute_step(step)

        assert "nonexistent" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_invalid_method_reference(
        self, executor: PipelineExecutor, initial_context: PipelineContext
    ) -> None:
        """Test error when referencing non-existent method."""
        step = PipelineStep(agent="crash_detector", method="nonexistent_method")
        executor.context = initial_context

        with pytest.raises(PipelineError) as exc_info:
            await executor.execute_step(step)

        assert "nonexistent_method" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_empty_pipeline(
        self, executor: PipelineExecutor, initial_context: PipelineContext
    ) -> None:
        """Test executing an empty pipeline."""
        executor.context = initial_context

        decisions = await executor.run([])

        assert decisions == []
        assert executor.context.decisions == []

    @pytest.mark.asyncio
    async def test_context_contains_previous_decisions(
        self, executor: PipelineExecutor, initial_context: PipelineContext
    ) -> None:
        """Test that each step receives context with previous decisions."""
        pipeline = [
            PipelineStep(agent="crash_detector", method="execute"),
            PipelineStep(agent="analyst", method="execute"),
        ]
        executor.context = initial_context

        # We need to verify that each step receives updated context
        call_count = 0
        original_execute = executor.execute_step

        async def tracking_execute(step: PipelineStep) -> AgentDecision:
            nonlocal call_count
            call_count += 1
            # Verify decisions count matches steps completed
            assert len(executor.context.decisions) == call_count - 1
            return await original_execute(step)

        executor.execute_step = tracking_execute
        await executor.run(pipeline)

        assert call_count == 2
