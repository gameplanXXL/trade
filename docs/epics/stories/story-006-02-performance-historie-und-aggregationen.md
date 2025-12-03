---
epic: 006
story: 02
title: "Performance-Historie und Aggregationen"
status: backlog
story_points: 3
covers: [FR34]
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

