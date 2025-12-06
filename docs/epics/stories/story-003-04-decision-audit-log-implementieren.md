---
epic: 003
story: 04
title: "Decision-Audit-Log implementieren"
status: completed
story_points: 3
---

## Story 3.4: Decision-Audit-Log implementieren

Als Entwickler,
möchte ich ein Audit-Log für alle Agent-Entscheidungen,
damit ich nachvollziehen kann, was das System entschieden hat.

**Acceptance Criteria:**

**Given** Pipeline-Executor
**When** ich das Audit-Log implementiere
**Then** existiert `src/db/models/agent_decision.py`:
```python
class AgentDecisionLog(Base):
    __tablename__ = "agent_decisions"

    id: Mapped[int] = mapped_column(primary_key=True)
    team_instance_id: Mapped[int] = mapped_column(ForeignKey("team_instances.id"))
    agent_name: Mapped[str] = mapped_column(String(50))
    decision_type: Mapped[str] = mapped_column(String(20))  # signal, warning, rejection, override
    data: Mapped[dict] = mapped_column(JSON)
    confidence: Mapped[float | None]
    created_at: Mapped[datetime] = mapped_column(default=func.now())
```

**And** Pipeline-Executor speichert jede Decision
**And** Override-Executions werden als `decision_type="override"` geloggt

## Tasks

- [x] Task 1: AgentDecisionLog Model erstellen
- [x] Task 2: TeamInstance Placeholder Model für FK
- [x] Task 3: Indexes für team_instance_id und created_at
- [x] Task 4: Unit Tests für Model-Struktur

## Technical Notes
- TimescaleDB Hypertable für schnelle Time-Queries
- Retention: 90 Tage (konfigurierbar)
- Index auf `team_instance_id`, `created_at`

## Prerequisites
Story 1.3, 3.1

## Dev Agent Record

### Debug Log
- 2025-12-03: Tests zuerst geschrieben (RED phase), dann Implementierung (GREEN phase)

### Implementation Plan
1. AgentDecisionLog SQLAlchemy Model in src/db/models.py
2. TeamInstance Placeholder Model für FK-Referenz (volle Impl in Epic 005)
3. JSON Column für data dict
4. Indexes für team_instance_id, created_at, agent_name
5. Unit Tests für Model-Struktur und Column-Typen

### Completion Notes
- AgentDecisionLog Model in src/db/models.py implementiert
- TeamInstance Placeholder Model für FK-Referenz erstellt
- Alle Columns gemäß AC: id, team_instance_id, agent_name, decision_type, data, confidence, created_at
- Indexes auf team_instance_id, created_at, agent_name
- JSON Column für flexible data Struktur
- confidence ist nullable
- 13 Unit Tests geschrieben und bestanden
- Alle 250 Tests bestanden (keine Regressionen)
- Linter (ruff) bestanden

Note: Die Integration in PipelineExecutor (automatisches Speichern) wird in Story 003-05 mit dem TeamOrchestrator implementiert.

## File List
- backend/src/db/models.py (modifiziert)
- backend/tests/db/__init__.py (neu)
- backend/tests/db/test_decision_log.py (neu)

## Change Log
- 2025-12-03: Story implementiert - AgentDecisionLog Model mit Tests
