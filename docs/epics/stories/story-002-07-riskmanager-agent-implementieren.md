---
epic: 002
story: 07
title: "RiskManager Agent implementieren"
status: backlog
story_points: 3
covers: [FR15, FR16, FR22]
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

