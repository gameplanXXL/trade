---
epic: 002
story: 02
title: "YAML Team-Loader implementieren"
status: backlog
story_points: 3
covers: [FR1, FR2, FR3, FR4, FR5]
---

## Story 2.2: YAML Team-Loader implementieren

Als Entwickler,
möchte ich einen YAML-Loader für Team-Templates,
damit ich Team-Konfigurationen aus Dateien laden kann.

**Acceptance Criteria:**

**Given** die Team-Schemas
**When** ich den Loader implementiere
**Then** existiert `src/teams/loader.py`:
```python
class TeamLoader:
    def load_template(self, path: Path) -> TeamTemplate:
        """Lädt und validiert ein Team-Template aus YAML"""

    def list_templates(self, directory: Path) -> list[str]:
        """Listet alle verfügbaren Templates"""

    def validate_template(self, template: TeamTemplate) -> list[str]:
        """Gibt Liste von Warnings zurück (leere Liste = valid)"""
```

**And** `team_templates/conservative_llm.yaml` existiert als erstes Template:
```yaml
name: "Conservative LLM Team"
version: "1.0"

roles:
  crash_detector:
    class_name: CrashDetector
    params:
      threshold: 0.9
      window_days: 30

  analyst:
    class_name: LLMSignalAnalyst
    params:
      model: "claude-sonnet-4-20250514"
      min_confidence: 0.75

  trader:
    class_name: Trader
    params:
      position_sizing: "conservative"
      max_positions: 2
      trailing_stop_pct: 2.0

  risk_manager:
    class_name: RiskManager
    params:
      max_drawdown: 0.20

pipeline:
  - agent: crash_detector
    method: check
  - agent: analyst
    method: generate_signal
  - agent: trader
    method: prepare_order
  - agent: risk_manager
    method: validate
  - agent: trader
    method: execute

override_rules:
  - name: "Crash Emergency"
    condition: "crash_detector.status == CRASH"
    action: "trader.close_all_positions()"
    priority: 1
```

**And** Invalid YAML gibt `ValidationError` mit Details

**Technical Notes:**
- PyYAML für Parsing
- Pydantic für Validation
- File-Encoding: UTF-8

**Prerequisites:** Story 2.1

