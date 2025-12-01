# CLAUDE.md - Multi-Agent Trading Platform

Diese Datei enthält Richtlinien für Claude Code bei der Arbeit an diesem Projekt.

## Projekt-Übersicht

Dies ist eine persönliche, adaptive **Multi-Agent Day-Trading-Plattform**, die verschiedene KI-Technologien (LLM und klassisches ML) kombiniert, um automatisierte Handelsentscheidungen zu treffen. Das System läuft auf einem Ubuntu 24.04 VServer mit MT5 via Wine.

**Kernkonzepte:**
- Multi-Agent-Architektur mit LLM, LSTM und Reinforcement Learning
- Team-basierte Organisation von Agenten
- Agent-Balancing basierend auf Performance
- Shadow-Portfolio für objektive Erfolgsmessung

## Git-Workflow (KRITISCH)

**Alle Änderungen MÜSSEN sofort committed und gepusht werden:**

```bash
# Nach jeder Code-Änderung:
git add -A
git commit -m "Beschreibende Commit-Message"
git push
```

**Regeln:**
- Keine ungespeicherten Änderungen liegen lassen
- Jede logische Änderung separat committen
- Immer sofort nach dem Commit pushen
- Commit-Messages auf Deutsch, klar und beschreibend

## Tech-Stack

### Backend (Python 3.11+)
- **Framework:** FastAPI + Uvicorn
- **Agent-Orchestrierung:** LangGraph + LangChain
- **MT5-Integration:** aiomql
- **Datenbank:** PostgreSQL 16 + TimescaleDB (für Zeitreihen)
- **Cache/Sessions:** Redis 7
- **ORM:** SQLAlchemy 2.0 + asyncpg
- **Migrations:** Alembic
- **Logging:** structlog (JSON)
- **Package Manager:** uv oder poetry

### Frontend (TypeScript)
- **Framework:** React 18 + Vite
- **Styling:** Tailwind CSS + shadcn/ui
- **State:** Zustand
- **Charts:** TradingView Lightweight Charts
- **WebSocket:** Socket.io Client
- **Package Manager:** pnpm

## Projektstruktur

```
trade/
├── backend/
│   ├── src/
│   │   ├── api/           # FastAPI Routes + WebSocket
│   │   ├── agents/        # LangGraph Agent-Rollen
│   │   ├── teams/         # Team-Loader, Pipeline, Overrides
│   │   ├── mt5/           # MT5-Adapter
│   │   ├── db/            # Models + Repositories
│   │   ├── services/      # Business Logic
│   │   ├── config/        # Pydantic Settings
│   │   └── core/          # Exceptions, Logging
│   ├── tests/
│   └── team_templates/    # YAML Team-Definitionen
├── frontend/
│   ├── src/
│   │   ├── components/    # UI + Charts
│   │   ├── features/      # Dashboard, Teams, Analytics
│   │   ├── hooks/
│   │   ├── stores/
│   │   └── lib/
│   └── tests/
└── docs/                  # PRD, Architecture
```

## Naming Conventions

### Python Backend
- **Dateien/Module:** snake_case (`crash_detector.py`)
- **Klassen:** PascalCase (`CrashDetector`)
- **Funktionen:** snake_case (`get_team_by_id()`)
- **Konstanten:** UPPER_SNAKE (`MAX_DRAWDOWN`)
- **Pydantic Models:** PascalCase + Suffix (`TeamCreate`, `TradeResponse`)

### TypeScript Frontend
- **Komponenten:** PascalCase (`TeamCard.tsx`)
- **Hooks:** camelCase + use (`useTeams.ts`)
- **Stores:** camelCase + Store (`teamStore.ts`)
- **Utilities:** camelCase (`formatCurrency.ts`)

### Datenbank
- **Tabellen:** snake_case, plural (`teams`, `trades`)
- **Spalten:** snake_case (`created_at`, `team_id`)
- **Foreign Keys:** `{table}_id` (`team_id`)

### API
- **Endpoints:** plural, kebab-case (`/api/teams`, `/api/agent-decisions`)
- **Actions:** verb prefix (`/api/teams/{id}/start`)

## API Response Format

**Erfolg:**
```json
{
  "data": { ... },
  "meta": { "timestamp": "2025-12-01T10:30:00Z" }
}
```

**Fehler:**
```json
{
  "error": {
    "code": "TEAM_NOT_FOUND",
    "message": "Team with ID 123 not found"
  }
}
```

## Error Handling

Python Exception Hierarchy:
```python
class TradingError(Exception):
    code: str = "TRADING_ERROR"

class MT5ConnectionError(TradingError):
    code = "MT5_CONNECTION_ERROR"

class PipelineError(TradingError):
    code = "PIPELINE_ERROR"
```

## Logging (structlog JSON)

```python
import structlog
log = structlog.get_logger()
log.info("trade_executed", team_id=123, symbol="EUR/USD", action="BUY")
```

## WebSocket Events

Format: `{domain}:{action}`
- `team:status_changed`
- `trade:executed`
- `alert:warning`

## Build & Run Commands

```bash
# Backend
cd backend
uv run uvicorn src.main:app --reload

# Frontend
cd frontend
pnpm dev

# Tests
cd backend && uv run pytest
cd frontend && pnpm test

# Linting
cd backend && uv run ruff check .
cd frontend && pnpm lint
```

## Wichtige Dokumentation

- **PRD:** `/docs/prd.md` - Alle funktionalen Anforderungen
- **Architektur:** `/docs/architecture.md` - Technische Entscheidungen und Patterns
- **BMAD Config:** `.bmad/core/config.yaml` - Projekteinstellungen

## Performance-Ziele

| Metrik | Ziel |
|--------|------|
| Pipeline-Durchlauf | < 1s |
| Dashboard-Load | < 2s |
| WebSocket-Latenz | < 500ms |
| DB-Queries | < 100ms |

## Sicherheitsrichtlinien

- Credentials mit Fernet verschlüsseln
- Keine Secrets in Logs
- Alle API-Inputs validieren (Pydantic)
- Session-basierte Authentifizierung via Redis

## Sprache

- **Code:** Englisch (Variablen, Funktionen, Kommentare)
- **Dokumentation:** Deutsch (PRD, Architecture, User-facing)
- **Commit-Messages:** Deutsch
