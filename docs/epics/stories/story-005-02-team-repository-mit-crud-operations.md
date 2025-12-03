---
epic: 005
story: 02
title: "Team-Repository mit CRUD-Operations"
status: backlog
story_points: 2
covers: [FR6, FR11]
---

## Story 5.2: Team-Repository mit CRUD-Operations

Als Entwickler,
möchte ich ein Repository für Team-Instanzen,
damit ich CRUD-Operationen sauber kapseln kann.

**Acceptance Criteria:**

**Given** TeamInstance Model
**When** ich das Repository implementiere
**Then** existiert `src/db/repositories/team_repo.py`:
```python
class TeamRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: TeamInstanceCreate) -> TeamInstance:
        """Erstellt neue Team-Instanz"""

    async def get_by_id(self, team_id: int) -> TeamInstance | None:
        """Holt Team-Instanz nach ID"""

    async def get_all(self, status: TeamInstanceStatus | None = None) -> list[TeamInstance]:
        """Listet alle (oder gefilterte) Instanzen"""

    async def update_status(self, team_id: int, status: TeamInstanceStatus) -> TeamInstance:
        """Ändert Status (active/paused/stopped)"""

    async def update_budget(self, team_id: int, new_budget: Decimal) -> TeamInstance:
        """Aktualisiert Budget"""

    async def delete(self, team_id: int) -> bool:
        """Löscht Instanz permanent"""
```

**And** Alle Operationen sind async
**And** Nicht gefundene IDs geben `None` oder `False` zurück

**Technical Notes:**
- SQLAlchemy 2.0 Style
- Session wird per Request injected
- Keine Business-Logik im Repository

**Prerequisites:** Story 5.1

