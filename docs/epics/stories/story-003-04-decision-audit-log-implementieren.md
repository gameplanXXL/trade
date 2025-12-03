---
epic: 003
story: 04
title: "Decision-Audit-Log implementieren"
status: backlog
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

**Technical Notes:**
- TimescaleDB Hypertable für schnelle Time-Queries
- Retention: 90 Tage (konfigurierbar)
- Index auf `team_instance_id`, `created_at`

**Prerequisites:** Story 1.3, 3.1

