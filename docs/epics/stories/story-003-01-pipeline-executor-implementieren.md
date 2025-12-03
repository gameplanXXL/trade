---
epic: 003
story: 01
title: "Pipeline-Executor implementieren"
status: backlog
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

- [ ] PipelineContext Model erstellen
- [ ] Step-Execution Logik
- [ ] Context-Propagation zwischen Steps
- [ ] Error Handling und Logging
- [ ] Integration Tests schreiben
**Technical Notes:**
- Async für non-blocking LLM-Calls
- Context accumulates alle Decisions
- Performance-Target: < 1s für Pipeline (ohne LLM)

**Prerequisites:** Story 2.2, 2.8

