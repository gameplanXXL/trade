# Epic 5: Team-Instanz-Management

**Epic Goal:** User kann Team-Instanzen erstellen, starten, stoppen und pausieren; Instanzen werden persistent gespeichert

---

## Story 5.1: TeamInstance Database Model

Als Entwickler,
möchte ich ein vollständiges TeamInstance-Model,
damit Team-Instanzen persistent gespeichert werden.

**Acceptance Criteria:**

**Given** die Datenbank-Infrastruktur
**When** ich das Model implementiere
**Then** existiert `src/db/models/team.py`:
```python
class TeamInstanceStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"

class TeamInstanceMode(str, Enum):
    PAPER = "paper"
    LIVE = "live"

class TeamInstance(Base):
    __tablename__ = "team_instances"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    template_name: Mapped[str] = mapped_column(String(100))
    status: Mapped[TeamInstanceStatus]
    mode: Mapped[TeamInstanceMode]
    symbols: Mapped[list[str]] = mapped_column(JSON)
    initial_budget: Mapped[Decimal]
    current_budget: Mapped[Decimal]
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(onupdate=func.now())

    # Relationships
    trades: Mapped[list["Trade"]] = relationship(back_populates="team_instance")
    decisions: Mapped[list["AgentDecisionLog"]] = relationship(back_populates="team_instance")
```

**And** Alembic-Migration erstellt die Tabelle
**And** Indizes auf `status`, `created_at`

**Technical Notes:**
- JSON für symbols Array
- Decimal mit precision=18, scale=8
- Soft-Delete nicht implementiert (STOPPED = final)

**Prerequisites:** Story 1.3

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

---

## Story 5.3: Teams REST-API Endpoints

Als Operator,
möchte ich REST-Endpoints für Team-Management,
damit ich Instanzen über HTTP verwalten kann.

**Acceptance Criteria:**

**Given** Team-Repository
**When** ich die API implementiere
**Then** existiert `src/api/routes/teams.py`:
```python
router = APIRouter(prefix="/api/teams", tags=["teams"])

@router.post("/", response_model=TeamResponse)
async def create_team(data: TeamCreate, repo: TeamRepository = Depends(get_repo)):
    """Erstellt neue Team-Instanz"""

@router.get("/", response_model=list[TeamResponse])
async def list_teams(status: str | None = None, repo: ...):
    """Listet alle Team-Instanzen"""

@router.get("/{team_id}", response_model=TeamDetailResponse)
async def get_team(team_id: int, repo: ...):
    """Holt Team-Details"""

@router.patch("/{team_id}/start", response_model=TeamResponse)
async def start_team(team_id: int, repo: ...):
    """Startet Team-Instanz"""

@router.patch("/{team_id}/pause", response_model=TeamResponse)
async def pause_team(team_id: int, repo: ...):
    """Pausiert Team-Instanz"""

@router.delete("/{team_id}")
async def stop_team(team_id: int, repo: ...):
    """Stoppt Team-Instanz permanent"""
```

**And** Request/Response Models in `src/api/schemas/team.py`:
```python
class TeamCreate(BaseModel):
    name: str
    template_name: str
    symbols: list[str]
    budget: Decimal
    mode: TeamInstanceMode = TeamInstanceMode.PAPER

class TeamResponse(BaseModel):
    id: int
    name: str
    status: TeamInstanceStatus
    mode: TeamInstanceMode
    current_budget: Decimal
    # ...
```

**And** Standard-Fehler-Format bei 404, 400

**Technical Notes:**
- Dependency Injection für Repository
- Pagination für list_teams (später)
- Response-Format gemäß Architecture

**Prerequisites:** Story 5.2

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

**Technical Notes:**
- Orchestrators werden im Memory gehalten
- Bei Restart: Alle ACTIVE Teams automatisch starten
- Graceful Shutdown bei Server-Stop

**Prerequisites:** Story 3.5, 5.3

---

**Epic 5 Complete**

**Stories Created:** 4
**FR Coverage:** FR6, FR7, FR8, FR9, FR10, FR11
**Technical Context Used:** Architecture Section 5 (Project Structure), API Design

---
