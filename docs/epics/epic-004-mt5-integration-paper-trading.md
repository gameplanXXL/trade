# Epic 4: MT5-Integration & Paper Trading ✅ COMPLETED

**Epic Goal:** User kann sich mit MT5 verbinden, Kursdaten empfangen und simulierte Trades im Paper-Modus ausführen

**Status:** 5/5 Stories done (100%)

---

## Story 4.1: MT5-Connector mit Auto-Reconnect

Als Operator,
möchte ich eine stabile MT5-Verbindung,
damit das System Kursdaten empfangen und Orders senden kann.

**Acceptance Criteria:**

**Given** MT5 läuft unter Wine auf dem VServer
**When** ich den Connector implementiere
**Then** existiert `src/mt5/connector.py`:
```python
from aiomql import MetaTrader

class MT5Connector:
    def __init__(self, settings: MT5Settings):
        self.settings = settings
        self._connected = False
        self._mt5: MetaTrader | None = None

    async def connect(self) -> bool:
        """Verbindet mit MT5, gibt True bei Erfolg zurück"""

    async def disconnect(self) -> None:
        """Trennt Verbindung sauber"""

    async def reconnect(self, max_attempts: int = 3) -> bool:
        """Auto-Reconnect mit exponential backoff"""

    @property
    def is_connected(self) -> bool:
        """Prüft Verbindungsstatus"""

    async def get_account_info(self) -> AccountInfo:
        """Holt Konto-Informationen"""
```

**And** Auto-Reconnect bei Verbindungsabbruch (3 Versuche, exponential backoff)
**And** Connection-Status wird geloggt
**And** `MT5ConnectionError` bei dauerhaftem Fehler

**Technical Notes:**
- aiomql für async MT5-Zugriff
- Wine-Kompatibilität bereits dokumentiert
- Health-Check prüft Verbindung alle 30s

**Prerequisites:** Story 1.1

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

**Technical Notes:**
- MT5 Magic Number für Order-Identifikation
- Trailing SL als Broker-Feature (wenn verfügbar) oder manuell
- Slippage-Toleranz konfigurierbar

**Prerequisites:** Story 4.1

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

**Technical Notes:**
- Simuliert realistische Execution (kein Perfect Fill)
- Spread aus Market Data
- Position-Updates alle 5 Sekunden

**Prerequisites:** Story 4.2, 4.3

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

---

**Epic 4 Complete**

**Stories Created:** 5
**FR Coverage:** FR23, FR24, FR25, FR26, FR27, FR28, FR52
**Technical Context Used:** Architecture Section MT5 Integration, Data Architecture

---
