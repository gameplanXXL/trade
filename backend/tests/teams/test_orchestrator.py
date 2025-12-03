"""Tests for Team Orchestrator with LangGraph - Story 003-05."""

from typing import Any

import pytest

from src.agents.base import AgentDecision, AgentStatus, BaseAgent
from src.teams.orchestrator import OrchestratorState, TeamOrchestrator
from src.teams.schemas import AgentConfig, OverrideRule, PipelineStep, TeamTemplate


class MockAgent(BaseAgent):
    """Mock agent for testing orchestrator."""

    name = "mock_agent"

    def _configure(self, params: dict[str, Any]) -> None:
        """Configure the mock agent."""
        self.decision_type = params.get("decision_type", "signal")
        self.should_fail = params.get("should_fail", False)

    async def execute(self, context: dict[str, Any]) -> AgentDecision:
        """Execute mock agent logic."""
        return AgentDecision(
            agent_name=self.name,
            decision_type=self.decision_type,
            data={"test": True},
            confidence=0.8,
        )

    async def close_all_positions(
        self, context: dict[str, Any] | None = None
    ) -> AgentDecision:
        """Close all positions action."""
        return AgentDecision(
            agent_name=self.name,
            decision_type="close_all",
            data={"action": "close_all_positions"},
        )


@pytest.fixture
def simple_template() -> TeamTemplate:
    """Create a simple team template for testing."""
    return TeamTemplate(
        name="Test Team",
        version="1.0.0",
        roles={
            "crash_detector": AgentConfig(
                class_name="CrashDetector",
                params={"threshold": 0.9},
            ),
            "analyst": AgentConfig(
                class_name="LLMSignalAnalyst",
                params={},
            ),
            "trader": AgentConfig(
                class_name="Trader",
                params={},
            ),
        },
        pipeline=[
            PipelineStep(agent="crash_detector", method="execute"),
            PipelineStep(agent="analyst", method="execute"),
            PipelineStep(agent="trader", method="execute"),
        ],
        override_rules=[
            OverrideRule(
                name="crash_halt",
                condition="crash_detector.status == CRASH",
                action="trader.close_all_positions()",
                priority=1,
            ),
        ],
    )


class TestOrchestratorState:
    """Tests for OrchestratorState TypedDict."""

    def test_state_structure(self) -> None:
        """Test that OrchestratorState has required keys."""
        state: OrchestratorState = {
            "market_data": {"EURUSD": {"bid": 1.1000}},
            "decisions": [],
            "current_status": AgentStatus.NORMAL,
            "override_triggered": False,
            "override_result": None,
        }

        assert "market_data" in state
        assert "decisions" in state
        assert "current_status" in state
        assert "override_triggered" in state
        assert "override_result" in state


class TestTeamOrchestratorInitialization:
    """Tests for TeamOrchestrator initialization."""

    def test_orchestrator_creates_agents(
        self, simple_template: TeamTemplate
    ) -> None:
        """Test that orchestrator creates agents from template."""
        orchestrator = TeamOrchestrator(simple_template)

        assert "crash_detector" in orchestrator.agents
        assert "analyst" in orchestrator.agents
        assert "trader" in orchestrator.agents

    def test_orchestrator_creates_pipeline_executor(
        self, simple_template: TeamTemplate
    ) -> None:
        """Test that orchestrator creates pipeline executor."""
        orchestrator = TeamOrchestrator(simple_template)

        assert orchestrator.pipeline is not None
        assert orchestrator.pipeline.agents == orchestrator.agents

    def test_orchestrator_creates_override_engine(
        self, simple_template: TeamTemplate
    ) -> None:
        """Test that orchestrator creates override engine."""
        orchestrator = TeamOrchestrator(simple_template)

        assert orchestrator.override_engine is not None
        assert len(orchestrator.override_engine.rules) == 1

    def test_orchestrator_builds_graph(
        self, simple_template: TeamTemplate
    ) -> None:
        """Test that orchestrator builds LangGraph StateGraph."""
        orchestrator = TeamOrchestrator(simple_template)

        assert orchestrator.graph is not None


class TestTeamOrchestratorGraph:
    """Tests for LangGraph configuration."""

    def test_graph_has_check_override_node(
        self, simple_template: TeamTemplate
    ) -> None:
        """Test that graph has check_override node."""
        orchestrator = TeamOrchestrator(simple_template)
        nodes = list(orchestrator.graph.nodes.keys())
        assert "check_override" in nodes

    def test_graph_has_run_pipeline_node(
        self, simple_template: TeamTemplate
    ) -> None:
        """Test that graph has run_pipeline node."""
        orchestrator = TeamOrchestrator(simple_template)
        nodes = list(orchestrator.graph.nodes.keys())
        assert "run_pipeline" in nodes


class TestTeamOrchestratorRunCycle:
    """Tests for run_cycle method."""

    @pytest.mark.asyncio
    async def test_run_cycle_returns_decisions(
        self, simple_template: TeamTemplate
    ) -> None:
        """Test that run_cycle returns list of decisions."""
        orchestrator = TeamOrchestrator(simple_template)
        market_data = {"EURUSD": {"bid": 1.1000, "ask": 1.1002}}

        result = await orchestrator.run_cycle(market_data)

        assert isinstance(result, list)
        for decision in result:
            assert isinstance(decision, AgentDecision)

    @pytest.mark.asyncio
    async def test_run_cycle_without_override(
        self, simple_template: TeamTemplate
    ) -> None:
        """Test run_cycle when no override is triggered."""
        orchestrator = TeamOrchestrator(simple_template)
        # Set all agents to NORMAL to avoid override
        for agent in orchestrator.agents.values():
            agent.set_status(AgentStatus.NORMAL)

        market_data = {"EURUSD": {"bid": 1.1000}}
        result = await orchestrator.run_cycle(market_data)

        # Should have decisions from all pipeline steps
        assert len(result) >= 1

    @pytest.mark.asyncio
    async def test_run_cycle_with_override(
        self, simple_template: TeamTemplate
    ) -> None:
        """Test run_cycle when override is triggered."""
        orchestrator = TeamOrchestrator(simple_template)
        # Set crash_detector to CRASH to trigger override
        orchestrator.agents["crash_detector"].set_status(AgentStatus.CRASH)

        market_data = {"EURUSD": {"bid": 1.1000}}
        result = await orchestrator.run_cycle(market_data)

        # Should have override decision with close_all action
        assert len(result) >= 1
        # The close_all_positions action returns decision_type="action" with action="close_all"
        close_decisions = [
            d for d in result
            if d.data.get("action") == "close_all"
        ]
        assert len(close_decisions) >= 1

        # Verify override was triggered
        state = orchestrator.get_current_state()
        assert state["override_triggered"] is True


class TestTeamOrchestratorState:
    """Tests for state management."""

    def test_initial_state_normal(
        self, simple_template: TeamTemplate
    ) -> None:
        """Test initial state is NORMAL."""
        orchestrator = TeamOrchestrator(simple_template)

        state = orchestrator.get_current_state()

        assert state["current_status"] == AgentStatus.NORMAL
        assert state["override_triggered"] is False

    @pytest.mark.asyncio
    async def test_state_updated_after_cycle(
        self, simple_template: TeamTemplate
    ) -> None:
        """Test state is updated after run_cycle."""
        orchestrator = TeamOrchestrator(simple_template)

        await orchestrator.run_cycle({"EURUSD": {"bid": 1.1000}})
        state = orchestrator.get_current_state()

        assert len(state["decisions"]) > 0


class TestGraphVisualization:
    """Tests for graph visualization."""

    def test_graph_can_be_drawn(
        self, simple_template: TeamTemplate
    ) -> None:
        """Test that graph can generate visualization data."""
        orchestrator = TeamOrchestrator(simple_template)

        # Should not raise
        mermaid_str = orchestrator.get_graph_visualization()

        assert isinstance(mermaid_str, str)
        assert len(mermaid_str) > 0
