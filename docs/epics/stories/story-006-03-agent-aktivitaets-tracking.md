---
epic: 006
story: 03
title: "Agent-Aktivitäts-Tracking"
status: backlog
story_points: 2
covers: [FR35]
---

## Story 6.3: Agent-Aktivitäts-Tracking

Als Operator,
möchte ich sehen, was Agenten entschieden haben,
damit ich das System-Verhalten nachvollziehen kann.

**Acceptance Criteria:**

**Given** AgentDecisionLog aus Epic 3
**When** ich Aktivitäts-Abfragen implementiere
**Then** existiert in `src/services/analytics.py`:
```python
class AnalyticsService:
    # ... existing methods ...

    async def get_agent_activity(
        self,
        team_id: int,
        agent_name: str | None = None,
        decision_type: str | None = None,
        since: datetime | None = None
    ) -> list[AgentDecisionLog]:
        """Filtert Agent-Entscheidungen"""

    async def get_activity_summary(self, team_id: int) -> ActivitySummary:
        """Zusammenfassung: Signale, Warnungen, Ablehnungen"""
```

**And** ActivitySummary:
```python
class ActivitySummary(BaseModel):
    total_signals: int
    buy_signals: int
    sell_signals: int
    hold_signals: int
    warnings: int
    rejections: int
    overrides: int
```

**And** Filterbar nach Zeitraum und Agent

**Technical Notes:**
- Effiziente Queries mit Indizes
- Pagination für große Ergebnismengen
- JSON-Data aus Decisions für Details

**Prerequisites:** Story 3.4, 6.1

