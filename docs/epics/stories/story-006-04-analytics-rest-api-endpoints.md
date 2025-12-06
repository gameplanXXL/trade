---
epic: 006
story: 04
title: "Analytics REST-API Endpoints"
status: done
story_points: 2
---

## Story 6.4: Analytics REST-API Endpoints

Als Operator,
möchte ich Analytics-Daten über API abrufen,
damit das Dashboard sie anzeigen kann.

**Acceptance Criteria:**

**Given** Analytics-Service
**When** ich API-Endpoints implementiere
**Then** existiert `src/api/routes/analytics.py`:
```python
router = APIRouter(prefix="/api/analytics", tags=["analytics"])

@router.get("/teams/{team_id}/summary", response_model=PerformanceSummary)
async def get_performance_summary(team_id: int):
    """Aktuelle Performance-Metriken"""

@router.get("/teams/{team_id}/history", response_model=list[PerformanceMetric])
async def get_performance_history(
    team_id: int,
    period: str = "daily",
    since: datetime | None = None
):
    """Historische Performance-Daten"""

@router.get("/teams/{team_id}/pnl-by-symbol", response_model=dict[str, Decimal])
async def get_pnl_by_symbol(team_id: int):
    """P/L aufgeschlüsselt nach Symbol"""

@router.get("/teams/{team_id}/activity", response_model=list[AgentDecision])
async def get_agent_activity(
    team_id: int,
    agent: str | None = None,
    type: str | None = None,
    limit: int = 100
):
    """Agent-Entscheidungshistorie"""
```

**Technical Notes:**
- Caching-Header für History-Endpoints
- Query-Parameter für Filterung
- Pagination mit `offset` und `limit`

**Prerequisites:** Story 6.1, 6.2, 6.3

---

## Implementation Notes (2025-12-06)

**Story vollständig umgesetzt:**

- ✅ `src/api/routes/analytics.py` mit allen Endpoints:
  - `GET /api/analytics/teams/{team_id}/summary`: Performance Summary
  - `GET /api/analytics/teams/{team_id}/history`: Historische Metriken
  - `GET /api/analytics/teams/{team_id}/pnl-by-symbol`: P/L nach Symbol
  - `GET /api/analytics/teams/{team_id}/activity`: Agent-Entscheidungen
  - `GET /api/analytics/teams/{team_id}/activity-summary`: Aggregierte Activity
- ✅ Query-Parameter für Filterung (period, since, limit, agent, type)
- ✅ Pydantic Response Models für Validierung
- ✅ HTTP 404 Handling für nicht gefundene Teams
- ✅ Strukturiertes Logging
