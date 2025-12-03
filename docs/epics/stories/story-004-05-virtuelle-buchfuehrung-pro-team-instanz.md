---
epic: 004
story: 05
title: "Virtuelle Buchführung pro Team-Instanz"
status: done
story_points: 3
covers: [FR28]
---

## Story 4.5: Virtuelle Buchführung pro Team-Instanz

Als Operator,
möchte ich eine virtuelle Buchführung pro Team-Instanz,
damit Budget und P/L korrekt getrackt werden.

**Acceptance Criteria:**

**Given** Paper-Trading-Engine
**When** ich die Buchführung implementiere
**Then** trackt jede Team-Instanz:
```python
# In db/models/team.py
class TeamInstance(Base):
    # ...
    initial_budget: Mapped[Decimal]
    current_budget: Mapped[Decimal]
    realized_pnl: Mapped[Decimal] = mapped_column(default=0)
    unrealized_pnl: Mapped[Decimal] = mapped_column(default=0)
```

**And** Budget-Updates bei:
  - Trade-Open: current_budget -= position_size
  - Trade-Close: current_budget += position_size + pnl
  - Position-Update: unrealized_pnl wird aktualisiert

**And** Trade-Tabelle speichert jeden Trade:
```python
class Trade(Base):
    __tablename__ = "trades"

    id: Mapped[int] = mapped_column(primary_key=True)
    team_instance_id: Mapped[int] = mapped_column(ForeignKey("team_instances.id"))
    symbol: Mapped[str]  # Kanonisch: EUR/USD
    side: Mapped[str]  # BUY, SELL
    size: Mapped[Decimal]
    entry_price: Mapped[Decimal]
    exit_price: Mapped[Decimal | None]
    pnl: Mapped[Decimal | None]
    status: Mapped[str]  # open, closed
    opened_at: Mapped[datetime]
    closed_at: Mapped[datetime | None]
```

## Tasks

- [x] TeamInstance Model erweitern (Budget-Felder)
- [x] Trade Model implementieren
- [x] BudgetManager Service erstellen
- [x] allocate_budget (Trade-Open)
- [x] release_budget (Trade-Close mit P/L)
- [x] update_unrealized_pnl
- [x] record_trade_open / record_trade_close
- [x] get_budget_summary
- [x] Unit Tests (18 Tests)

**Technical Notes:**
- Decimal (Numeric) für alle Geldbeträge (keine Float-Rundungsfehler)
- Trade-Status: open → closed
- Hypertable für trades vorbereitet (TimescaleDB)
- Relationships zwischen TeamInstance und Trade

**Prerequisites:** Story 4.4, 1.3

---

## Dev Agent Record

### Implementation Notes (2025-12-03)
- TeamInstance mit initial_budget, current_budget, realized_pnl, unrealized_pnl
- Trade Model mit vollständigen Feldern für Tracking
- BudgetManager als zentrale Service-Klasse für Budget-Operationen
- Budget-Allokation bei Trade-Open, Release bei Trade-Close
- get_budget_summary mit total_equity und total_return_pct
- Relationships für einfachen Zugriff auf Trades/Decisions

### File List
- `backend/src/db/models.py` (erweitert: TeamInstance, Trade)
- `backend/src/services/budget_manager.py` (neu)
- `backend/src/services/__init__.py` (erweitert)
- `backend/tests/services/test_budget_manager.py` (neu)

### Test Results
- 18 neue Tests für BudgetManager
- Alle 382 Backend-Tests bestanden
