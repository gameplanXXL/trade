---
epic: 002
story: 04
title: "CrashDetector Agent implementieren"
status: completed
story_points: 3
covers: [FR12, FR16]
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

