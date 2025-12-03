---
epic: 002
story: 06
title: "Trader Agent implementieren"
status: backlog
story_points: 3
covers: [FR14, FR16]
---

## Story 2.6: Trader Agent implementieren

Als Entwickler,
möchte ich einen Trader-Agenten,
damit das System Orders vorbereiten und ausführen kann.

**Acceptance Criteria:**

**Given** BaseAgent
**When** ich Trader implementiere
**Then** existiert `src/agents/trader.py`:
```python
class TraderMode(str, Enum):
    ACTIVE = "active"
    HOLD = "hold"

class Trader(BaseAgent):
    name = "trader"
    mode: TraderMode = TraderMode.ACTIVE

    def _configure(self, params: dict) -> None:
        self.position_sizing = params.get("position_sizing", "conservative")
        self.max_positions = params.get("max_positions", 3)
        self.trailing_stop_pct = params.get("trailing_stop_pct", 2.0)

    async def prepare_order(self, context: dict) -> AgentDecision:
        """Bereitet Order basierend auf Signal vor"""

    async def execute(self, context: dict) -> AgentDecision:
        """Führt Order aus (Paper oder Live)"""

    async def close_all_positions(self) -> AgentDecision:
        """Emergency: Schließt alle offenen Positionen"""

    def set_mode(self, mode: TraderMode) -> None:
        """Wechselt Trading-Modus (ACTIVE/HOLD)"""
```

**And** Position-Sizing-Strategien:
  - `conservative`: 1% des Budgets pro Trade
  - `moderate`: 2% des Budgets
  - `aggressive`: 5% des Budgets

**And** Trailing Stoploss wird automatisch gesetzt

**Technical Notes:**
- Order-Objekt enthält: symbol, side, size, entry, stop_loss
- HOLD-Mode blockt neue Orders, erlaubt Close
- Integration mit MT5 in Epic 4

**Prerequisites:** Story 2.3

