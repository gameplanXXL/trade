---
epic: 009
story: 04
title: "LLM-API Retry-Logic"
status: backlog
story_points: 2
covers: [FR54]
---

## Story 9.4: LLM-API Retry-Logic

Als Entwickler,
möchte ich robuste LLM-API-Aufrufe mit Retry-Logic,
damit temporäre Fehler automatisch behandelt werden.

**Acceptance Criteria:**

**Given** LLMSignalAnalyst
**When** ich Retry-Logic implementiere
**Then** existiert `src/agents/analyst.py` mit:
```python
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

class LLMSignalAnalyst(BaseAgent):
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((APIError, Timeout)),
        before_sleep=lambda retry_state: log.warning(
            "llm_retry",
            attempt=retry_state.attempt_number,
            error=str(retry_state.outcome.exception())
        )
    )
    async def _call_llm(self, prompt: str) -> str:
        """LLM-Aufruf mit Retry"""
        return await self.llm.ainvoke(prompt)
```

**And** Retry bei:
  - Rate Limiting (429)
  - Server Errors (5xx)
  - Timeout

**And** Logging jedes Retry-Versuchs
**And** Fallback nach 3 Versuchen: HOLD-Signal mit Warning

**Technical Notes:**
- tenacity Library für Retry
- Exponential Backoff: 2s, 4s, 8s
- Gesamter Timeout: ~30s

**Prerequisites:** Story 2.5

