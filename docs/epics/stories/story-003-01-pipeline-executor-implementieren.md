---
epic: 003
story: 01
title: "Pipeline-Executor implementieren"
status: Ready for Review
story_points: 5
covers: [FR17, FR22]
---

## Story 3.1: Pipeline-Executor implementieren

Als Entwickler,
möchte ich einen Pipeline-Executor,
damit Team-Pipelines sequenziell ausgeführt werden.

**Acceptance Criteria:**

**Given** Team-Templates und Agenten
**When** ich den Pipeline-Executor implementiere
**Then** existiert `src/teams/pipeline.py`:
```python
class PipelineContext(BaseModel):
    team_id: int
    symbols: list[str]
    market_data: dict
    decisions: list[AgentDecision] = []
    current_step: int = 0

class PipelineExecutor:
    def __init__(self, agents: dict[str, BaseAgent]):
        self.agents = agents
        self.context = PipelineContext()

    async def execute_step(self, step: PipelineStep) -> AgentDecision:
        """Führt einzelnen Pipeline-Schritt aus"""
        agent = self.agents[step.agent]
        method = getattr(agent, step.method)
        return await method(self.context.model_dump())

    async def run(self, pipeline: list[PipelineStep]) -> list[AgentDecision]:
        """Führt komplette Pipeline aus"""
        for step in pipeline:
            decision = await self.execute_step(step)
            self.context.decisions.append(decision)
            log.info("pipeline_step_completed",
                     step=step.agent,
                     method=step.method,
                     decision=decision.decision_type)
        return self.context.decisions
```

**And** Pipeline stoppt bei kritischen Fehlern
**And** Jeder Schritt wird mit Timestamp geloggt
**And** Context wird zwischen Schritten weitergegeben


## Tasks

- [x] Task 1: PipelineContext Model erstellen
- [x] Task 2: Step-Execution Logik
- [x] Task 3: Context-Propagation zwischen Steps
- [x] Task 4: Error Handling und Logging
- [x] Task 5: Integration Tests schreiben

## Technical Notes
- Async für non-blocking LLM-Calls
- Context accumulates alle Decisions
- Performance-Target: < 1s für Pipeline (ohne LLM)

## Prerequisites
Story 2.2, 2.8

## Dev Agent Record

### Debug Log
- 2025-12-03: Tests zuerst geschrieben (RED phase), dann Implementierung (GREEN phase)

### Implementation Plan
1. PipelineContext Pydantic Model mit team_id, symbols, market_data, decisions, current_step
2. PipelineExecutor mit agents dict, context management
3. execute_step() mit Agent/Method Validation und Error Handling
4. run() für sequentielle Pipeline-Ausführung mit Context-Propagation
5. Umfassende Tests für alle Acceptance Criteria

### Completion Notes
- PipelineContext Model implementiert mit allen Feldern laut AC
- PipelineExecutor implementiert mit execute_step() und run()
- Pipeline stoppt bei kritischen Fehlern (PipelineError)
- Jeder Schritt wird mit Timestamp geloggt (pipeline_step_starting, pipeline_step_completed)
- Context wird zwischen Schritten weitergegeben (decisions accumulate, current_step increments)
- 16 Unit Tests geschrieben und bestanden
- Alle 204 Tests der gesamten Test-Suite bestanden (keine Regressionen)
- Linter (ruff) bestanden

## File List
- backend/src/teams/pipeline.py (neu)
- backend/tests/teams/test_pipeline.py (neu)

## Change Log
- 2025-12-03: Story implementiert - PipelineContext, PipelineExecutor mit Tests
