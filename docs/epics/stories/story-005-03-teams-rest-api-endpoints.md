---
epic: 005
story: 03
title: "Teams REST-API Endpoints"
status: completed
story_points: 3
covers: [FR6, FR7, FR8, FR9]
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

