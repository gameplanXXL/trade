"""Template API schemas for request/response models - Story 008-05."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from src.teams.schemas import TeamTemplate


class TemplateResponse(BaseModel):
    """Response schema for a team template."""

    name: str = Field(..., description="Template identifier (filename without extension)")
    display_name: str = Field(..., description="Human-readable template name")
    description: str = Field(..., description="Template description")
    version: str = Field(..., description="Template version")
    roles: list[str] = Field(..., description="List of agent roles in this template")
    pipeline: str = Field(..., description="Pipeline description")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "conservative_llm",
                "display_name": "Conservative LLM Team",
                "description": "LLM-based trading with conservative risk management",
                "version": "1.0.0",
                "roles": ["crash_detector", "analyst", "trader", "risk_manager"],
                "pipeline": "crash_detector → analyst → trader → risk_manager → trader",
            }
        }
    )

    @classmethod
    def from_template(cls, name: str, template: TeamTemplate) -> "TemplateResponse":
        """Create response from TeamTemplate instance.

        Args:
            name: Template identifier (filename without extension).
            template: Validated TeamTemplate instance.

        Returns:
            TemplateResponse with formatted data.
        """
        # Build pipeline description
        pipeline_steps = " → ".join(
            f"{step.agent}.{step.method}" for step in template.pipeline
        )

        # Extract roles
        roles = list(template.roles.keys())

        # Create description from template name
        description = template.name

        return cls(
            name=name,
            display_name=template.name,
            description=description,
            version=template.version,
            roles=roles,
            pipeline=pipeline_steps,
        )


class TemplateListResponse(BaseModel):
    """Response schema for list of templates with metadata."""

    data: list[TemplateResponse]
    meta: dict[str, Any] = Field(
        default_factory=dict,
        description="Metadata about the response",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "data": [
                    {
                        "name": "conservative_llm",
                        "display_name": "Conservative LLM Team",
                        "description": "LLM-based trading with conservative risk management",
                        "version": "1.0.0",
                        "roles": ["crash_detector", "analyst", "trader", "risk_manager"],
                        "pipeline": "crash_detector → analyst → trader → risk_manager → trader",
                    }
                ],
                "meta": {"timestamp": "2025-12-06T10:00:00Z"},
            }
        }
    )
