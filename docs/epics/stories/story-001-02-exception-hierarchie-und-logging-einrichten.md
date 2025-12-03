---
epic: 001
story: 02
title: "Exception-Hierarchie und Logging einrichten"
status: backlog
story_points: 2
covers: [FR53]
---

## Story 1.2: Exception-Hierarchie und Logging einrichten

Als Entwickler,
möchte ich eine einheitliche Exception-Hierarchie und strukturiertes Logging,
damit alle Fehler konsistent behandelt und geloggt werden.

**Acceptance Criteria:**

**Given** das initialisierte Backend-Projekt
**When** ich die Exception-Hierarchie implementiere
**Then** existiert in `src/core/exceptions.py`:
```python
class TradingError(Exception):
    code: str = "TRADING_ERROR"

class MT5ConnectionError(TradingError):
    code = "MT5_CONNECTION_ERROR"

class PipelineError(TradingError):
    code = "PIPELINE_ERROR"

class ValidationError(TradingError):
    code = "VALIDATION_ERROR"
```

**And** ein FastAPI Exception Handler gibt JSON-Fehler zurück:
```json
{
  "error": {
    "code": "TRADING_ERROR",
    "message": "Beschreibung des Fehlers"
  }
}
```

**And** structlog ist konfiguriert mit JSON-Output:
```python
import structlog
log = structlog.get_logger()
log.info("event_name", key="value")
# Output: {"timestamp": "...", "level": "INFO", "event": "event_name", "key": "value"}
```

**And** Secrets werden aus Logs gefiltert (keine Passwords, API-Keys)

**Technical Notes:**
- structlog Processor Chain für JSON-Formatierung
- Log-Level via Environment Variable `LOG_LEVEL` (default: INFO)
- Sensitive Fields: `password`, `api_key`, `secret`, `token`

**Prerequisites:** Story 1.1

