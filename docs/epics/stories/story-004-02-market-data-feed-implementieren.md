---
epic: 004
story: 02
title: "Market-Data-Feed implementieren"
status: backlog
story_points: 3
covers: [FR24]
---

## Story 4.2: Market-Data-Feed implementieren

Als Operator,
möchte ich Echtzeit-Kursdaten von MT5,
damit Agenten aktuelle Marktdaten für Entscheidungen haben.

**Acceptance Criteria:**

**Given** MT5-Connector
**When** ich den Market-Data-Feed implementiere
**Then** existiert `src/mt5/market_data.py`:
```python
class MarketDataFeed:
    def __init__(self, connector: MT5Connector, symbols: list[str]):
        self.connector = connector
        self.symbols = symbols

    async def get_current_price(self, symbol: str) -> Price:
        """Holt aktuellen Bid/Ask für Symbol"""

    async def get_ohlcv(self, symbol: str, timeframe: str, count: int) -> list[OHLCV]:
        """Holt historische Kerzen"""

    async def subscribe(self, callback: Callable) -> None:
        """Startet Tick-Subscription für alle Symbole"""

    async def unsubscribe(self) -> None:
        """Stoppt Subscription"""
```

**And** Symbol-Normalisierung: `EUR/USD` → `EURUSD` (MT5-Format)
**And** Preise werden in `market_data` Hypertable gespeichert
**And** WebSocket-Push bei neuen Ticks (Epic 7)

**Technical Notes:**
- Kanonische Symbole in DB: `EUR/USD`
- MT5-Symbole: `EURUSD` (ohne Slash)
- TimescaleDB für Zeitreihen-Speicherung

**Prerequisites:** Story 4.1, 1.3

