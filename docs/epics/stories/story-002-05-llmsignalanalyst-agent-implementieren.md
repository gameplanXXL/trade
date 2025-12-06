---
epic: 002
story: 05
title: "LLMSignalAnalyst Agent implementieren"
status: completed
story_points: 5
covers: [FR13, FR16]
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



## Tasks

- [ ] LangChain ChatAnthropic Setup
- [ ] Prompt-Template erstellen
- [ ] Response-Parsing mit Pydantic
- [ ] Timeout und Error Handling
- [ ] Unit Tests schreiben
**Technical Notes:**
- LangChain ChatAnthropic Wrapper
- Structured Output via Pydantic
- Timeout: 30 Sekunden
- Retry bei API-Fehlern (3 Versuche)

**Prerequisites:** Story 2.3, Story 1.7 (für API-Key)

