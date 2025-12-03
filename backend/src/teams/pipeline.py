"""Pipeline executor for team agent orchestration - Story 003-01."""

from datetime import UTC, datetime
from typing import Any

import structlog
from pydantic import BaseModel, Field

from src.agents.base import AgentDecision, BaseAgent
from src.core.exceptions import PipelineError
from src.teams.schemas import PipelineStep

log = structlog.get_logger()


class PipelineContext(BaseModel):
    """Context passed between pipeline steps.

    Accumulates decisions from each step and provides
    market data and team information to agents.
    """

    team_id: int = Field(..., description="ID of the team running the pipeline")
    symbols: list[str] = Field(..., description="Trading symbols to process")
    market_data: dict[str, Any] = Field(
        ..., description="Current market data keyed by symbol"
    )
    decisions: list[AgentDecision] = Field(
        default_factory=list,
        description="Accumulated decisions from pipeline steps",
    )
    current_step: int = Field(
        default=0,
        description="Current step index in the pipeline",
    )


class PipelineExecutor:
    """Executes team pipelines sequentially.

    Manages the execution of agent pipeline steps, propagating
    context between steps and handling errors appropriately.
    """

    def __init__(self, agents: dict[str, BaseAgent]) -> None:
        """Initialize the pipeline executor.

        Args:
            agents: Dictionary mapping role names to agent instances.
        """
        self.agents = agents
        self.context: PipelineContext | None = None

    async def execute_step(self, step: PipelineStep) -> AgentDecision:
        """Execute a single pipeline step.

        Args:
            step: The pipeline step to execute.

        Returns:
            AgentDecision from the executed agent.

        Raises:
            PipelineError: If agent or method not found, or execution fails.
        """
        if self.context is None:
            raise PipelineError(
                "Pipeline context not initialized",
                details={"step": step.agent},
            )

        # Validate agent exists
        if step.agent not in self.agents:
            raise PipelineError(
                f"Agent not found: {step.agent}",
                details={
                    "agent": step.agent,
                    "available_agents": list(self.agents.keys()),
                },
            )

        agent = self.agents[step.agent]

        # Validate method exists
        if not hasattr(agent, step.method):
            raise PipelineError(
                f"Method not found: {step.method}",
                details={
                    "agent": step.agent,
                    "method": step.method,
                    "available_methods": [
                        m for m in dir(agent) if not m.startswith("_")
                    ],
                },
            )

        method = getattr(agent, step.method)

        step_start = datetime.now(UTC)

        log.info(
            "pipeline_step_starting",
            team_id=self.context.team_id,
            step=step.agent,
            method=step.method,
            current_step=self.context.current_step,
            timestamp=step_start.isoformat(),
        )

        try:
            # Execute the agent method with context
            decision = await method(self.context.model_dump())

            log.info(
                "pipeline_step_completed",
                team_id=self.context.team_id,
                step=step.agent,
                method=step.method,
                decision_type=decision.decision_type,
                duration_ms=(datetime.now(UTC) - step_start).total_seconds() * 1000,
                timestamp=datetime.now(UTC).isoformat(),
            )

            return decision

        except PipelineError:
            # Re-raise pipeline errors as-is
            raise
        except Exception as e:
            log.error(
                "pipeline_step_failed",
                team_id=self.context.team_id,
                step=step.agent,
                method=step.method,
                error=str(e),
                timestamp=datetime.now(UTC).isoformat(),
            )
            raise PipelineError(
                f"Step execution failed: {step.agent}.{step.method}",
                details={
                    "agent": step.agent,
                    "method": step.method,
                    "error": str(e),
                },
            ) from e

    async def run(self, pipeline: list[PipelineStep]) -> list[AgentDecision]:
        """Execute a complete pipeline.

        Args:
            pipeline: List of pipeline steps to execute in order.

        Returns:
            List of AgentDecisions from all executed steps.

        Raises:
            PipelineError: If any step fails critically.
        """
        if self.context is None:
            raise PipelineError("Pipeline context not initialized")

        pipeline_start = datetime.now(UTC)

        log.info(
            "pipeline_starting",
            team_id=self.context.team_id,
            total_steps=len(pipeline),
            symbols=self.context.symbols,
            timestamp=pipeline_start.isoformat(),
        )

        for step in pipeline:
            decision = await self.execute_step(step)
            self.context.decisions.append(decision)
            self.context.current_step += 1

        pipeline_duration = (datetime.now(UTC) - pipeline_start).total_seconds() * 1000

        log.info(
            "pipeline_completed",
            team_id=self.context.team_id,
            total_steps=len(pipeline),
            total_decisions=len(self.context.decisions),
            duration_ms=pipeline_duration,
            timestamp=datetime.now(UTC).isoformat(),
        )

        return self.context.decisions
