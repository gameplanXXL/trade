---
epic: 005
story: 04
title: "Team-Lifecycle-Manager"
status: backlog
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

- [ ] Team-Start Logik
- [ ] Team-Pause/Resume
- [ ] Team-Stop mit Position-Closing
- [ ] Restart Recovery
- [ ] Graceful Shutdown
**Technical Notes:**
- Orchestrators werden im Memory gehalten
- Bei Restart: Alle ACTIVE Teams automatisch starten
- Graceful Shutdown bei Server-Stop

**Prerequisites:** Story 3.5, 5.3

