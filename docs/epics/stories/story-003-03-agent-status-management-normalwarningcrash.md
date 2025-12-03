---
epic: 003
story: 03
title: "Agent-Status-Management (NORMAL/WARNING/CRASH)"
status: backlog
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

**Technical Notes:**
- Status ist Agent-Attribut, nicht global
- Mehrere Agenten können WARNING haben
- CRASH von einem Agent kann Team pausieren

**Prerequisites:** Story 2.3, 2.4

