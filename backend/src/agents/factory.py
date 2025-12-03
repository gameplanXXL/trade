"""Agent factory and registry for dynamic agent creation."""

from typing import Any

import structlog

from src.agents.analyst import LLMSignalAnalyst
from src.agents.base import BaseAgent
from src.agents.crash_detector import CrashDetector
from src.agents.risk_manager import RiskManager
from src.agents.trader import Trader
from src.core.exceptions import ValidationError

log = structlog.get_logger()


# Agent registry mapping class names to agent classes
AGENT_REGISTRY: dict[str, type[BaseAgent]] = {
    "CrashDetector": CrashDetector,
    "LLMSignalAnalyst": LLMSignalAnalyst,
    "Trader": Trader,
    "RiskManager": RiskManager,
}


def create_agent(class_name: str, params: dict[str, Any]) -> BaseAgent:
    """Create an agent instance from configuration.

    Args:
        class_name: Name of the agent class to instantiate.
        params: Agent-specific configuration parameters.

    Returns:
        Instantiated BaseAgent subclass.

    Raises:
        ValidationError: If the agent class is not found in registry.
    """
    if class_name not in AGENT_REGISTRY:
        raise ValidationError(
            f"Unknown agent class: {class_name}",
            details={
                "class_name": class_name,
                "available_agents": list(AGENT_REGISTRY.keys()),
            },
        )

    agent_class = AGENT_REGISTRY[class_name]
    agent = agent_class(params)

    log.info(
        "agent_created",
        class_name=class_name,
        agent_name=agent.name,
    )

    return agent


def get_available_agents() -> list[str]:
    """Get list of available agent class names.

    Returns:
        List of registered agent class names.
    """
    return list(AGENT_REGISTRY.keys())


def register_agent(class_name: str, agent_class: type[BaseAgent]) -> None:
    """Register a new agent class.

    Allows runtime registration of new agent types.

    Args:
        class_name: Name to register the agent under.
        agent_class: The agent class (must inherit from BaseAgent).

    Raises:
        ValidationError: If the class doesn't inherit from BaseAgent.
    """
    if not issubclass(agent_class, BaseAgent):
        raise ValidationError(
            f"Agent class must inherit from BaseAgent: {class_name}",
            details={"class_name": class_name},
        )

    AGENT_REGISTRY[class_name] = agent_class

    log.info(
        "agent_registered",
        class_name=class_name,
    )
