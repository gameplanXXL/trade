"""Base agent abstract class for all trading agents."""

from abc import ABC, abstractmethod
from datetime import UTC, datetime
from enum import Enum
from typing import Any

import structlog
from pydantic import BaseModel, Field

log = structlog.get_logger()


class AgentStatus(str, Enum):
    """Status of an agent in the trading pipeline."""

    NORMAL = "normal"
    WARNING = "warning"
    CRASH = "crash"


class AgentDecision(BaseModel):
    """Decision output from an agent execution."""

    agent_name: str = Field(..., description="Name of the agent that made the decision")
    decision_type: str = Field(
        ...,
        description="Type of decision: signal, warning, rejection, action",
    )
    data: dict[str, Any] = Field(
        default_factory=dict, description="Decision-specific data"
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="When the decision was made"
    )
    confidence: float | None = Field(
        default=None, ge=0.0, le=1.0, description="Confidence level (0.0-1.0)"
    )


class BaseAgent(ABC):
    """Abstract base class for all trading agents.

    All agents in the trading platform must inherit from this class
    and implement the required abstract methods.
    """

    name: str = "base_agent"

    def __init__(self, params: dict[str, Any]) -> None:
        """Initialize the agent with configuration parameters.

        Args:
            params: Agent-specific configuration parameters.
        """
        self.params = params
        self._status = AgentStatus.NORMAL
        self._configure(params)
        log.info(
            "agent_initialized",
            agent_name=self.name,
            status=self._status.value,
        )

    @property
    def status(self) -> AgentStatus:
        """Get the current agent status."""
        return self._status

    @status.setter
    def status(self, value: AgentStatus) -> None:
        """Set the agent status with logging."""
        old_status = self._status
        self._status = value
        if old_status != value:
            log.warning(
                "agent_status_changed",
                agent=self.name,
                old_status=old_status.value,
                new_status=value.value,
            )

    def set_status(self, status: AgentStatus) -> None:
        """Set the agent status with logging.

        This method updates the agent's status and logs the change
        if the status actually changed.

        Args:
            status: The new AgentStatus to set.
        """
        self.status = status

    @abstractmethod
    def _configure(self, params: dict[str, Any]) -> None:
        """Configure the agent with parameters.

        This method is called during initialization to set up
        agent-specific configuration.

        Args:
            params: Agent-specific configuration parameters.
        """

    @abstractmethod
    async def execute(self, context: dict[str, Any]) -> AgentDecision:
        """Execute the agent's logic.

        Args:
            context: Execution context containing market data,
                    previous decisions, and other relevant information.

        Returns:
            AgentDecision containing the agent's decision.
        """

    def to_dict(self) -> dict[str, Any]:
        """Serialize agent state for logging/API.

        Returns:
            Dictionary representation of the agent's current state.
        """
        return {
            "name": self.name,
            "status": self._status.value,
            "params": self.params,
        }
