# Epic 2: Team-System & Agent-Rollen

**Epic Goal:** User kann ein Team-Template laden und die Agent-Rollen sehen, die darin definiert sind

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

---

## Story 2.2: YAML Team-Loader implementieren

Als Entwickler,
möchte ich einen YAML-Loader für Team-Templates,
damit ich Team-Konfigurationen aus Dateien laden kann.

**Acceptance Criteria:**

**Given** die Team-Schemas
**When** ich den Loader implementiere
**Then** existiert `src/teams/loader.py`:
```python
class TeamLoader:
    def load_template(self, path: Path) -> TeamTemplate:
        """Lädt und validiert ein Team-Template aus YAML"""

    def list_templates(self, directory: Path) -> list[str]:
        """Listet alle verfügbaren Templates"""

    def validate_template(self, template: TeamTemplate) -> list[str]:
        """Gibt Liste von Warnings zurück (leere Liste = valid)"""
```

**And** `team_templates/conservative_llm.yaml` existiert als erstes Template:
```yaml
name: "Conservative LLM Team"
version: "1.0"

roles:
  crash_detector:
    class_name: CrashDetector
    params:
      threshold: 0.9
      window_days: 30

  analyst:
    class_name: LLMSignalAnalyst
    params:
      model: "claude-sonnet-4-20250514"
      min_confidence: 0.75

  trader:
    class_name: Trader
    params:
      position_sizing: "conservative"
      max_positions: 2
      trailing_stop_pct: 2.0

  risk_manager:
    class_name: RiskManager
    params:
      max_drawdown: 0.20

pipeline:
  - agent: crash_detector
    method: check
  - agent: analyst
    method: generate_signal
  - agent: trader
    method: prepare_order
  - agent: risk_manager
    method: validate
  - agent: trader
    method: execute

override_rules:
  - name: "Crash Emergency"
    condition: "crash_detector.status == CRASH"
    action: "trader.close_all_positions()"
    priority: 1
```

**And** Invalid YAML gibt `ValidationError` mit Details

**Technical Notes:**
- PyYAML für Parsing
- Pydantic für Validation
- File-Encoding: UTF-8

**Prerequisites:** Story 2.1

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

---

## Story 2.4: CrashDetector Agent implementieren

Als Entwickler,
möchte ich einen CrashDetector-Agenten,
damit das System Crash-Situationen am Markt erkennen kann.

**Acceptance Criteria:**

**Given** BaseAgent
**When** ich CrashDetector implementiere
**Then** existiert `src/agents/crash_detector.py`:
```python
class CrashDetector(BaseAgent):
    name = "crash_detector"

    def _configure(self, params: dict) -> None:
        self.threshold = params.get("threshold", 0.9)
        self.window_days = params.get("window_days", 30)
        self.indicators = params.get("indicators", ["volatility", "rsi"])

    async def check(self, context: dict) -> AgentDecision:
        """
        Prüft Marktdaten auf Crash-Indikatoren.
        Setzt self.status auf NORMAL, WARNING oder CRASH.
        """
```

**And** konfigurierbare Parameter:
  - `threshold`: Schwellenwert für Crash-Erkennung (0.0-1.0)
  - `window_days`: Zeitfenster für Analyse
  - `indicators`: Liste der zu prüfenden Indikatoren

**And** Rückgabe enthält `crash_probability` und `triggered_indicators`

**Technical Notes:**
- MVP: Einfache Volatilitäts-Prüfung
- Post-MVP: Erweiterte Indikatoren (RSI, Moving Averages)
- Status-Mapping: probability > threshold → CRASH, > 0.7 → WARNING

**Prerequisites:** Story 2.3

---

## Story 2.5: LLMSignalAnalyst Agent implementieren

Als Entwickler,
möchte ich einen LLM-basierten Signal-Analysten,
damit das System Trading-Signale via Claude generieren kann.

**Acceptance Criteria:**

**Given** BaseAgent und LangChain
**When** ich LLMSignalAnalyst implementiere
**Then** existiert `src/agents/analyst.py`:
```python
from langchain_anthropic import ChatAnthropic

class LLMSignalAnalyst(BaseAgent):
    name = "analyst"

    def _configure(self, params: dict) -> None:
        self.model = params.get("model", "claude-sonnet-4-20250514")
        self.min_confidence = params.get("min_confidence", 0.7)
        self.lookback = params.get("lookback", 14)

        self.llm = ChatAnthropic(model=self.model)

    async def generate_signal(self, context: dict) -> AgentDecision:
        """
        Analysiert Marktdaten und generiert Trading-Signal.
        Returns: BUY, SELL, oder HOLD mit Confidence-Score.
        """
```

**And** Prompt enthält:
  - Aktuelle Kursdaten
  - Technische Indikatoren
  - CrashDetector-Status
  - Historische Performance

**And** Response wird als JSON geparst mit `action`, `confidence`, `reasoning`

**Technical Notes:**
- LangChain ChatAnthropic Wrapper
- Structured Output via Pydantic
- Timeout: 30 Sekunden
- Retry bei API-Fehlern (3 Versuche)

**Prerequisites:** Story 2.3, Story 1.7 (für API-Key)

---

## Story 2.6: Trader Agent implementieren

Als Entwickler,
möchte ich einen Trader-Agenten,
damit das System Orders vorbereiten und ausführen kann.

**Acceptance Criteria:**

**Given** BaseAgent
**When** ich Trader implementiere
**Then** existiert `src/agents/trader.py`:
```python
class TraderMode(str, Enum):
    ACTIVE = "active"
    HOLD = "hold"

class Trader(BaseAgent):
    name = "trader"
    mode: TraderMode = TraderMode.ACTIVE

    def _configure(self, params: dict) -> None:
        self.position_sizing = params.get("position_sizing", "conservative")
        self.max_positions = params.get("max_positions", 3)
        self.trailing_stop_pct = params.get("trailing_stop_pct", 2.0)

    async def prepare_order(self, context: dict) -> AgentDecision:
        """Bereitet Order basierend auf Signal vor"""

    async def execute(self, context: dict) -> AgentDecision:
        """Führt Order aus (Paper oder Live)"""

    async def close_all_positions(self) -> AgentDecision:
        """Emergency: Schließt alle offenen Positionen"""

    def set_mode(self, mode: TraderMode) -> None:
        """Wechselt Trading-Modus (ACTIVE/HOLD)"""
```

**And** Position-Sizing-Strategien:
  - `conservative`: 1% des Budgets pro Trade
  - `moderate`: 2% des Budgets
  - `aggressive`: 5% des Budgets

**And** Trailing Stoploss wird automatisch gesetzt

**Technical Notes:**
- Order-Objekt enthält: symbol, side, size, entry, stop_loss
- HOLD-Mode blockt neue Orders, erlaubt Close
- Integration mit MT5 in Epic 4

**Prerequisites:** Story 2.3

---

## Story 2.7: RiskManager Agent implementieren

Als Entwickler,
möchte ich einen RiskManager-Agenten,
damit Orders vor Ausführung validiert werden.

**Acceptance Criteria:**

**Given** BaseAgent
**When** ich RiskManager implementiere
**Then** existiert `src/agents/risk_manager.py`:
```python
class RiskDecision(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"
    REDUCE = "reduce"

class RiskManager(BaseAgent):
    name = "risk_manager"

    def _configure(self, params: dict) -> None:
        self.max_drawdown = params.get("max_drawdown", 0.25)
        self.max_exposure = params.get("max_exposure", 0.5)
        self.max_position_size = params.get("max_position_size", 0.1)

    async def validate(self, context: dict) -> AgentDecision:
        """
        Validiert Order gegen Risiko-Regeln.
        Returns: APPROVE, REJECT, oder REDUCE mit Begründung.
        """

    def check_drawdown(self, current_pnl: Decimal, budget: Decimal) -> bool:
        """Prüft ob Drawdown-Limit erreicht"""

    def check_exposure(self, positions: list, new_order: Order) -> bool:
        """Prüft Gesamt-Exposure"""
```

**And** Rejection-Gründe werden geloggt:
  - `MAX_DRAWDOWN_EXCEEDED`
  - `MAX_EXPOSURE_EXCEEDED`
  - `POSITION_SIZE_TOO_LARGE`
  - `CRASH_MODE_ACTIVE`

**Technical Notes:**
- Drawdown = (Peak - Current) / Peak
- Exposure = Summe aller offenen Positionen / Budget
- REDUCE gibt angepasste Position-Size zurück

**Prerequisites:** Story 2.3

---

## Story 2.8: Agent-Factory und Registry

Als Entwickler,
möchte ich eine Factory zum Erstellen von Agenten aus Config,
damit Teams dynamisch aus YAML instanziiert werden können.

**Acceptance Criteria:**

**Given** alle Agent-Implementierungen
**When** ich die Factory implementiere
**Then** existiert `src/agents/__init__.py`:
```python
AGENT_REGISTRY = {
    "CrashDetector": CrashDetector,
    "LLMSignalAnalyst": LLMSignalAnalyst,
    "Trader": Trader,
    "RiskManager": RiskManager,
}

def create_agent(class_name: str, params: dict) -> BaseAgent:
    """Erstellt Agent-Instanz aus Config"""
    if class_name not in AGENT_REGISTRY:
        raise ValidationError(f"Unknown agent: {class_name}")
    return AGENT_REGISTRY[class_name](params)
```

**And** Team-Loader verwendet Factory für Agent-Erstellung
**And** Unbekannte Agent-Klassen geben klaren Fehler

**Technical Notes:**
- Registry ermöglicht einfache Erweiterung
- Post-MVP: LSTMAnalyst, RLAnalyst hinzufügen

**Prerequisites:** Story 2.4, 2.5, 2.6, 2.7

---

**Epic 2 Complete**

**Stories Created:** 8
**FR Coverage:** FR1, FR2, FR3, FR4, FR5, FR12, FR13, FR14, FR15, FR16
**Technical Context Used:** Architecture Section 3 (Agents), PRD Technical Requirements

---
