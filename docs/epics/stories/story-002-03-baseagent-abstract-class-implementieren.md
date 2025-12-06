---
epic: 002
story: 03
title: "BaseAgent Abstract Class implementieren"
status: completed
story_points: 3
covers: [FR16]
---

## Story 2.3: BaseAgent Abstract Class implementieren

Als Entwickler,
möchte ich eine abstrakte Basis-Klasse für alle Agenten,
damit alle Agent-Rollen ein einheitliches Interface haben.

**Acceptance Criteria:**

**Given** das Backend-Projekt
**When** ich BaseAgent implementiere
**Then** existiert `src/agents/base.py`:
```python
from abc import ABC, abstractmethod
from enum import Enum

class AgentStatus(str, Enum):
    NORMAL = "normal"
    WARNING = "warning"
    CRASH = "crash"

class AgentDecision(BaseModel):
    agent_name: str
    decision_type: str  # signal, warning, rejection, action
    data: dict[str, Any]
    timestamp: datetime
    confidence: float | None = None

class BaseAgent(ABC):
    name: str
    status: AgentStatus = AgentStatus.NORMAL

    def __init__(self, params: dict[str, Any]):
        self.params = params
        self._configure(params)

    @abstractmethod
    def _configure(self, params: dict[str, Any]) -> None:
        """Agent-spezifische Konfiguration"""

    @abstractmethod
    async def execute(self, context: dict) -> AgentDecision:
        """Führt Agent-Logik aus"""

    def to_dict(self) -> dict:
        """Serialisiert Agent-Status für Logging/API"""
```

**And** `AgentDecision` wird für alle Agent-Outputs verwendet
**And** Status-Änderungen werden geloggt

**Technical Notes:**
- Async-native für LLM-Calls
- Context-Dict enthält Market-Data, Previous Decisions
- Logging via structlog

**Prerequisites:** Story 1.2

