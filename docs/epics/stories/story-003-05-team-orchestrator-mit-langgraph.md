---
epic: 003
story: 05
title: "Team-Orchestrator mit LangGraph"
status: backlog
story_points: 5
covers: [FR17]
---

## Story 3.5: Team-Orchestrator mit LangGraph

Als Entwickler,
möchte ich einen LangGraph-basierten Orchestrator,
damit die Agent-Koordination graph-basiert erfolgt.

**Acceptance Criteria:**

**Given** Pipeline und Override-Engine
**When** ich den Orchestrator implementiere
**Then** existiert `src/teams/orchestrator.py`:
```python
from langgraph.graph import StateGraph, END

class TeamOrchestrator:
    def __init__(self, template: TeamTemplate):
        self.template = template
        self.agents = self._create_agents()
        self.pipeline = PipelineExecutor(self.agents)
        self.override_engine = OverrideEngine(template.override_rules, self.agents)
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Baut LangGraph StateGraph aus Pipeline-Definition"""

    async def run_cycle(self, market_data: dict) -> list[AgentDecision]:
        """
        Führt einen Trading-Zyklus aus:
        1. Override-Check
        2. Pipeline-Execution (wenn kein Override)
        3. Audit-Logging
        """
```

**And** Graph-State enthält:
  - Market Data
  - Agent Decisions
  - Current Status (NORMAL/WARNING/CRASH)

**And** Visualisierung des Graphs ist möglich (für Debugging)



## Tasks

- [ ] StateGraph-Definition
- [ ] Node-Funktionen implementieren
- [ ] Conditional Edges konfigurieren
- [ ] Integration mit Pipeline/Override
- [ ] Graph-Visualisierung
**Technical Notes:**
- LangGraph für State-Management
- Conditional Edges basierend auf Agent-Status
- END-Node bei Override oder Pipeline-Completion

**Prerequisites:** Story 3.1, 3.2

