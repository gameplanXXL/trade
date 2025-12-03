---
epic: 004
story: 01
title: "MT5-Connector mit Auto-Reconnect"
status: backlog
story_points: 5
covers: [FR23, FR52]
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



## Tasks

- [ ] aiomql Integration
- [ ] Connection Management
- [ ] Auto-Reconnect mit Backoff
- [ ] Health Check implementieren
- [ ] Error Handling (MT5ConnectionError)
**Technical Notes:**
- aiomql für async MT5-Zugriff
- Wine-Kompatibilität bereits dokumentiert
- Health-Check prüft Verbindung alle 30s

**Prerequisites:** Story 1.1

