---
epic: 001
story: 02
title: "Exception-Hierarchie und Logging einrichten"
status: done
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

## Tasks

- [x] Task 1: Story-Status auf in-progress setzen
- [x] Task 2: FastAPI Exception Handler implementieren
- [x] Task 3: Secrets-Filterung in structlog einbauen
- [x] Task 4: Logging beim App-Start initialisieren
- [x] Task 5: Tests und Verifizierung

## Dev Agent Record

### Agent Model Used
Claude Opus 4.5 (claude-opus-4-5-20251101)

### Completion Notes
Alle Acceptance Criteria erfüllt:
- ✅ Exception-Hierarchie in `src/core/exceptions.py` (bereits in Story 001-01)
- ✅ FastAPI Exception Handler mit JSON-Fehlerformat
- ✅ structlog mit JSON-Output und ISO-Timestamps
- ✅ Secrets-Filterung für password, api_key, secret, token, etc.
- ✅ Logging-Initialisierung beim App-Start via lifespan
- ✅ ruff check bestanden

### Verified Output Examples
```json
// GET /test-error Response:
{"error":{"code":"TRADING_ERROR","message":"This is a test error","details":{"test":true}}}

// Secrets Filtering:
{"password": "[REDACTED]", "user": "john", "event": "test", ...}
{"message": "Config: password=[REDACTED], server=localhost", ...}
```

## File List
- `backend/src/api/exception_handlers.py` - FastAPI Exception Handler (NEU)
- `backend/src/core/logging.py` - structlog mit Secrets-Filterung (ERWEITERT)
- `backend/src/main.py` - Lifespan-Handler und Exception-Registration (ERWEITERT)

## Change Log
- 2025-12-03: Story gestartet, Status: in-progress
- 2025-12-03: Story abgeschlossen, Status: done

