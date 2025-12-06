# Epic 6: Performance Analytics

**Epic Goal:** User sieht Trading-Metriken (P/L, Win-Rate, Sharpe Ratio, Drawdown) für jede Team-Instanz

---

## Story 6.1: Analytics-Service mit Metriken-Berechnung ✅

**Status:** completed

Als Operator,
möchte ich Trading-Metriken für jede Team-Instanz,
damit ich die Performance objektiv bewerten kann.

**Acceptance Criteria:**

**Given** Trades-Daten in der Datenbank
**When** ich den Analytics-Service implementiere
**Then** existiert `src/services/analytics.py`:
```python
class AnalyticsService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def calculate_total_pnl(self, team_id: int) -> Decimal:
        """Gesamt-P/L (realized + unrealized)"""

    async def calculate_pnl_by_symbol(self, team_id: int) -> dict[str, Decimal]:
        """P/L aufgeschlüsselt nach Symbol"""

    async def calculate_win_rate(self, team_id: int) -> float:
        """Gewinn-Trades / Gesamt-Trades"""

    async def calculate_sharpe_ratio(self, team_id: int, risk_free_rate: float = 0.02) -> float:
        """Risikoadjustierte Rendite"""

    async def calculate_max_drawdown(self, team_id: int) -> float:
        """Maximaler Rückgang vom Peak"""

    async def get_performance_summary(self, team_id: int) -> PerformanceSummary:
        """Alle Metriken in einem Call"""
```

**And** Formeln:
  - Win Rate = Count(pnl > 0) / Count(all trades)
  - Sharpe = (Mean Return - Risk Free) / Std Dev
  - Max Drawdown = (Peak - Trough) / Peak

**And** Performance-Summary für API-Response:
```python
class PerformanceSummary(BaseModel):
    total_pnl: Decimal
    total_pnl_percent: float
    win_rate: float
    sharpe_ratio: float
    max_drawdown: float
    total_trades: int
    winning_trades: int
    losing_trades: int
```

**Technical Notes:**
- TimescaleDB time_bucket für Aggregationen
- Caching für häufig abgefragte Metriken (Redis)
- Berechnung on-demand, nicht pre-computed (MVP)

**Prerequisites:** Story 4.5, 5.1

---

## Story 6.2: Performance-Historie und Aggregationen

Als Operator,
möchte ich historische Performance-Daten,
damit ich Trends über Zeit analysieren kann.

**Acceptance Criteria:**

**Given** Analytics-Service
**When** ich Historie-Tracking implementiere
**Then** existiert `src/db/models/performance_metrics.py`:
```python
class PerformanceMetric(Base):
    __tablename__ = "performance_metrics"

    id: Mapped[int] = mapped_column(primary_key=True)
    team_instance_id: Mapped[int] = mapped_column(ForeignKey("team_instances.id"))
    timestamp: Mapped[datetime]
    period: Mapped[str]  # hourly, daily, weekly
    pnl: Mapped[Decimal]
    pnl_percent: Mapped[float]
    win_rate: Mapped[float]
    sharpe_ratio: Mapped[float | None]
    max_drawdown: Mapped[float]
    trade_count: Mapped[int]
```

**And** TimescaleDB Hypertable mit automatischer Retention:
  - Hourly: 7 Tage
  - Daily: 1 Jahr
  - Weekly: Unbegrenzt

**And** Scheduled Job aggregiert Daten:
```python
async def aggregate_performance():
    """Läuft stündlich, erstellt Aggregationen"""
```

**Technical Notes:**
- TimescaleDB Continuous Aggregates für Effizienz
- Retention Policy in Migration definieren
- Job via APScheduler oder Celery-Beat

**Prerequisites:** Story 6.1

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

**Epic 6 Complete**

**Stories Created:** 4
**FR Coverage:** FR29, FR30, FR31, FR32, FR33, FR34, FR35
**Technical Context Used:** Architecture Data Architecture, TimescaleDB

---
