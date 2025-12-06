---
epic: 003
story: 05
title: "Team-Orchestrator mit LangGraph"
status: completed
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

- [x] Task 1: StateGraph-Definition
- [x] Task 2: Node-Funktionen implementieren
- [x] Task 3: Conditional Edges konfigurieren
- [x] Task 4: Integration mit Pipeline/Override
- [x] Task 5: Graph-Visualisierung

## Technical Notes
- LangGraph für State-Management
- Conditional Edges basierend auf Agent-Status
- END-Node bei Override oder Pipeline-Completion

## Prerequisites
Story 3.1, 3.2

## Dev Agent Record

### Debug Log
- 2025-12-03: Tests zuerst geschrieben (RED phase), dann Implementierung (GREEN phase)
- 2025-12-03: langgraph>=0.2 zu pyproject.toml hinzugefügt
- 2025-12-03: Trader.close_all_positions() angepasst für context-Parameter

### Implementation Plan
1. OrchestratorState TypedDict mit market_data, decisions, current_status
2. TeamOrchestrator Klasse mit agents, pipeline, override_engine, graph
3. _build_graph() mit check_override und run_pipeline Nodes
4. Conditional Edges: override_triggered -> END, sonst -> run_pipeline
5. run_cycle() für komplette Trading-Zyklus-Ausführung
6. get_graph_visualization() für Mermaid-Diagramme

### Completion Notes
- OrchestratorState TypedDict implementiert
- TeamOrchestrator mit allen AC-Anforderungen:
  - Creates agents from template
  - Creates PipelineExecutor
  - Creates OverrideEngine
  - Builds LangGraph StateGraph
- Graph mit check_override und run_pipeline Nodes
- Conditional Edges basierend auf override_triggered
- run_cycle() führt Override-Check, Pipeline-Execution aus
- get_current_state() und get_graph_visualization() implementiert
- 13 Unit Tests geschrieben und bestanden
- Alle 263 Tests bestanden (keine Regressionen)
- Linter (ruff) bestanden

## File List
- backend/src/teams/orchestrator.py (neu)
- backend/tests/teams/test_orchestrator.py (neu)
- backend/src/agents/trader.py (modifiziert - close_all_positions context param)
- backend/pyproject.toml (modifiziert - langgraph dependency)

## Change Log
- 2025-12-03: Story implementiert - TeamOrchestrator mit LangGraph StateGraph
