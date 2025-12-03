"""Tests for team YAML loader."""

from pathlib import Path
from textwrap import dedent

import pytest

from src.core.exceptions import ConfigurationError, ValidationError
from src.teams.loader import TeamLoader
from src.teams.schemas import TeamTemplate


@pytest.fixture
def loader() -> TeamLoader:
    """Create a TeamLoader instance."""
    return TeamLoader()


@pytest.fixture
def tmp_templates_dir(tmp_path: Path) -> Path:
    """Create a temporary templates directory."""
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()
    return templates_dir


@pytest.fixture
def valid_yaml_content() -> str:
    """Provide valid YAML template content."""
    return dedent("""\
        name: "Test Team"
        version: "1.0.0"
        roles:
          detector:
            class_name: TestDetector
            params:
              threshold: 0.5
          trader:
            class_name: TestTrader
            params: {}
        pipeline:
          - agent: detector
            method: analyze
          - agent: trader
            method: execute
        override_rules:
          - name: "halt_rule"
            condition: "detector.alert"
            action: "trader.halt"
            priority: 1
    """)


class TestTeamLoaderLoadTemplate:
    """Tests for TeamLoader.load_template method."""

    def test_load_valid_template(
        self, loader: TeamLoader, tmp_templates_dir: Path, valid_yaml_content: str
    ) -> None:
        """Test loading a valid YAML template."""
        template_path = tmp_templates_dir / "test.yaml"
        template_path.write_text(valid_yaml_content, encoding="utf-8")

        result = loader.load_template(template_path)

        assert isinstance(result, TeamTemplate)
        assert result.name == "Test Team"
        assert result.version == "1.0.0"
        assert len(result.roles) == 2
        assert len(result.pipeline) == 2
        assert len(result.override_rules) == 1

    def test_load_template_file_not_found(
        self, loader: TeamLoader, tmp_templates_dir: Path
    ) -> None:
        """Test that missing file raises ConfigurationError."""
        with pytest.raises(ConfigurationError) as exc_info:
            loader.load_template(tmp_templates_dir / "nonexistent.yaml")

        assert "not found" in str(exc_info.value).lower()
        assert exc_info.value.code == "CONFIGURATION_ERROR"

    def test_load_invalid_yaml_syntax(
        self, loader: TeamLoader, tmp_templates_dir: Path
    ) -> None:
        """Test that invalid YAML syntax raises ConfigurationError."""
        template_path = tmp_templates_dir / "invalid.yaml"
        template_path.write_text("name: [invalid yaml syntax", encoding="utf-8")

        with pytest.raises(ConfigurationError) as exc_info:
            loader.load_template(template_path)

        assert "invalid yaml" in str(exc_info.value).lower()

    def test_load_empty_template(
        self, loader: TeamLoader, tmp_templates_dir: Path
    ) -> None:
        """Test that empty template raises ValidationError."""
        template_path = tmp_templates_dir / "empty.yaml"
        template_path.write_text("", encoding="utf-8")

        with pytest.raises(ValidationError) as exc_info:
            loader.load_template(template_path)

        assert "empty" in str(exc_info.value).lower()

    def test_load_template_validation_error(
        self, loader: TeamLoader, tmp_templates_dir: Path
    ) -> None:
        """Test that invalid template data raises ValidationError with details."""
        template_path = tmp_templates_dir / "invalid_data.yaml"
        template_path.write_text(
            dedent("""\
                name: "Test"
                version: "invalid-version"
                roles: {}
                pipeline: []
            """),
            encoding="utf-8",
        )

        with pytest.raises(ValidationError) as exc_info:
            loader.load_template(template_path)

        error = exc_info.value
        assert error.code == "VALIDATION_ERROR"
        assert "errors" in error.details
        assert len(error.details["errors"]) > 0

    def test_load_template_utf8_encoding(
        self, loader: TeamLoader, tmp_templates_dir: Path
    ) -> None:
        """Test that UTF-8 encoded files are properly loaded."""
        template_path = tmp_templates_dir / "utf8.yaml"
        content = dedent("""\
            name: "Testteam mit Umläuten äöü"
            version: "1.0.0"
            roles:
              trader:
                class_name: Trader
                params: {}
            pipeline:
              - agent: trader
                method: execute
        """)
        template_path.write_text(content, encoding="utf-8")

        result = loader.load_template(template_path)

        assert "Umläuten" in result.name
        assert "äöü" in result.name


class TestTeamLoaderListTemplates:
    """Tests for TeamLoader.list_templates method."""

    def test_list_templates_empty_directory(
        self, loader: TeamLoader, tmp_templates_dir: Path
    ) -> None:
        """Test listing templates in empty directory."""
        result = loader.list_templates(tmp_templates_dir)
        assert result == []

    def test_list_templates_with_yaml_files(
        self, loader: TeamLoader, tmp_templates_dir: Path, valid_yaml_content: str
    ) -> None:
        """Test listing templates returns yaml files."""
        (tmp_templates_dir / "team1.yaml").write_text(valid_yaml_content)
        (tmp_templates_dir / "team2.yaml").write_text(valid_yaml_content)
        (tmp_templates_dir / "readme.txt").write_text("not a template")

        result = loader.list_templates(tmp_templates_dir)

        assert len(result) == 2
        assert "team1.yaml" in result
        assert "team2.yaml" in result
        assert "readme.txt" not in result

    def test_list_templates_includes_yml_extension(
        self, loader: TeamLoader, tmp_templates_dir: Path, valid_yaml_content: str
    ) -> None:
        """Test that .yml files are also listed."""
        (tmp_templates_dir / "team1.yml").write_text(valid_yaml_content)

        result = loader.list_templates(tmp_templates_dir)

        assert "team1.yml" in result

    def test_list_templates_directory_not_found(
        self, loader: TeamLoader, tmp_path: Path
    ) -> None:
        """Test that missing directory raises ConfigurationError."""
        with pytest.raises(ConfigurationError) as exc_info:
            loader.list_templates(tmp_path / "nonexistent")

        assert "not found" in str(exc_info.value).lower()

    def test_list_templates_not_a_directory(
        self, loader: TeamLoader, tmp_path: Path
    ) -> None:
        """Test that file path raises ConfigurationError."""
        file_path = tmp_path / "file.txt"
        file_path.write_text("content")

        with pytest.raises(ConfigurationError) as exc_info:
            loader.list_templates(file_path)

        assert "not a directory" in str(exc_info.value).lower()


class TestTeamLoaderValidateTemplate:
    """Tests for TeamLoader.validate_template method."""

    def test_validate_valid_template(self, loader: TeamLoader) -> None:
        """Test validating a well-formed template returns no warnings."""
        template = TeamTemplate(
            name="Good Team",
            version="1.0.0",
            roles={
                "detector": {"class_name": "Detector", "params": {}},
                "risk_manager": {"class_name": "RiskManager", "params": {}},
            },
            pipeline=[
                {"agent": "detector", "method": "analyze"},
                {"agent": "risk_manager", "method": "validate"},
            ],
        )

        warnings = loader.validate_template(template)

        assert warnings == []

    def test_validate_unused_roles(self, loader: TeamLoader) -> None:
        """Test that unused roles generate warnings."""
        template = TeamTemplate(
            name="Team with unused",
            version="1.0.0",
            roles={
                "used_agent": {"class_name": "UsedAgent", "params": {}},
                "unused_agent": {"class_name": "UnusedAgent", "params": {}},
                "risk_manager": {"class_name": "RiskManager", "params": {}},
            },
            pipeline=[
                {"agent": "used_agent", "method": "run"},
                {"agent": "risk_manager", "method": "validate"},
            ],
        )

        warnings = loader.validate_template(template)

        assert any("unused" in w.lower() for w in warnings)
        assert any("unused_agent" in w for w in warnings)

    def test_validate_missing_risk_manager(self, loader: TeamLoader) -> None:
        """Test that missing RiskManager generates warning."""
        template = TeamTemplate(
            name="Team without risk",
            version="1.0.0",
            roles={
                "trader": {"class_name": "Trader", "params": {}},
                "analyzer": {"class_name": "Analyzer", "params": {}},
            },
            pipeline=[
                {"agent": "trader", "method": "run"},
                {"agent": "analyzer", "method": "analyze"},
            ],
        )

        warnings = loader.validate_template(template)

        assert any("riskmanager" in w.lower() for w in warnings)

    def test_validate_duplicate_override_priorities(self, loader: TeamLoader) -> None:
        """Test that duplicate override priorities generate warning."""
        template = TeamTemplate(
            name="Team with duplicates",
            version="1.0.0",
            roles={
                "agent": {"class_name": "Agent", "params": {}},
                "risk_manager": {"class_name": "RiskManager", "params": {}},
            },
            pipeline=[
                {"agent": "agent", "method": "run"},
                {"agent": "risk_manager", "method": "validate"},
            ],
            override_rules=[
                {"name": "rule1", "condition": "true", "action": "halt", "priority": 1},
                {"name": "rule2", "condition": "false", "action": "continue", "priority": 1},
            ],
        )

        warnings = loader.validate_template(template)

        assert any("priority" in w.lower() for w in warnings)

    def test_validate_single_pipeline_step(self, loader: TeamLoader) -> None:
        """Test that single pipeline step generates warning."""
        template = TeamTemplate(
            name="Single step team",
            version="1.0.0",
            roles={
                "risk_manager": {"class_name": "RiskManager", "params": {}},
            },
            pipeline=[
                {"agent": "risk_manager", "method": "run"},
            ],
        )

        warnings = loader.validate_template(template)

        assert any("one step" in w.lower() for w in warnings)


class TestConservativeLLMTemplate:
    """Integration tests for the conservative_llm.yaml template."""

    @pytest.fixture
    def templates_path(self) -> Path:
        """Get path to actual templates directory."""
        return Path(__file__).parent.parent.parent / "team_templates"

    def test_conservative_llm_template_exists(self, templates_path: Path) -> None:
        """Test that conservative_llm.yaml exists."""
        template_file = templates_path / "conservative_llm.yaml"
        assert template_file.exists(), f"Template not found at {template_file}"

    def test_conservative_llm_template_loads(
        self, loader: TeamLoader, templates_path: Path
    ) -> None:
        """Test that conservative_llm.yaml loads successfully."""
        template = loader.load_template(templates_path / "conservative_llm.yaml")

        assert template.name == "Conservative LLM Team"
        assert template.version == "1.0.0"

    def test_conservative_llm_template_has_required_roles(
        self, loader: TeamLoader, templates_path: Path
    ) -> None:
        """Test that conservative_llm.yaml has all required roles."""
        template = loader.load_template(templates_path / "conservative_llm.yaml")

        assert "crash_detector" in template.roles
        assert "analyst" in template.roles
        assert "trader" in template.roles
        assert "risk_manager" in template.roles

    def test_conservative_llm_template_validates_clean(
        self, loader: TeamLoader, templates_path: Path
    ) -> None:
        """Test that conservative_llm.yaml passes validation."""
        template = loader.load_template(templates_path / "conservative_llm.yaml")
        warnings = loader.validate_template(template)

        # Analyst role is not in the RiskManager category so we expect that warning
        # But no other warnings should be present
        non_risk_warnings = [w for w in warnings if "riskmanager" not in w.lower()]
        assert non_risk_warnings == [], f"Unexpected warnings: {non_risk_warnings}"
