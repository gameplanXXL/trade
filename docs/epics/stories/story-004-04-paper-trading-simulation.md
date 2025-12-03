---
epic: 004
story: 04
title: "Paper-Trading-Simulation"
status: done
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

- [x] PaperPosition Model
- [x] PaperTradingEngine Klasse
- [x] Simulated Order Execution mit Budget-Check
- [x] Spread-Berechnung bei Entry
- [x] Position-Update Loop
- [x] Trailing SL Update bei Preisbewegung
- [x] Stop Loss / Take Profit Auto-Close
- [x] get_equity Berechnung
- [x] Unit Tests (25 Tests)

**Technical Notes:**
- Simuliert realistische Execution mit Spread
- P/L = (exit - entry) * volume * 100000 (Forex)
- Position-Updates alle 5 Sekunden (konfigurierbar)
- DB-Persistenz vorbereitet für Story 4.5

**Prerequisites:** Story 4.2, 4.3

---

## Dev Agent Record

### Implementation Notes (2025-12-03)
- PaperTradingEngine mit vollständiger Trading-Simulation
- Budget-Validierung vor Order-Ausführung
- Spread-Kosten werden bei Entry berechnet und vom P/L abgezogen
- Trailing SL folgt nur in Gewinnrichtung
- Auto-Close bei SL/TP Hit
- JPY-Pairs mit korrekter Pip-Berechnung (0.01 vs 0.0001)

### File List
- `backend/src/services/__init__.py` (neu)
- `backend/src/services/paper_trading.py` (neu)
- `backend/tests/services/__init__.py` (neu)
- `backend/tests/services/test_paper_trading.py` (neu)

### Test Results
- 25 neue Tests für PaperTradingEngine
- Alle 364 Backend-Tests bestanden
