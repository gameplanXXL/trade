"""Tests for agent factory and registry."""

from typing import Any

import pytest

from src.agents import (
    AGENT_REGISTRY,
    BaseAgent,
    CrashDetector,
    LLMSignalAnalyst,
    RiskManager,
    Trader,
    create_agent,
    get_available_agents,
    register_agent,
)
from src.agents.base import AgentDecision
from src.core.exceptions import ValidationError


class TestAgentRegistry:
    """Tests for agent registry."""

    def test_registry_contains_crash_detector(self) -> None:
        """Test that CrashDetector is registered."""
        assert "CrashDetector" in AGENT_REGISTRY
        assert AGENT_REGISTRY["CrashDetector"] == CrashDetector

    def test_registry_contains_llm_analyst(self) -> None:
        """Test that LLMSignalAnalyst is registered."""
        assert "LLMSignalAnalyst" in AGENT_REGISTRY
        assert AGENT_REGISTRY["LLMSignalAnalyst"] == LLMSignalAnalyst

    def test_registry_contains_trader(self) -> None:
        """Test that Trader is registered."""
        assert "Trader" in AGENT_REGISTRY
        assert AGENT_REGISTRY["Trader"] == Trader

    def test_registry_contains_risk_manager(self) -> None:
        """Test that RiskManager is registered."""
        assert "RiskManager" in AGENT_REGISTRY
        assert AGENT_REGISTRY["RiskManager"] == RiskManager

    def test_registry_has_four_agents(self) -> None:
        """Test that registry has all four base agents."""
        assert len(AGENT_REGISTRY) >= 4


class TestCreateAgent:
    """Tests for create_agent function."""

    def test_create_crash_detector(self) -> None:
        """Test creating a CrashDetector."""
        agent = create_agent("CrashDetector", {"threshold": 0.8})

        assert isinstance(agent, CrashDetector)
        assert agent.threshold == 0.8

    def test_create_llm_analyst(self) -> None:
        """Test creating an LLMSignalAnalyst."""
        agent = create_agent("LLMSignalAnalyst", {"min_confidence": 0.8})

        assert isinstance(agent, LLMSignalAnalyst)
        assert agent.min_confidence == 0.8

    def test_create_trader(self) -> None:
        """Test creating a Trader."""
        agent = create_agent("Trader", {"max_positions": 5})

        assert isinstance(agent, Trader)
        assert agent.max_positions == 5

    def test_create_risk_manager(self) -> None:
        """Test creating a RiskManager."""
        agent = create_agent("RiskManager", {"max_drawdown": 0.15})

        assert isinstance(agent, RiskManager)
        assert agent.max_drawdown == 0.15

    def test_create_with_empty_params(self) -> None:
        """Test creating an agent with empty params uses defaults."""
        agent = create_agent("CrashDetector", {})

        assert isinstance(agent, CrashDetector)
        assert agent.threshold == 0.9  # default

    def test_create_unknown_agent_raises_error(self) -> None:
        """Test that unknown agent class raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            create_agent("UnknownAgent", {})

        error = exc_info.value
        assert error.code == "VALIDATION_ERROR"
        assert "UnknownAgent" in error.message
        assert "available_agents" in error.details

    def test_create_agent_returns_base_agent(self) -> None:
        """Test that created agents inherit from BaseAgent."""
        for class_name in AGENT_REGISTRY.keys():
            agent = create_agent(class_name, {})
            assert isinstance(agent, BaseAgent)


class TestGetAvailableAgents:
    """Tests for get_available_agents function."""

    def test_returns_list(self) -> None:
        """Test that it returns a list."""
        result = get_available_agents()
        assert isinstance(result, list)

    def test_contains_all_registered_agents(self) -> None:
        """Test that it contains all registered agents."""
        result = get_available_agents()

        assert "CrashDetector" in result
        assert "LLMSignalAnalyst" in result
        assert "Trader" in result
        assert "RiskManager" in result


class TestRegisterAgent:
    """Tests for register_agent function."""

    def test_register_new_agent(self) -> None:
        """Test registering a new agent class."""

        class CustomAgent(BaseAgent):
            name = "custom_agent"

            def _configure(self, params: dict[str, Any]) -> None:
                pass

            async def execute(self, context: dict[str, Any]) -> AgentDecision:
                return AgentDecision(
                    agent_name=self.name, decision_type="signal"
                )

        register_agent("CustomAgent", CustomAgent)

        assert "CustomAgent" in AGENT_REGISTRY
        agent = create_agent("CustomAgent", {})
        assert isinstance(agent, CustomAgent)

        # Cleanup
        del AGENT_REGISTRY["CustomAgent"]

    def test_register_non_base_agent_raises_error(self) -> None:
        """Test that registering non-BaseAgent raises error."""

        class NotAnAgent:
            pass

        with pytest.raises(ValidationError) as exc_info:
            register_agent("NotAnAgent", NotAnAgent)  # type: ignore

        assert "inherit from BaseAgent" in str(exc_info.value)


class TestTeamLoaderIntegration:
    """Integration tests with TeamLoader."""

    def test_create_agents_from_template_roles(self) -> None:
        """Test creating agents from a team template's roles."""
        # Simulate template roles
        roles = {
            "crash_detector": {
                "class_name": "CrashDetector",
                "params": {"threshold": 0.85},
            },
            "analyst": {
                "class_name": "LLMSignalAnalyst",
                "params": {"min_confidence": 0.7},
            },
            "trader": {
                "class_name": "Trader",
                "params": {"position_sizing": "conservative"},
            },
            "risk_manager": {
                "class_name": "RiskManager",
                "params": {"max_drawdown": 0.20},
            },
        }

        # Create agents from roles
        agents = {}
        for role_name, config in roles.items():
            agents[role_name] = create_agent(
                config["class_name"], config["params"]
            )

        # Verify all agents created correctly
        assert len(agents) == 4
        assert isinstance(agents["crash_detector"], CrashDetector)
        assert isinstance(agents["analyst"], LLMSignalAnalyst)
        assert isinstance(agents["trader"], Trader)
        assert isinstance(agents["risk_manager"], RiskManager)

        # Verify params applied
        assert agents["crash_detector"].threshold == 0.85
        assert agents["analyst"].min_confidence == 0.7
        assert agents["risk_manager"].max_drawdown == 0.20
