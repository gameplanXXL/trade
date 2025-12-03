"""Pydantic models for team YAML configuration validation."""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, model_validator


class AgentType(str, Enum):
    """Available agent types in the trading platform."""

    CRASH_DETECTOR = "crash_detector"
    LLM_ANALYST = "llm_analyst"
    TRADER = "trader"
    RISK_MANAGER = "risk_manager"


class AgentConfig(BaseModel):
    """Configuration for a single agent in a team."""

    class_name: str = Field(..., description="Fully qualified class name of the agent")
    params: dict[str, Any] = Field(
        default_factory=dict, description="Agent-specific parameters"
    )


class PipelineStep(BaseModel):
    """A single step in the team's execution pipeline."""

    agent: str = Field(..., description="Role name of the agent to execute")
    method: str = Field(..., description="Method to call on the agent")


class OverrideRule(BaseModel):
    """Override rule for conditional pipeline behavior."""

    name: str = Field(..., description="Unique name for the rule")
    condition: str = Field(..., description="Condition expression to evaluate")
    action: str = Field(..., description="Action to take when condition is true")
    priority: int = Field(default=10, ge=1, le=100, description="Rule priority (1-100)")


class TeamTemplate(BaseModel):
    """Complete team configuration template."""

    name: str = Field(..., min_length=1, max_length=100, description="Team name")
    version: str = Field(..., pattern=r"^\d+\.\d+\.\d+$", description="Semantic version")
    roles: dict[str, AgentConfig] = Field(
        ..., min_length=1, description="Agent role definitions"
    )
    pipeline: list[PipelineStep] = Field(
        ..., min_length=1, description="Execution pipeline steps"
    )
    override_rules: list[OverrideRule] = Field(
        default_factory=list, description="Override rules for pipeline"
    )

    @model_validator(mode="after")
    def validate_pipeline_references(self) -> "TeamTemplate":
        """Validate that all pipeline steps reference defined roles."""
        defined_roles = set(self.roles.keys())
        for step in self.pipeline:
            if step.agent not in defined_roles:
                raise ValueError(
                    f"Pipeline step references undefined role '{step.agent}'. "
                    f"Defined roles: {', '.join(sorted(defined_roles))}"
                )
        return self

    @model_validator(mode="after")
    def validate_unique_override_names(self) -> "TeamTemplate":
        """Validate that override rule names are unique."""
        names = [rule.name for rule in self.override_rules]
        duplicates = [name for name in names if names.count(name) > 1]
        if duplicates:
            raise ValueError(
                f"Duplicate override rule names: {', '.join(set(duplicates))}"
            )
        return self
