---
epic: 005
story: 01
title: "TeamInstance Database Model"
status: backlog
story_points: 2
covers: [FR6, FR7, FR8, FR10, FR11]
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

