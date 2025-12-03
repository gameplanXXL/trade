---
epic: 003
story: 02
title: "Override-Rule-Engine implementieren"
status: Ready for Review
story_points: 5
covers: [FR18, FR20, FR21]
---

## Story 3.2: Override-Rule-Engine implementieren

Als Entwickler,
möchte ich eine Override-Rule-Engine,
damit kritische Situationen die normale Pipeline überschreiben.

**Acceptance Criteria:**

**Given** der Pipeline-Executor
**When** ich die Override-Engine implementiere
**Then** existiert `src/teams/override.py`:
```python
class OverrideEngine:
    def __init__(self, rules: list[OverrideRule], agents: dict[str, BaseAgent]):
        self.rules = sorted(rules, key=lambda r: r.priority)
        self.agents = agents

    def evaluate_condition(self, condition: str, context: dict) -> bool:
        """
        Evaluiert Bedingung gegen aktuellen Kontext.
        Beispiel: "crash_detector.status == CRASH"
        """

    async def check_and_execute(self, context: dict) -> OverrideResult | None:
        """
        Prüft alle Regeln in Prioritäts-Reihenfolge.
        Führt erste zutreffende Regel aus und gibt Result zurück.
        None wenn keine Regel zutrifft.
        """

    async def execute_action(self, action: str, context: dict) -> AgentDecision:
        """
        Führt Override-Action aus.
        Beispiel: "trader.close_all_positions()"
        """
```

**And** Regeln werden nach Priorität sortiert (niedrig = höher)
**And** Nur erste zutreffende Regel wird ausgeführt
**And** Override-Execution wird geloggt mit Regel-Name


## Tasks

- [x] Task 1: Condition-Parser implementieren
- [x] Task 2: Action-Executor implementieren
- [x] Task 3: Priority-Sortierung
- [x] Task 4: Override-Logging
- [x] Task 5: Edge-Case Tests

## Technical Notes
- Condition-Evaluation: Einfaches String-Parsing, keine eval()
- Supported Conditions: `agent.status == VALUE`, `agent.field > VALUE`
- Action-Parsing: `agent.method()` oder `agent.method(arg)`

## Prerequisites
Story 3.1

## Dev Agent Record

### Debug Log
- 2025-12-03: Tests zuerst geschrieben (RED phase), dann Implementierung (GREEN phase)

### Implementation Plan
1. OverrideResult Pydantic Model für Ergebnisse
2. OverrideEngine mit rules/agents Initialisierung
3. evaluate_condition() mit Regex-Parser für agent.field op value
4. execute_action() mit Regex-Parser für agent.method()
5. check_and_execute() mit Priority-basierter Ausführung
6. Umfassende Edge-Case Tests

### Completion Notes
- OverrideResult Model implementiert
- OverrideEngine mit Priority-Sortierung (niedrig = höher)
- Condition-Parser unterstützt: ==, !=, >, <, >=, <=
- Unterstützt agent.status, agent.field_value, context.field
- Action-Executor parst agent.method() Format
- Nur erste zutreffende Regel wird ausgeführt
- Alle Override-Aktionen werden mit rule_name geloggt
- 23 Unit Tests geschrieben und bestanden
- Alle 227 Tests der gesamten Test-Suite bestanden (keine Regressionen)
- Linter (ruff) bestanden

## File List
- backend/src/teams/override.py (neu)
- backend/tests/teams/test_override.py (neu)

## Change Log
- 2025-12-03: Story implementiert - OverrideEngine, OverrideResult mit Tests
