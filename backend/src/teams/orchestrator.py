"""Team Orchestrator with LangGraph for agent coordination - Story 003-05."""

from datetime import UTC, datetime
from typing import Any, TypedDict

import structlog
from langgraph.graph import END, StateGraph

from src.agents.base import AgentDecision, AgentStatus, BaseAgent
from src.agents.factory import create_agent
from src.teams.override import OverrideEngine, OverrideResult
from src.teams.pipeline import PipelineContext, PipelineExecutor
from src.teams.schemas import TeamTemplate

log = structlog.get_logger()


class OrchestratorState(TypedDict):
    """State for the LangGraph orchestrator.

    Attributes:
        market_data: Current market data keyed by symbol.
        decisions: Accumulated agent decisions from the cycle.
        current_status: Overall team status (based on agent states).
        override_triggered: Whether an override rule was triggered.
        override_result: Result of override execution if triggered.
    """

    market_data: dict[str, Any]
    decisions: list[AgentDecision]
    current_status: AgentStatus
    override_triggered: bool
    override_result: OverrideResult | None


class TeamOrchestrator:
    """LangGraph-based orchestrator for team agent coordination.

    Manages the execution of trading cycles including:
    - Override rule checking
    - Pipeline execution
    - State management
    - Audit logging
    """

    def __init__(self, template: TeamTemplate) -> None:
        """Initialize the orchestrator from a team template.

        Args:
            template: TeamTemplate defining agents, pipeline, and rules.
        """
        self.template = template
        self.agents = self._create_agents()
        self.pipeline = PipelineExecutor(self.agents)
        self.override_engine = OverrideEngine(
            rules=template.override_rules,
            agents=self.agents,
        )
        self.graph = self._build_graph()
        self._state = self._create_initial_state()

        log.info(
            "orchestrator_initialized",
            team_name=template.name,
            agent_count=len(self.agents),
            pipeline_steps=len(template.pipeline),
            override_rules=len(template.override_rules),
        )

    def _create_agents(self) -> dict[str, BaseAgent]:
        """Create agent instances from template roles.

        Returns:
            Dictionary mapping role names to agent instances.
        """
        agents: dict[str, BaseAgent] = {}

        for role_name, config in self.template.roles.items():
            agent = create_agent(config.class_name, config.params)
            agents[role_name] = agent

        return agents

    def _create_initial_state(self) -> OrchestratorState:
        """Create the initial orchestrator state.

        Returns:
            Initial state with empty decisions and NORMAL status.
        """
        return OrchestratorState(
            market_data={},
            decisions=[],
            current_status=AgentStatus.NORMAL,
            override_triggered=False,
            override_result=None,
        )

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph StateGraph for orchestration.

        The graph has the following structure:
        1. check_override: Check if any override rules match
        2. If override triggered -> END
        3. run_pipeline: Execute the agent pipeline
        4. END

        Returns:
            Compiled StateGraph for cycle execution.
        """
        # Define the graph with state schema
        graph = StateGraph(OrchestratorState)

        # Add nodes
        graph.add_node("check_override", self._node_check_override)
        graph.add_node("run_pipeline", self._node_run_pipeline)

        # Set entry point
        graph.set_entry_point("check_override")

        # Add conditional edge from check_override
        graph.add_conditional_edges(
            "check_override",
            self._route_after_override,
            {
                "override_triggered": END,
                "continue": "run_pipeline",
            },
        )

        # Add edge from run_pipeline to END
        graph.add_edge("run_pipeline", END)

        return graph.compile()

    async def _node_check_override(
        self, state: OrchestratorState
    ) -> dict[str, Any]:
        """Node: Check override rules.

        Args:
            state: Current orchestrator state.

        Returns:
            Updated state dict with override check results.
        """
        log.debug(
            "orchestrator_check_override",
            team_name=self.template.name,
            timestamp=datetime.now(UTC).isoformat(),
        )

        result = await self.override_engine.check_and_execute(state["market_data"])

        if result is not None:
            log.info(
                "orchestrator_override_triggered",
                team_name=self.template.name,
                rule_name=result.rule_name,
                timestamp=datetime.now(UTC).isoformat(),
            )

            return {
                "override_triggered": True,
                "override_result": result,
                "decisions": [result.decision] if result.decision else [],
                "current_status": AgentStatus.CRASH,
            }

        return {
            "override_triggered": False,
            "override_result": None,
        }

    def _route_after_override(self, state: OrchestratorState) -> str:
        """Conditional routing after override check.

        Args:
            state: Current orchestrator state.

        Returns:
            "override_triggered" if override was triggered, "continue" otherwise.
        """
        if state.get("override_triggered", False):
            return "override_triggered"
        return "continue"

    async def _node_run_pipeline(
        self, state: OrchestratorState
    ) -> dict[str, Any]:
        """Node: Run the agent pipeline.

        Args:
            state: Current orchestrator state.

        Returns:
            Updated state dict with pipeline decisions.
        """
        log.debug(
            "orchestrator_run_pipeline",
            team_name=self.template.name,
            pipeline_steps=len(self.template.pipeline),
            timestamp=datetime.now(UTC).isoformat(),
        )

        # Initialize pipeline context
        self.pipeline.context = PipelineContext(
            team_id=0,  # Will be set by TeamInstance
            symbols=list(state["market_data"].keys()),
            market_data=state["market_data"],
        )

        # Execute pipeline
        decisions = await self.pipeline.run(self.template.pipeline)

        # Determine overall status from agent states
        overall_status = self._determine_overall_status()

        log.info(
            "orchestrator_pipeline_completed",
            team_name=self.template.name,
            decisions_count=len(decisions),
            overall_status=overall_status.value,
            timestamp=datetime.now(UTC).isoformat(),
        )

        return {
            "decisions": decisions,
            "current_status": overall_status,
        }

    def _determine_overall_status(self) -> AgentStatus:
        """Determine overall team status from agent states.

        Returns highest severity status from all agents.

        Returns:
            CRASH if any agent is CRASH,
            WARNING if any agent is WARNING,
            NORMAL otherwise.
        """
        for agent in self.agents.values():
            if agent.status == AgentStatus.CRASH:
                return AgentStatus.CRASH

        for agent in self.agents.values():
            if agent.status == AgentStatus.WARNING:
                return AgentStatus.WARNING

        return AgentStatus.NORMAL

    async def run_cycle(
        self, market_data: dict[str, Any]
    ) -> list[AgentDecision]:
        """Run a complete trading cycle.

        1. Check override rules
        2. Run pipeline if no override
        3. Return decisions

        Args:
            market_data: Current market data keyed by symbol.

        Returns:
            List of AgentDecisions from the cycle.
        """
        cycle_start = datetime.now(UTC)

        log.info(
            "orchestrator_cycle_starting",
            team_name=self.template.name,
            symbols=list(market_data.keys()),
            timestamp=cycle_start.isoformat(),
        )

        # Initialize state for this cycle
        initial_state: OrchestratorState = {
            "market_data": market_data,
            "decisions": [],
            "current_status": AgentStatus.NORMAL,
            "override_triggered": False,
            "override_result": None,
        }

        # Run the graph
        final_state = await self.graph.ainvoke(initial_state)

        # Update internal state
        self._state = final_state

        cycle_duration = (datetime.now(UTC) - cycle_start).total_seconds() * 1000

        log.info(
            "orchestrator_cycle_completed",
            team_name=self.template.name,
            decisions_count=len(final_state["decisions"]),
            override_triggered=final_state["override_triggered"],
            overall_status=final_state["current_status"].value
            if isinstance(final_state["current_status"], AgentStatus)
            else final_state["current_status"],
            duration_ms=cycle_duration,
            timestamp=datetime.now(UTC).isoformat(),
        )

        return final_state["decisions"]

    def get_current_state(self) -> OrchestratorState:
        """Get the current orchestrator state.

        Returns:
            Current OrchestratorState.
        """
        return self._state

    def get_graph_visualization(self) -> str:
        """Get Mermaid visualization of the graph.

        Returns:
            Mermaid diagram string for visualization.
        """
        try:
            return self.graph.get_graph().draw_mermaid()
        except Exception as e:
            log.warning(
                "orchestrator_visualization_failed",
                error=str(e),
            )
            # Return a basic representation if Mermaid fails
            return (
                "graph TD\n"
                "    START --> check_override\n"
                "    check_override -->|override| END\n"
                "    check_override -->|continue| run_pipeline\n"
                "    run_pipeline --> END"
            )
