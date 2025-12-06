---
epic: 002
story: 01
title: "Team-YAML-Schema und Pydantic Models definieren"
status: completed
story_points: 3
covers: [FR1, FR2, FR3, FR4]
---

## Story 2.1: Team-YAML-Schema und Pydantic Models definieren

Als Entwickler,
möchte ich Pydantic Models für Team-Konfigurationen,
damit YAML-Templates typsicher validiert werden können.

**Acceptance Criteria:**

**Given** das Backend-Projekt
**When** ich die Team-Schemas implementiere
**Then** existiert `src/teams/schemas.py` mit:
```python
from pydantic import BaseModel
from enum import Enum

class AgentType(str, Enum):
    CRASH_DETECTOR = "crash_detector"
    LLM_ANALYST = "llm_analyst"
    TRADER = "trader"
    RISK_MANAGER = "risk_manager"

class AgentConfig(BaseModel):
    class_name: str
    params: dict[str, Any]

class PipelineStep(BaseModel):
    agent: str
    method: str

class OverrideRule(BaseModel):
    name: str
    condition: str
    action: str
    priority: int = 10

class TeamTemplate(BaseModel):
    name: str
    version: str
    roles: dict[str, AgentConfig]
    pipeline: list[PipelineStep]
    override_rules: list[OverrideRule] = []
```

**And** Validation-Errors geben klare Fehlermeldungen

**Technical Notes:**
- Pydantic v2 mit `model_validator` für Cross-Field-Validation
- Pipeline-Schritte referenzieren definierte Rollen
- Override-Conditions als String (später evaluiert)

**Prerequisites:** Story 1.1

