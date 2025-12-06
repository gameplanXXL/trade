"""Team Templates REST API endpoints - Story 008-05."""

from datetime import UTC, datetime
from pathlib import Path

import structlog
from fastapi import APIRouter, HTTPException, status

from src.api.schemas.template import TemplateListResponse, TemplateResponse
from src.config.settings import get_settings
from src.core.exceptions import ConfigurationError, ValidationError
from src.teams.loader import TeamLoader
from src.teams.schemas import TeamTemplate

log = structlog.get_logger()

router = APIRouter(prefix="/api/team-templates", tags=["templates"])

settings = get_settings()


def get_templates_directory() -> Path:
    """Get the path to the team templates directory."""
    # Templates are in the project root under team_templates/
    base_dir = Path(__file__).parent.parent.parent.parent
    return base_dir / "team_templates"


@router.get("/", response_model=TemplateListResponse)
async def list_templates() -> dict:
    """List all available team templates.

    Returns a list of templates with metadata for the UI.
    """
    loader = TeamLoader()
    templates_dir = get_templates_directory()

    try:
        template_files = loader.list_templates(templates_dir)
    except ConfigurationError as e:
        log.error("failed_to_list_templates", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "TEMPLATE_LIST_ERROR", "message": str(e)},
        )

    templates = []
    for template_file in template_files:
        template_path = templates_dir / template_file
        try:
            template = loader.load_template(template_path)
            templates.append(
                TemplateResponse.from_template(
                    name=template_file.replace(".yaml", "").replace(".yml", ""),
                    template=template,
                )
            )
        except (ConfigurationError, ValidationError) as e:
            log.warning(
                "skipping_invalid_template",
                template_file=template_file,
                error=str(e),
            )
            # Skip invalid templates instead of failing the whole request
            continue

    return {
        "data": templates,
        "meta": {"timestamp": datetime.now(UTC).isoformat()},
    }


@router.get("/{template_name}", response_model=TemplateResponse)
async def get_template(template_name: str) -> TemplateResponse:
    """Get details for a specific team template.

    Args:
        template_name: Name of the template (without .yaml extension).

    Returns:
        Template details including roles and pipeline.
    """
    loader = TeamLoader()
    templates_dir = get_templates_directory()

    # Try both .yaml and .yml extensions
    template_path = templates_dir / f"{template_name}.yaml"
    if not template_path.exists():
        template_path = templates_dir / f"{template_name}.yml"

    if not template_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "TEMPLATE_NOT_FOUND",
                "message": f"Template '{template_name}' not found",
            },
        )

    try:
        template = loader.load_template(template_path)
        return TemplateResponse.from_template(name=template_name, template=template)
    except (ConfigurationError, ValidationError) as e:
        log.error(
            "failed_to_load_template",
            template_name=template_name,
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_TEMPLATE", "message": str(e)},
        )
