---
epic: 004
story: 05
title: "Virtuelle Buchführung pro Team-Instanz"
status: backlog
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

**Technical Notes:**
- Decimal für alle Geldbeträge (keine Float-Rundungsfehler)
- Trade-Status: open → closed
- Hypertable für trades (TimescaleDB)

**Prerequisites:** Story 4.4, 1.3

