---
epic: 004
story: 04
title: "Paper-Trading-Simulation"
status: backlog
story_points: 5
covers: [FR27]
---

## Story 4.4: Paper-Trading-Simulation

Als Operator,
möchte ich einen Paper-Trading-Modus,
damit ich Strategien ohne echtes Geld testen kann.

**Acceptance Criteria:**

**Given** Order-Management und Market-Data
**When** ich Paper-Trading implementiere
**Then** existiert `src/services/paper_trading.py`:
```python
class PaperTradingEngine:
    def __init__(self, market_data: MarketDataFeed):
        self.market_data = market_data
        self.positions: dict[int, PaperPosition] = {}
        self._ticket_counter = 0

    async def execute_order(self, order: OrderRequest, budget: Decimal) -> OrderResult:
        """
        Simuliert Order-Ausführung:
        - Prüft Budget
        - Erstellt virtuelle Position
        - Setzt virtuellen Trailing SL
        """

    async def update_positions(self) -> list[PositionUpdate]:
        """
        Aktualisiert alle Positionen mit aktuellen Preisen.
        Schließt Positionen wenn SL erreicht.
        """

    async def close_position(self, ticket: int) -> OrderResult:
        """Schließt virtuelle Position"""

    def get_equity(self, current_prices: dict) -> Decimal:
        """Berechnet aktuelles Equity"""
```

**And** Paper-Positionen werden in DB gespeichert (für Persistenz bei Restart)
**And** P/L-Berechnung berücksichtigt Spread
**And** Trailing SL wird bei Preis-Updates geprüft



## Tasks

- [ ] PaperPosition Model
- [ ] Simulated Execution
- [ ] Position-Update Loop
- [ ] Spread-Berechnung
- [ ] Persistenz in DB
**Technical Notes:**
- Simuliert realistische Execution (kein Perfect Fill)
- Spread aus Market Data
- Position-Updates alle 5 Sekunden

**Prerequisites:** Story 4.2, 4.3

