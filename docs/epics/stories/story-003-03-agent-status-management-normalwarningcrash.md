---
epic: 003
story: 03
title: "Agent-Status-Management (NORMAL/WARNING/CRASH)"
status: Ready for Review
story_points: 2
covers: [FR19, FR20, FR21]
---

## Story 3.3: Agent-Status-Management (NORMAL/WARNING/CRASH)

Als Entwickler,
möchte ich ein einheitliches Status-Management für Agenten,
damit Override-Regeln auf Status reagieren können.

**Acceptance Criteria:**

**Given** BaseAgent mit Status
**When** ich Status-Management implementiere
**Then** haben alle Agenten:
```python
class BaseAgent:
    status: AgentStatus = AgentStatus.NORMAL

    def set_status(self, status: AgentStatus) -> None:
        old_status = self.status
        self.status = status
        if old_status != status:
            log.warning("agent_status_changed",
                        agent=self.name,
                        old_status=old_status,
                        new_status=status)
```

**And** CrashDetector setzt Status basierend auf Analyse:
  - NORMAL: crash_probability < 0.5
  - WARNING: 0.5 <= crash_probability < threshold
  - CRASH: crash_probability >= threshold

**And** Status-Änderungen triggern WebSocket-Events (Epic 7)

## Tasks

- [x] Task 1: set_status() Methode in BaseAgent hinzufügen
- [x] Task 2: CrashDetector Status-Schwellwerte gemäß AC anpassen
- [x] Task 3: Unit Tests für set_status() schreiben
- [x] Task 4: Unit Tests für neue Schwellwerte schreiben

## Technical Notes
- Status ist Agent-Attribut, nicht global
- Mehrere Agenten können WARNING haben
- CRASH von einem Agent kann Team pausieren

## Prerequisites
Story 2.3, 2.4

## Dev Agent Record

### Debug Log
- 2025-12-03: Tests zuerst geschrieben (RED phase), dann Implementierung (GREEN phase)
- 2025-12-03: Bestehende CrashDetector Tests angepasst für neue Schwellwerte

### Implementation Plan
1. set_status() Methode in BaseAgent hinzufügen (Wrapper um Property Setter)
2. Status-Änderungen als log.warning loggen (statt log.info)
3. CrashDetector _update_status() Schwellwerte anpassen:
   - NORMAL bei < 0.5 (statt < 0.7)
   - WARNING bei >= 0.5 und < threshold (statt >= 0.7)
4. Umfassende Tests für alle Schwellwert-Grenzen

### Completion Notes
- set_status() Methode in BaseAgent implementiert
- Status-Logging auf log.warning geändert mit agent= Parameter
- CrashDetector Schwellwerte gemäß AC angepasst
- CrashDetector verwendet jetzt set_status() statt direkter Zuweisung
- 10 neue Tests für set_status() und Status-Schwellwerte
- Alle 237 Tests bestanden (keine Regressionen)
- Linter (ruff) bestanden

## File List
- backend/src/agents/base.py (modifiziert)
- backend/src/agents/crash_detector.py (modifiziert)
- backend/tests/agents/test_base.py (modifiziert)
- backend/tests/agents/test_crash_detector.py (modifiziert)

## Change Log
- 2025-12-03: Story implementiert - set_status() Methode, angepasste Schwellwerte mit Tests
