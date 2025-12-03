"""YAML loader for team templates."""

from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError as PydanticValidationError

from src.core.exceptions import ConfigurationError, ValidationError
from src.teams.schemas import TeamTemplate


class TeamLoader:
    """Loads and validates team templates from YAML files."""

    def load_template(self, path: Path) -> TeamTemplate:
        """Load and validate a team template from a YAML file.

        Args:
            path: Path to the YAML template file.

        Returns:
            Validated TeamTemplate instance.

        Raises:
            ConfigurationError: If file cannot be read or parsed.
            ValidationError: If template validation fails.
        """
        if not path.exists():
            raise ConfigurationError(
                f"Template file not found: {path}",
                details={"path": str(path)},
            )

        try:
            with open(path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ConfigurationError(
                f"Invalid YAML in template: {path}",
                details={"path": str(path), "error": str(e)},
            ) from e
        except OSError as e:
            raise ConfigurationError(
                f"Cannot read template file: {path}",
                details={"path": str(path), "error": str(e)},
            ) from e

        if data is None:
            raise ValidationError(
                f"Empty template file: {path}",
                details={"path": str(path)},
            )

        return self._parse_template(data, path)

    def _parse_template(self, data: dict[str, Any], path: Path) -> TeamTemplate:
        """Parse and validate template data.

        Args:
            data: Parsed YAML data.
            path: Path to the template file (for error messages).

        Returns:
            Validated TeamTemplate instance.

        Raises:
            ValidationError: If template validation fails.
        """
        try:
            return TeamTemplate(**data)
        except PydanticValidationError as e:
            errors = []
            for error in e.errors():
                loc = ".".join(str(x) for x in error["loc"])
                msg = error["msg"]
                errors.append(f"{loc}: {msg}")

            raise ValidationError(
                f"Invalid template: {path}",
                details={
                    "path": str(path),
                    "errors": errors,
                },
            ) from e

    def list_templates(self, directory: Path) -> list[str]:
        """List all available template files in a directory.

        Args:
            directory: Path to the templates directory.

        Returns:
            List of template filenames (without directory path).

        Raises:
            ConfigurationError: If directory doesn't exist or isn't readable.
        """
        if not directory.exists():
            raise ConfigurationError(
                f"Templates directory not found: {directory}",
                details={"directory": str(directory)},
            )

        if not directory.is_dir():
            raise ConfigurationError(
                f"Not a directory: {directory}",
                details={"directory": str(directory)},
            )

        templates = []
        for file_path in sorted(directory.glob("*.yaml")):
            templates.append(file_path.name)
        for file_path in sorted(directory.glob("*.yml")):
            if file_path.stem + ".yaml" not in [t.rsplit(".", 1)[0] + ".yaml" for t in templates]:
                templates.append(file_path.name)

        return templates

    def validate_template(self, template: TeamTemplate) -> list[str]:
        """Validate a template and return warnings.

        Performs additional semantic validation beyond Pydantic schema validation.

        Args:
            template: TeamTemplate to validate.

        Returns:
            List of warning messages (empty list = valid).
        """
        warnings = []

        # Check for unused roles
        used_roles = {step.agent for step in template.pipeline}
        unused_roles = set(template.roles.keys()) - used_roles
        if unused_roles:
            warnings.append(
                f"Unused roles defined but not in pipeline: {', '.join(sorted(unused_roles))}"
            )

        # Check for recommended agents
        role_class_names = {
            config.class_name.lower()
            for config in template.roles.values()
        }
        if "riskmanager" not in role_class_names and "risk_manager" not in role_class_names:
            warnings.append("No RiskManager agent defined - recommended for production use")

        # Check override rule priorities
        priorities = [rule.priority for rule in template.override_rules]
        if len(priorities) != len(set(priorities)):
            warnings.append("Multiple override rules share the same priority")

        # Check pipeline has at least 2 steps for meaningful workflow
        if len(template.pipeline) < 2:
            warnings.append("Pipeline has only one step - consider adding more agents")

        return warnings
