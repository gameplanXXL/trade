# Epic 3: Pipeline-Execution & Override-Engine

**Epic Goal:** User kann eine Team-Pipeline starten und sieht, wie Agenten sequenziell arbeiten; Override-Regeln greifen bei kritischen Situationen

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

**Technical Notes:**
- Async für non-blocking LLM-Calls
- Context accumulates alle Decisions
- Performance-Target: < 1s für Pipeline (ohne LLM)

**Prerequisites:** Story 2.2, 2.8

---

## Story 3.2: Override-Rule-Engine implementieren

Als Entwickler,
möchte ich eine Override-Rule-Engine,
damit kritische Situationen die normale Pipeline überschreiben.

**Acceptance Criteria:**

**Given** der Pipeline-Executor
**When** ich die Override-Engine implementiere
**Then** existiert `src/teams/override.py`:
```python
class OverrideEngine:
    def __init__(self, rules: list[OverrideRule], agents: dict[str, BaseAgent]):
        self.rules = sorted(rules, key=lambda r: r.priority)
        self.agents = agents

    def evaluate_condition(self, condition: str, context: dict) -> bool:
        """
        Evaluiert Bedingung gegen aktuellen Kontext.
        Beispiel: "crash_detector.status == CRASH"
        """

    async def check_and_execute(self, context: dict) -> OverrideResult | None:
        """
        Prüft alle Regeln in Prioritäts-Reihenfolge.
        Führt erste zutreffende Regel aus und gibt Result zurück.
        None wenn keine Regel zutrifft.
        """

    async def execute_action(self, action: str, context: dict) -> AgentDecision:
        """
        Führt Override-Action aus.
        Beispiel: "trader.close_all_positions()"
        """
```

**And** Regeln werden nach Priorität sortiert (niedrig = höher)
**And** Nur erste zutreffende Regel wird ausgeführt
**And** Override-Execution wird geloggt mit Regel-Name

**Technical Notes:**
- Condition-Evaluation: Einfaches String-Parsing, keine eval()
- Supported Conditions: `agent.status == VALUE`, `agent.field > VALUE`
- Action-Parsing: `agent.method()` oder `agent.method(arg)`

**Prerequisites:** Story 3.1

---

## Story 3.3: Agent-Status-Management (NORMAL/WARNING/CRASH)

Als Entwickler,
möchte ich ein einheitliches Status-Management für Agenten,
damit Override-Regeln auf Status reagieren können.

**Acceptance Criteria:**

**Given** BaseAgent mit Status
**When** ich Status-Management implementiere
**Then** haben alle Agenten:
```python
class BaseAgent:
    status: AgentStatus = AgentStatus.NORMAL

    def set_status(self, status: AgentStatus) -> None:
        old_status = self.status
        self.status = status
        if old_status != status:
            log.warning("agent_status_changed",
                        agent=self.name,
                        old_status=old_status,
                        new_status=status)
```

**And** CrashDetector setzt Status basierend auf Analyse:
  - NORMAL: crash_probability < 0.5
  - WARNING: 0.5 <= crash_probability < threshold
  - CRASH: crash_probability >= threshold

**And** Status-Änderungen triggern WebSocket-Events (Epic 7)

**Technical Notes:**
- Status ist Agent-Attribut, nicht global
- Mehrere Agenten können WARNING haben
- CRASH von einem Agent kann Team pausieren

**Prerequisites:** Story 2.3, 2.4

---

## Story 3.4: Decision-Audit-Log implementieren

Als Entwickler,
möchte ich ein Audit-Log für alle Agent-Entscheidungen,
damit ich nachvollziehen kann, was das System entschieden hat.

**Acceptance Criteria:**

**Given** Pipeline-Executor
**When** ich das Audit-Log implementiere
**Then** existiert `src/db/models/agent_decision.py`:
```python
class AgentDecisionLog(Base):
    __tablename__ = "agent_decisions"

    id: Mapped[int] = mapped_column(primary_key=True)
    team_instance_id: Mapped[int] = mapped_column(ForeignKey("team_instances.id"))
    agent_name: Mapped[str] = mapped_column(String(50))
    decision_type: Mapped[str] = mapped_column(String(20))  # signal, warning, rejection, override
    data: Mapped[dict] = mapped_column(JSON)
    confidence: Mapped[float | None]
    created_at: Mapped[datetime] = mapped_column(default=func.now())
```

**And** Pipeline-Executor speichert jede Decision
**And** Override-Executions werden als `decision_type="override"` geloggt

**Technical Notes:**
- TimescaleDB Hypertable für schnelle Time-Queries
- Retention: 90 Tage (konfigurierbar)
- Index auf `team_instance_id`, `created_at`

**Prerequisites:** Story 1.3, 3.1

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

**Technical Notes:**
- LangGraph für State-Management
- Conditional Edges basierend auf Agent-Status
- END-Node bei Override oder Pipeline-Completion

**Prerequisites:** Story 3.1, 3.2

---

**Epic 3 Complete**

**Stories Created:** 5
**FR Coverage:** FR17, FR18, FR19, FR20, FR21, FR22
**Technical Context Used:** Architecture Section 3 (Teams), LangGraph Integration

---
