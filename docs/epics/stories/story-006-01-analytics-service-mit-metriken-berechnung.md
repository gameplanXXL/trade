---
epic: 006
story: 01
title: "Analytics-Service mit Metriken-Berechnung"
status: backlog
story_points: 5
covers: [FR29, FR30, FR31, FR32, FR33]
---

## Story 6.1: Analytics-Service mit Metriken-Berechnung

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



## Tasks

- [ ] P/L Berechnung
- [ ] Win-Rate Berechnung
- [ ] Sharpe Ratio Implementierung
- [ ] Max Drawdown Berechnung
- [ ] Caching mit Redis
**Technical Notes:**
- TimescaleDB time_bucket für Aggregationen
- Caching für häufig abgefragte Metriken (Redis)
- Berechnung on-demand, nicht pre-computed (MVP)

**Prerequisites:** Story 4.5, 5.1

