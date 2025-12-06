---
epic: 005
story: 04
title: "Team-Lifecycle-Manager"
status: done
story_points: 5
covers: [FR9]
---

## Story 5.4: Team-Lifecycle-Manager

Als Entwickler,
möchte ich einen Lifecycle-Manager für Teams,
damit Start/Stop/Pause korrekt orchestriert werden.

**Acceptance Criteria:**

**Given** Team-Repository und Orchestrator
**When** ich den Lifecycle-Manager implementiere
**Then** existiert `src/services/team_lifecycle.py`:
```python
class TeamLifecycleManager:
    def __init__(self, repo: TeamRepository, orchestrators: dict[int, TeamOrchestrator]):
        self.repo = repo
        self.orchestrators = orchestrators

    async def start_team(self, team_id: int) -> TeamInstance:
        """
        Startet Team-Instanz:
        1. Lädt Template
        2. Erstellt Orchestrator
        3. Startet Trading-Loop
        4. Aktualisiert Status auf ACTIVE
        """

    async def pause_team(self, team_id: int) -> TeamInstance:
        """
        Pausiert Team:
        1. Stoppt Trading-Loop
        2. Behält Positionen offen
        3. Aktualisiert Status auf PAUSED
        """

    async def stop_team(self, team_id: int) -> TeamInstance:
        """
        Stoppt Team permanent:
        1. Schließt alle Positionen
        2. Stoppt Orchestrator
        3. Aktualisiert Status auf STOPPED
        """

    async def get_running_teams(self) -> list[int]:
        """Gibt IDs aller laufenden Teams zurück"""
```

**And** Start validiert:
  - Template existiert
  - Budget > 0
  - Symbols sind gültig

**And** Stop schließt automatisch alle Positionen



## Tasks

- [x] Team-Start Logik
- [x] Team-Pause/Resume
- [x] Team-Stop mit Position-Closing
- [x] Restart Recovery
- [x] Graceful Shutdown
**Technical Notes:**
- Orchestrators werden im Memory gehalten
- Bei Restart: Alle ACTIVE Teams automatisch starten
- Graceful Shutdown bei Server-Stop

**Prerequisites:** Story 3.5, 5.3

---

## Implementation Notes (2025-12-06)

**Story vollständig umgesetzt:**

- ✅ `src/services/team_lifecycle.py` mit TeamLifecycleManager:
  - `start_team()`: Lädt Template, erstellt Orchestrator, startet Trading-Loop
  - `pause_team()`: Stoppt Trading-Loop, behält Orchestrator im Memory
  - `resume_team()`: Nutzt existierenden Orchestrator oder erstellt neuen
  - `stop_team()`: Schließt Positionen, entfernt Orchestrator
  - `get_running_teams()`: Gibt IDs aller aktiven Teams zurück
  - `get_orchestrator()`: Zugriff auf Orchestrator eines Teams
- ✅ In-Memory-Tracking: `_orchestrators` und `_tasks` Dictionaries
- ✅ Start-Validierung:
  - Template existiert und ist valide
  - Budget > 0
  - Symbols im kanonischen Format (XXX/YYY)
- ✅ `startup()`: Auto-Start aller zuvor aktiven Teams bei App-Start
- ✅ `shutdown()`: Graceful Shutdown mit Position-Closing
- ✅ `_close_all_positions()`: Schließt alle offenen Trades beim Stoppen
- ✅ `_trading_loop()`: Asynchroner Trading-Loop mit konfigurierbarem Intervall
- ✅ Strukturiertes Logging für alle Operationen
