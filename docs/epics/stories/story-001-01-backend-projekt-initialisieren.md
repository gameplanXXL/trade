---
epic: 001
story: 01
title: "Backend-Projekt initialisieren"
status: done
story_points: 3
---

## Story 1.1: Backend-Projekt initialisieren

Als Entwickler,
möchte ich ein strukturiertes Python-Backend-Projekt mit FastAPI,
damit ich eine solide Basis für alle weiteren Backend-Features habe.

**Acceptance Criteria:**

**Given** ein leeres `backend/` Verzeichnis
**When** ich das Projekt initialisiere
**Then** existiert eine `pyproject.toml` mit allen Core-Dependencies:
  - fastapi >= 0.104
  - uvicorn[standard]
  - sqlalchemy >= 2.0
  - asyncpg
  - alembic
  - redis
  - pydantic >= 2.0
  - pydantic-settings
  - structlog
  - python-socketio

**And** die Projektstruktur entspricht der Architecture:
```
backend/
├── pyproject.toml
├── alembic.ini
├── .env.example
└── src/
    ├── __init__.py
    ├── main.py
    ├── api/
    │   ├── __init__.py
    │   └── deps.py
    ├── config/
    │   ├── __init__.py
    │   └── settings.py
    └── core/
        ├── __init__.py
        ├── exceptions.py
        └── logging.py
```

**And** `src/main.py` startet einen FastAPI-Server auf Port 8000
**And** `GET /health` gibt `{"status": "ok"}` zurück
**And** `uv run uvicorn src.main:app --reload` startet erfolgreich

## Tasks

- [x] Task 1: Backend-Verzeichnis und pyproject.toml erstellen
- [x] Task 2: Projektstruktur anlegen (src/, api/, config/, core/)
- [x] Task 3: FastAPI main.py mit Health-Endpoint implementieren
- [x] Task 4: Basis-Module erstellen (deps.py, settings.py, exceptions.py, logging.py)
- [x] Task 5: alembic.ini und .env.example erstellen
- [x] Task 6: Server starten und Health-Endpoint testen

## Dev Notes

**Technical Notes:**
- Package Manager: uv (bevorzugt) oder poetry
- Python Version: 3.11+
- Settings via Pydantic Settings mit `.env` Support

**Prerequisites:** Keine

## Dev Agent Record

### Agent Model Used
Claude Opus 4 (claude-opus-4-5-20250514)

### Implementation Plan
1. Erstelle backend/ Verzeichnis mit pyproject.toml
2. Lege Projektstruktur gemäß Architecture an
3. Implementiere FastAPI main.py mit /health Endpoint
4. Erstelle Basis-Module für spätere Stories
5. Konfiguriere Alembic für Migrations
6. Teste Server-Start und Health-Endpoint

### Debug Log References
- uv nicht installiert → `curl -LsSf https://astral.sh/uv/install.sh | sh` ausgeführt
- hatchling konnte Package nicht finden → `[tool.hatch.build.targets.wheel] packages = ["src"]` zur pyproject.toml hinzugefügt
- README.md fehlte → README.md erstellt

### Completion Notes
Alle Acceptance Criteria erfüllt:
- ✅ pyproject.toml mit allen Core-Dependencies erstellt
- ✅ Projektstruktur gemäß Architecture angelegt
- ✅ FastAPI main.py mit /health Endpoint implementiert
- ✅ Basis-Module (deps.py, settings.py, exceptions.py, logging.py) erstellt
- ✅ alembic.ini und .env.example erstellt
- ✅ Server startet erfolgreich, /health gibt {"status":"ok"} zurück
- ✅ ruff check bestanden

## File List
- `backend/pyproject.toml` - Projekt-Konfiguration mit Dependencies
- `backend/README.md` - Projekt-README
- `backend/alembic.ini` - Alembic Migrations-Konfiguration
- `backend/.env.example` - Environment-Variablen-Template
- `backend/src/__init__.py` - Package-Initialisierung
- `backend/src/main.py` - FastAPI Entry Point mit /health Endpoint
- `backend/src/api/__init__.py` - API-Modul-Init
- `backend/src/api/deps.py` - Dependency Injection
- `backend/src/config/__init__.py` - Config-Modul-Init
- `backend/src/config/settings.py` - Pydantic Settings
- `backend/src/core/__init__.py` - Core-Modul-Init
- `backend/src/core/exceptions.py` - Exception-Hierarchie
- `backend/src/core/logging.py` - structlog-Konfiguration

## Change Log
- 2025-12-03: Story gestartet, Status: in-progress
- 2025-12-03: Story abgeschlossen, Status: done
