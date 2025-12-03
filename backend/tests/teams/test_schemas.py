"""Tests for team schema validation."""

import pytest
from pydantic import ValidationError

from src.teams.schemas import (
    AgentConfig,
    AgentType,
    OverrideRule,
    PipelineStep,
    TeamTemplate,
)


class TestAgentType:
    """Tests for AgentType enum."""

    def test_agent_type_values(self) -> None:
        """Test that all expected agent types exist."""
        assert AgentType.CRASH_DETECTOR == "crash_detector"
        assert AgentType.LLM_ANALYST == "llm_analyst"
        assert AgentType.TRADER == "trader"
        assert AgentType.RISK_MANAGER == "risk_manager"

    def test_agent_type_is_string(self) -> None:
        """Test that AgentType is a string enum."""
        assert isinstance(AgentType.CRASH_DETECTOR, str)
        assert AgentType.CRASH_DETECTOR.value == "crash_detector"


class TestAgentConfig:
    """Tests for AgentConfig model."""

    def test_valid_agent_config(self) -> None:
        """Test creating a valid agent config."""
        config = AgentConfig(
            class_name="src.agents.CrashDetector",
            params={"threshold": 0.5, "lookback_period": 100},
        )
        assert config.class_name == "src.agents.CrashDetector"
        assert config.params == {"threshold": 0.5, "lookback_period": 100}

    def test_agent_config_default_params(self) -> None:
        """Test that params defaults to empty dict."""
        config = AgentConfig(class_name="src.agents.CrashDetector")
        assert config.params == {}

    def test_agent_config_missing_class_name(self) -> None:
        """Test that class_name is required."""
        with pytest.raises(ValidationError) as exc_info:
            AgentConfig(params={})  # type: ignore[call-arg]
        assert "class_name" in str(exc_info.value)


class TestPipelineStep:
    """Tests for PipelineStep model."""

    def test_valid_pipeline_step(self) -> None:
        """Test creating a valid pipeline step."""
        step = PipelineStep(agent="crash_detector", method="analyze")
        assert step.agent == "crash_detector"
        assert step.method == "analyze"

    def test_pipeline_step_missing_fields(self) -> None:
        """Test that agent and method are required."""
        with pytest.raises(ValidationError):
            PipelineStep(agent="crash_detector")  # type: ignore[call-arg]
        with pytest.raises(ValidationError):
            PipelineStep(method="analyze")  # type: ignore[call-arg]


class TestOverrideRule:
    """Tests for OverrideRule model."""

    def test_valid_override_rule(self) -> None:
        """Test creating a valid override rule."""
        rule = OverrideRule(
            name="crash_halt",
            condition="crash_detector.status == 'CRASH'",
            action="halt_trading",
            priority=1,
        )
        assert rule.name == "crash_halt"
        assert rule.condition == "crash_detector.status == 'CRASH'"
        assert rule.action == "halt_trading"
        assert rule.priority == 1

    def test_override_rule_default_priority(self) -> None:
        """Test that priority defaults to 10."""
        rule = OverrideRule(
            name="test_rule",
            condition="true",
            action="do_nothing",
        )
        assert rule.priority == 10

    def test_override_rule_priority_bounds(self) -> None:
        """Test that priority must be between 1 and 100."""
        with pytest.raises(ValidationError) as exc_info:
            OverrideRule(
                name="test_rule",
                condition="true",
                action="do_nothing",
                priority=0,
            )
        assert "priority" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            OverrideRule(
                name="test_rule",
                condition="true",
                action="do_nothing",
                priority=101,
            )
        assert "priority" in str(exc_info.value)


class TestTeamTemplate:
    """Tests for TeamTemplate model."""

    @pytest.fixture
    def valid_team_data(self) -> dict:
        """Provide valid team template data."""
        return {
            "name": "Conservative Team",
            "version": "1.0.0",
            "roles": {
                "crash_detector": {
                    "class_name": "src.agents.CrashDetector",
                    "params": {"threshold": 0.5},
                },
                "trader": {
                    "class_name": "src.agents.Trader",
                    "params": {"max_position": 1000},
                },
            },
            "pipeline": [
                {"agent": "crash_detector", "method": "analyze"},
                {"agent": "trader", "method": "execute"},
            ],
            "override_rules": [
                {
                    "name": "crash_halt",
                    "condition": "crash_detector.status == 'CRASH'",
                    "action": "halt_trading",
                    "priority": 1,
                }
            ],
        }

    def test_valid_team_template(self, valid_team_data: dict) -> None:
        """Test creating a valid team template."""
        team = TeamTemplate(**valid_team_data)
        assert team.name == "Conservative Team"
        assert team.version == "1.0.0"
        assert len(team.roles) == 2
        assert len(team.pipeline) == 2
        assert len(team.override_rules) == 1

    def test_team_template_empty_override_rules(self, valid_team_data: dict) -> None:
        """Test that override_rules defaults to empty list."""
        del valid_team_data["override_rules"]
        team = TeamTemplate(**valid_team_data)
        assert team.override_rules == []

    def test_team_template_invalid_version(self, valid_team_data: dict) -> None:
        """Test that version must be semantic version format."""
        valid_team_data["version"] = "1.0"
        with pytest.raises(ValidationError) as exc_info:
            TeamTemplate(**valid_team_data)
        assert "version" in str(exc_info.value)

        valid_team_data["version"] = "v1.0.0"
        with pytest.raises(ValidationError) as exc_info:
            TeamTemplate(**valid_team_data)
        assert "version" in str(exc_info.value)

    def test_team_template_name_constraints(self, valid_team_data: dict) -> None:
        """Test name length constraints."""
        valid_team_data["name"] = ""
        with pytest.raises(ValidationError) as exc_info:
            TeamTemplate(**valid_team_data)
        assert "name" in str(exc_info.value)

        valid_team_data["name"] = "x" * 101
        with pytest.raises(ValidationError) as exc_info:
            TeamTemplate(**valid_team_data)
        assert "name" in str(exc_info.value)

    def test_team_template_requires_roles(self, valid_team_data: dict) -> None:
        """Test that at least one role is required."""
        valid_team_data["roles"] = {}
        with pytest.raises(ValidationError) as exc_info:
            TeamTemplate(**valid_team_data)
        assert "roles" in str(exc_info.value)

    def test_team_template_requires_pipeline(self, valid_team_data: dict) -> None:
        """Test that at least one pipeline step is required."""
        valid_team_data["pipeline"] = []
        with pytest.raises(ValidationError) as exc_info:
            TeamTemplate(**valid_team_data)
        assert "pipeline" in str(exc_info.value)

    def test_pipeline_references_defined_roles(self, valid_team_data: dict) -> None:
        """Test that pipeline steps must reference defined roles."""
        valid_team_data["pipeline"].append(
            {"agent": "undefined_agent", "method": "process"}
        )
        with pytest.raises(ValidationError) as exc_info:
            TeamTemplate(**valid_team_data)
        error_msg = str(exc_info.value)
        assert "undefined_agent" in error_msg
        assert "undefined role" in error_msg.lower()

    def test_override_rule_names_unique(self, valid_team_data: dict) -> None:
        """Test that override rule names must be unique."""
        valid_team_data["override_rules"] = [
            {
                "name": "duplicate_name",
                "condition": "true",
                "action": "action1",
            },
            {
                "name": "duplicate_name",
                "condition": "false",
                "action": "action2",
            },
        ]
        with pytest.raises(ValidationError) as exc_info:
            TeamTemplate(**valid_team_data)
        error_msg = str(exc_info.value)
        assert "duplicate" in error_msg.lower()

    def test_clear_validation_error_messages(self, valid_team_data: dict) -> None:
        """Test that validation errors provide clear messages."""
        # Test undefined role error message
        valid_team_data["pipeline"] = [
            {"agent": "nonexistent_role", "method": "do_something"}
        ]
        with pytest.raises(ValidationError) as exc_info:
            TeamTemplate(**valid_team_data)
        error_msg = str(exc_info.value)
        assert "nonexistent_role" in error_msg
        assert "crash_detector" in error_msg  # Should list defined roles
