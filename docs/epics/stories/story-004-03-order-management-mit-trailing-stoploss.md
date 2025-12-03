---
epic: 004
story: 03
title: "Order-Management mit Trailing Stoploss"
status: done
story_points: 5
covers: [FR25, FR26]
---

## Story 4.3: Order-Management mit Trailing Stoploss

Als Operator,
möchte ich Order-Ausführung mit automatischem Trailing Stoploss,
damit jede Position gegen Verluste abgesichert ist.

**Acceptance Criteria:**

**Given** MT5-Connector
**When** ich Order-Management implementiere
**Then** existiert `src/mt5/orders.py`:
```python
class OrderManager:
    def __init__(self, connector: MT5Connector):
        self.connector = connector

    async def place_order(self, order: OrderRequest) -> OrderResult:
        """
        Platziert Order mit automatischem Trailing Stoploss.
        Returns: OrderResult mit ticket_id und status.
        """

    async def modify_order(self, ticket: int, stop_loss: Decimal) -> bool:
        """Modifiziert bestehende Order (für Trailing SL Update)"""

    async def close_position(self, ticket: int) -> OrderResult:
        """Schließt Position"""

    async def close_all_positions(self, symbol: str | None = None) -> list[OrderResult]:
        """Emergency: Schließt alle (oder symbol-spezifische) Positionen"""

    async def get_open_positions(self) -> list[Position]:
        """Listet alle offenen Positionen"""
```

**And** Trailing Stoploss wird automatisch gesetzt:
  - Initial: Entry - (Entry * trailing_stop_pct / 100)
  - Update: Wenn Preis steigt, SL folgt nach

**And** Order-Typen: MARKET_BUY, MARKET_SELL
**And** Alle Orders werden in `trades` Tabelle geloggt



## Tasks

- [x] OrderRequest/OrderResult Models
- [x] OrderSide, OrderType, OrderStatus Enums
- [x] Place Order Logik
- [x] Trailing Stoploss Berechnung
- [x] Trailing Stop Update bei Preisbewegung
- [x] Position Management (modify, close)
- [x] close_all_positions (Emergency)
- [x] Unit Tests (27 Tests)

**Technical Notes:**
- MT5 Magic Number für Order-Identifikation
- Trailing SL manuell implementiert (später Broker-Feature)
- Slippage-Toleranz konfigurierbar

**Prerequisites:** Story 4.1

---

## Dev Agent Record

### Implementation Notes (2025-12-03)
- Vollständiges OrderManager mit Trailing SL
- Trailing SL: BUY = price - (price * pct), SELL = price + (price * pct)
- SL folgt nur in Gewinnrichtung (nie zurück)
- Position Tracking in Memory (DB-Persistenz in Story 4.5)
- P/L Berechnung bei Position Close

### File List
- `backend/src/mt5/orders.py` (neu)
- `backend/src/mt5/__init__.py` (erweitert)
- `backend/tests/mt5/test_orders.py` (neu)

### Test Results
- 27 neue Tests für OrderManager
- Alle 339 Backend-Tests bestanden
