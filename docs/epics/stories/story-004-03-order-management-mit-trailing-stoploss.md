---
epic: 004
story: 03
title: "Order-Management mit Trailing Stoploss"
status: backlog
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

- [ ] OrderRequest/OrderResult Models
- [ ] Place Order Logik
- [ ] Trailing Stoploss Implementierung
- [ ] Position Management
- [ ] Order-Logging in DB
**Technical Notes:**
- MT5 Magic Number für Order-Identifikation
- Trailing SL als Broker-Feature (wenn verfügbar) oder manuell
- Slippage-Toleranz konfigurierbar

**Prerequisites:** Story 4.1

