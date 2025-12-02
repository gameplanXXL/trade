---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8]
inputDocuments:
  - "/docs/prd.md"
  - "/docs/analysis/research/technical-ki-trading-plattform-research-2025-12-01.md"
workflowType: 'architecture'
lastStep: 8
project_name: 'trade'
user_name: 'Christian'
date: '2025-12-01'
status: 'complete'
completedAt: '2025-12-01'
---

# Architecture Decision Document

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together._

## Project Context Analysis

### Requirements Overview

**Functional Requirements:**

Das PRD definiert 54 funktionale Anforderungen in 8 Kategorien:

| Kategorie | Anzahl | Architektonische Implikation |
|-----------|--------|------------------------------|
| Team-Konfiguration | 5 | YAML-Parser, Pydantic-Validierung |
| Team-Instanz-Management | 6 | PostgreSQL CRUD, State Management |
| Agent-Rollen | 5 | Plugin-Architektur, Python-Klassen |
| Pipeline & Regeln | 6 | Sequenzielle Executor, Priority Queue |
| Trading Execution | 6 | MT5-Adapter, Order-Management |
| Performance Analytics | 7 | TimescaleDB, Aggregations-Pipeline |
| Dashboard | 13 | REST API, WebSocket, Vue/React |
| Sicherheit & Fehler | 6 | Encryption, Retry-Logic, Logging |

**Non-Functional Requirements:**

| NFR | Zielwert | Architektonische Konsequenz |
|-----|----------|----------------------------|
| Pipeline-Durchlauf | < 1s | Async Processing, kein Blocking |
| Dashboard-Load | < 2s | Lazy Loading, Caching |
| WebSocket-Latenz | < 500ms | Redis Pub/Sub, Event-Driven |
| LLM-Response | < 5s | Timeout-Handling, Fallback |
| DB-Queries | < 100ms | Indexing, Query-Optimierung |
| Max. Teams | 20 | Horizontal Scalability (später) |

**Scale & Complexity:**

- **Primary domain:** Backend-Orchestrierung mit Web-Dashboard
- **Complexity level:** Hoch
- **Estimated architectural components:** 12-15 Core-Services

### Technical Constraints & Dependencies

| Constraint | Entscheidung | Impact |
|------------|--------------|--------|
| **MT5-Plattform** | Wine unter Ubuntu 24.04 | Single-Server-Deployment, alle Services auf einem Host |
| **LLM-API-Kosten** | Cloud-APIs initial, vLLM später | Caching wichtig, Fallback-Strategie |
| **Single-Server** | Docker Compose | Kein Kubernetes nötig, einfaches Deployment |
| **Persönliche Nutzung** | Simplified Auth | Session-basiert, kein OAuth/OIDC |

### Cross-Cutting Concerns Identified

| Concern | Strategie |
|---------|-----------|
| **Error Handling** | Einheitliche Exception-Hierarchie, Retry-Policies (LLM, MT5) |
| **Logging** | Strukturiertes JSON-Logging, Agent-Decision-Audit-Trail |
| **Configuration** | YAML-basiert mit Pydantic-Validierung, Hot-Reload |
| **Security** | Credential-Verschlüsselung (Fernet), HTTPS, keine Secrets in Logs |
| **Monitoring** | Health-Endpoints, Dashboard-integrierte Metriken |

### MT5/Wine Integration

**Deployment-Modell:**
```
Ubuntu 24.04 VServer
├── Wine + MT5 Terminal (GUI-less oder VNC)
├── Python Backend (FastAPI, LangGraph)
├── PostgreSQL + TimescaleDB
├── Redis
└── Frontend (Nginx + Vue/React)
```

**MT5-Kommunikation:**
- `aiomql` oder offizielle `MetaTrader5`-Bibliothek verbindet sich via IPC zum Wine-MT5
- Wine-Kompatibilität für MT5 ist gut dokumentiert und produktionserprobt
- Optional: Xvfb für headless MT5-Betrieb

## Starter Template & Project Structure

### Technology Stack Decision

| Layer | Technologie | Begründung |
|-------|-------------|------------|
| **Backend** | Python 3.11+ / FastAPI | MT5-Integration, LangGraph, ML-Ökosystem |
| **Frontend** | React 18 / Vite / TypeScript | Großes Ökosystem, TradingView-Integration |
| **Styling** | Tailwind CSS + shadcn/ui | Rapid Development, konsistente UI |
| **State** | Zustand (Frontend), Redis (Backend) | Lightweight, performant |

### Backend Project Structure

Modulare Struktur optimiert für Multi-Agent-Trading:

```
src/
├── api/                 # FastAPI Routes
│   ├── routes/          # REST Endpoints
│   └── websocket/       # WebSocket Handler
├── agents/              # LangGraph Agent-Rollen
│   ├── crash_detector.py
│   ├── analyst.py
│   ├── trader.py
│   └── risk_manager.py
├── teams/               # Team-Loader & Pipeline-Executor
│   ├── loader.py        # YAML-Parser
│   ├── pipeline.py      # Sequential Executor
│   └── override.py      # Override-Rule-Engine
├── mt5/                 # MT5-Adapter (aiomql)
├── db/                  # SQLAlchemy Models + Repositories
│   ├── models/
│   └── repositories/
├── services/            # Business Logic
│   ├── analytics.py
│   └── balancing.py
├── config/              # Pydantic Settings
└── main.py
```

### Frontend Project Structure

Vite-basierte React-App mit TypeScript:

```
src/
├── components/          # UI-Komponenten (shadcn/ui basiert)
│   ├── ui/              # Basis-Komponenten
│   └── charts/          # TradingView Charts
├── features/            # Feature-Module
│   ├── dashboard/
│   ├── teams/
│   └── analytics/
├── hooks/               # Custom Hooks
│   ├── useWebSocket.ts
│   └── useTeams.ts
├── stores/              # Zustand Stores
├── lib/                 # Utilities, API-Client
└── App.tsx
```

### Development Tooling

| Tool | Backend | Frontend |
|------|---------|----------|
| **Package Manager** | uv / poetry | pnpm |
| **Linting** | ruff | ESLint + Prettier |
| **Testing** | pytest + pytest-asyncio | Vitest |
| **Type Checking** | mypy | TypeScript strict |
| **Formatting** | ruff format | Prettier |

### Key Libraries

**Backend:**
- `fastapi` + `uvicorn` – Web Framework
- `langgraph` – Agent-Orchestrierung
- `aiomql` – MT5 Async Integration
- `sqlalchemy` + `asyncpg` – Database ORM
- `redis` + `aioredis` – Caching & Pub/Sub
- `pydantic` – Validation & Settings
- `structlog` – Structured Logging

**Frontend:**
- `react` + `react-dom` – UI Framework
- `@tanstack/react-query` – Server State
- `zustand` – Client State
- `lightweight-charts` – TradingView Charts
- `react-router-dom` – Routing
- `socket.io-client` – WebSocket

## Core Architectural Decisions

### Decision Summary

| Kategorie | Entscheidung | Rationale |
|-----------|--------------|-----------|
| **Database** | PostgreSQL 16 + TimescaleDB | Zeitreihen-optimiert für Trading-Daten |
| **ORM** | SQLAlchemy 2.0 + asyncpg | Async-native, Type-Safe |
| **Migrations** | Alembic | Standard für SQLAlchemy |
| **Cache** | Redis 7 | Session Store + Pub/Sub für WebSocket |
| **Auth** | Redis Sessions | Stateful, Logout-fähig, Single-User |
| **Credentials** | Fernet Encryption | Python-native, ausreichend für Personal Use |
| **WebSocket** | python-socketio + Socket.io Client | Robust Reconnect, Rooms für Team-Updates |
| **LLM Integration** | LangChain Wrappers | Nahtlose LangGraph-Integration |

### Data Architecture

**TimescaleDB Hypertables:**

| Tabelle | Partitionierung | Retention |
|---------|-----------------|-----------|
| `market_data` | Zeit (1 Tag) | 30 Tage raw, dann aggregiert |
| `trades` | Zeit (1 Woche) | Unbegrenzt |
| `performance_metrics` | Zeit (1 Tag) | Unbegrenzt (aggregiert) |

**Standard PostgreSQL Tabellen:**
- `teams` – Team-Instanzen
- `team_templates` – YAML-Referenzen
- `agent_decisions` – Audit-Log
- `users` – Single User (Personal Use)

### Authentication & Security

**Session Flow:**
```
Login → Validate Password → Create Redis Session → Set Cookie
Request → Read Cookie → Validate Session in Redis → Allow/Deny
Logout → Delete Redis Session → Clear Cookie
```

**Credential Storage:**
```python
from cryptography.fernet import Fernet

# Encrypted in DB, key in environment
MT5_PASSWORD = Fernet(KEY).encrypt(password.encode())
LLM_API_KEY = Fernet(KEY).encrypt(api_key.encode())
```

### API & Communication

**REST Endpoints (FastAPI):**
- `/api/teams/*` – Team CRUD
- `/api/analytics/*` – Performance-Daten
- `/api/config/*` – System-Konfiguration

**WebSocket Events (Socket.io):**

| Event | Direction | Payload |
|-------|-----------|---------|
| `team:status` | Server → Client | Team-Status-Updates |
| `trade:executed` | Server → Client | Neue Trade-Benachrichtigung |
| `alert:warning` | Server → Client | Warnung (Drawdown, etc.) |
| `alert:crash` | Server → Client | Crash-Detection-Alert |

**Rooms:**
- `team:{team_id}` – Updates für spezifisches Team
- `global` – System-weite Alerts

### LLM Integration

**LangChain + LangGraph Setup:**
```python
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph

# Unified interface via LangChain
llm_claude = ChatAnthropic(model="claude-sonnet-4-20250514")
llm_openai = ChatOpenAI(model="gpt-4o")

# Used in LangGraph agents
analyst_node = create_analyst_agent(llm=llm_claude)
```

### Infrastructure

**Docker Compose Services:**

| Service | Image | Ports |
|---------|-------|-------|
| `backend` | Custom Python | 8000 |
| `frontend` | Nginx + React Build | 80, 443 |
| `postgres` | timescale/timescaledb | 5432 |
| `redis` | redis:7-alpine | 6379 |

**MT5 (Host-Level, nicht Docker):**
- Wine + MT5 läuft direkt auf Ubuntu Host
- Python Backend kommuniziert via IPC

## Implementation Patterns & Consistency Rules

### Naming Patterns

**Database (PostgreSQL):**

| Element | Convention | Beispiel |
|---------|------------|----------|
| Tabellen | snake_case, plural | `teams`, `trades`, `agent_decisions` |
| Spalten | snake_case | `created_at`, `team_id`, `is_active` |
| Foreign Keys | `{table}_id` | `team_id`, `user_id` |
| Indizes | `idx_{table}_{columns}` | `idx_trades_team_id` |
| Constraints | `{table}_{type}_{columns}` | `teams_pk_id`, `trades_fk_team_id` |

**Python Backend:**

| Element | Convention | Beispiel |
|---------|------------|----------|
| Module/Dateien | snake_case | `crash_detector.py`, `team_loader.py` |
| Klassen | PascalCase | `CrashDetector`, `TeamInstance` |
| Funktionen | snake_case | `get_team_by_id()`, `execute_pipeline()` |
| Konstanten | UPPER_SNAKE | `MAX_DRAWDOWN`, `DEFAULT_TIMEOUT` |
| Pydantic Models | PascalCase + Suffix | `TeamCreate`, `TradeResponse` |

**React Frontend:**

| Element | Convention | Beispiel |
|---------|------------|----------|
| Komponenten | PascalCase | `TeamCard.tsx`, `DashboardView.tsx` |
| Hooks | camelCase + use | `useTeams.ts`, `useWebSocket.ts` |
| Utilities | camelCase | `formatCurrency.ts`, `apiClient.ts` |
| Stores | camelCase + Store | `teamStore.ts`, `alertStore.ts` |
| Types/Interfaces | PascalCase | `Team`, `TradeEvent` |

**API Endpoints:**

| Pattern | Convention | Beispiel |
|---------|------------|----------|
| Resources | plural, kebab-case | `/api/teams`, `/api/agent-decisions` |
| Actions | verb prefix | `/api/teams/{id}/start`, `/api/teams/{id}/stop` |
| Query Params | snake_case | `?team_id=1&include_trades=true` |

### API Response Format

**Erfolg:**
```json
{
  "data": { ... },
  "meta": {
    "timestamp": "2025-12-01T10:30:00Z"
  }
}
```

**Fehler:**
```json
{
  "error": {
    "code": "TEAM_NOT_FOUND",
    "message": "Team with ID 123 not found",
    "details": { ... }
  }
}
```

**Liste mit Pagination:**
```json
{
  "data": [ ... ],
  "meta": {
    "total": 100,
    "page": 1,
    "per_page": 20
  }
}
```

### Socket.io Event Patterns

| Element | Convention | Beispiel |
|---------|------------|----------|
| Event Naming | `{domain}:{action}` | `team:status_changed`, `trade:executed` |
| Room Naming | `{domain}:{id}` | `team:123`, `global` |

**Event Payload Struktur:**
```json
{
  "event": "team:status_changed",
  "data": {
    "team_id": 123,
    "old_status": "active",
    "new_status": "paused"
  },
  "timestamp": "2025-12-01T10:30:00Z"
}
```

### Error Handling Patterns

**Python Exception Hierarchy:**
```python
class TradingError(Exception):
    """Base exception for trading operations"""
    code: str = "TRADING_ERROR"

class MT5ConnectionError(TradingError):
    code = "MT5_CONNECTION_ERROR"

class PipelineError(TradingError):
    code = "PIPELINE_ERROR"

class ValidationError(TradingError):
    code = "VALIDATION_ERROR"

class InsufficientBudgetError(TradingError):
    code = "INSUFFICIENT_BUDGET"
```

**FastAPI Exception Handler:**
```python
@app.exception_handler(TradingError)
async def trading_error_handler(request: Request, exc: TradingError):
    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "code": exc.code,
                "message": str(exc),
                "details": getattr(exc, "details", None)
            }
        }
    )
```

### Logging Patterns

**Format (structlog JSON):**
```json
{
  "timestamp": "2025-12-01T10:30:00Z",
  "level": "INFO",
  "event": "trade_executed",
  "team_id": 123,
  "trade_id": 456,
  "symbol": "EUR/USD",
  "action": "BUY",
  "amount": 0.1
}
```

**Log-Level Verwendung:**

| Level | Verwendung | Beispiel |
|-------|------------|----------|
| DEBUG | Entwicklung, Pipeline-Details | Pipeline step completed |
| INFO | Trade-Ausführungen, Team-Status | Trade executed, Team started |
| WARNING | Drawdown-Schwellen, Retry-Attempts | Drawdown at 15%, LLM retry 2/3 |
| ERROR | Fehlgeschlagene Operationen | MT5 connection failed |

### Enforcement Guidelines

**Alle AI-Agenten MÜSSEN:**

1. Diese Naming-Conventions bei Codegenerierung befolgen
2. API-Responses im definierten Format zurückgeben
3. Exceptions aus der definierten Hierarchy verwenden
4. Strukturiertes Logging mit den definierten Feldern nutzen
5. Socket.io Events im `{domain}:{action}` Format benennen

**Verification:**
- Ruff für Python Linting (Naming Conventions)
- ESLint für TypeScript (Naming Conventions)
- API-Tests prüfen Response-Format
- Log-Aggregation prüft JSON-Struktur

## Project Structure & Boundaries

### Complete Project Directory Structure

```
trade/
├── README.md
├── docker-compose.yml
├── docker-compose.dev.yml
├── .env.example
├── .gitignore
├── Makefile                      # Dev-Shortcuts (make dev, make test)
│
├── backend/
│   ├── pyproject.toml            # uv/poetry Config
│   ├── alembic.ini
│   ├── .env.example
│   │
│   ├── src/
│   │   ├── __init__.py
│   │   ├── main.py               # FastAPI Entry Point
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── deps.py           # Dependency Injection
│   │   │   ├── routes/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── teams.py      # /api/teams/*
│   │   │   │   ├── analytics.py  # /api/analytics/*
│   │   │   │   ├── trades.py     # /api/trades/*
│   │   │   │   └── auth.py       # /api/auth/*
│   │   │   └── websocket/
│   │   │       ├── __init__.py
│   │   │       ├── handler.py    # Socket.io Handler
│   │   │       └── events.py     # Event Definitions
│   │   │
│   │   ├── agents/               # LangGraph Agent-Rollen
│   │   │   ├── __init__.py
│   │   │   ├── base.py           # BaseAgent Abstract Class
│   │   │   ├── crash_detector.py
│   │   │   ├── analyst.py        # LLMSignalAnalyst
│   │   │   ├── trader.py
│   │   │   └── risk_manager.py
│   │   │
│   │   ├── teams/                # Team-System
│   │   │   ├── __init__.py
│   │   │   ├── loader.py         # YAML Team-Loader
│   │   │   ├── pipeline.py       # Pipeline Executor
│   │   │   ├── override.py       # Override-Rule-Engine
│   │   │   └── schemas.py        # Team Pydantic Models
│   │   │
│   │   ├── mt5/                  # MT5 Integration
│   │   │   ├── __init__.py
│   │   │   ├── connector.py      # aiomql Wrapper
│   │   │   ├── orders.py         # Order Management
│   │   │   └── market_data.py    # Price Feed
│   │   │
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── session.py        # SQLAlchemy Session
│   │   │   ├── models/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── team.py
│   │   │   │   ├── trade.py
│   │   │   │   ├── market_data.py
│   │   │   │   └── agent_decision.py
│   │   │   └── repositories/
│   │   │       ├── __init__.py
│   │   │       ├── team_repo.py
│   │   │       ├── trade_repo.py
│   │   │       └── analytics_repo.py
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── analytics.py      # Performance Calculation
│   │   │   ├── balancing.py      # Agent-Balancing (Post-MVP)
│   │   │   └── credentials.py    # Fernet Encryption
│   │   │
│   │   ├── config/
│   │   │   ├── __init__.py
│   │   │   └── settings.py       # Pydantic Settings
│   │   │
│   │   └── core/
│   │       ├── __init__.py
│   │       ├── exceptions.py     # Exception Hierarchy
│   │       └── logging.py        # Structlog Setup
│   │
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   │
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py           # Fixtures
│   │   ├── unit/
│   │   │   ├── test_agents/
│   │   │   ├── test_teams/
│   │   │   └── test_services/
│   │   └── integration/
│   │       ├── test_api/
│   │       └── test_mt5/
│   │
│   └── team_templates/           # YAML Team-Definitionen
│       ├── conservative_llm.yaml
│       └── aggressive_lstm.yaml
│
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   ├── .env.example
│   │
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── index.css
│   │   │
│   │   ├── components/
│   │   │   ├── ui/               # shadcn/ui Basis
│   │   │   │   ├── button.tsx
│   │   │   │   ├── card.tsx
│   │   │   │   └── ...
│   │   │   ├── charts/
│   │   │   │   ├── PriceChart.tsx
│   │   │   │   ├── PerformanceChart.tsx
│   │   │   │   └── DrawdownChart.tsx
│   │   │   └── layout/
│   │   │       ├── Header.tsx
│   │   │       ├── Sidebar.tsx
│   │   │       └── MainLayout.tsx
│   │   │
│   │   ├── features/
│   │   │   ├── dashboard/
│   │   │   │   ├── DashboardView.tsx
│   │   │   │   ├── TeamCard.tsx
│   │   │   │   └── AlertList.tsx
│   │   │   ├── teams/
│   │   │   │   ├── TeamList.tsx
│   │   │   │   ├── TeamDetail.tsx
│   │   │   │   └── TeamCreate.tsx
│   │   │   ├── analytics/
│   │   │   │   ├── AnalyticsView.tsx
│   │   │   │   └── TradeHistory.tsx
│   │   │   └── auth/
│   │   │       └── LoginForm.tsx
│   │   │
│   │   ├── hooks/
│   │   │   ├── useWebSocket.ts
│   │   │   ├── useTeams.ts
│   │   │   └── useAnalytics.ts
│   │   │
│   │   ├── stores/
│   │   │   ├── teamStore.ts
│   │   │   ├── alertStore.ts
│   │   │   └── authStore.ts
│   │   │
│   │   ├── lib/
│   │   │   ├── api.ts            # Axios/Fetch Client
│   │   │   ├── socket.ts         # Socket.io Client
│   │   │   └── utils.ts
│   │   │
│   │   └── types/
│   │       ├── team.ts
│   │       ├── trade.ts
│   │       └── api.ts
│   │
│   └── tests/
│       └── components/
│
└── docs/
    ├── prd.md
    ├── architecture.md
    └── analysis/
```

### Architectural Boundaries

**Layer Architecture:**

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React)                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  Dashboard  │  │   Teams     │  │  Analytics  │         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │
│         └────────────────┼────────────────┘                 │
│                          │ REST + WebSocket                 │
├──────────────────────────┼──────────────────────────────────┤
│                     Backend (FastAPI)                        │
│                          │                                   │
│  ┌───────────────────────┼───────────────────────┐         │
│  │                  API Layer                     │         │
│  │  routes/* + websocket/*                        │         │
│  └───────────────────────┼───────────────────────┘         │
│                          │                                   │
│  ┌───────────────────────┼───────────────────────┐         │
│  │               Service Layer                    │         │
│  │  services/* + teams/*                          │         │
│  └───────────────────────┼───────────────────────┘         │
│                          │                                   │
│  ┌───────────────────────┼───────────────────────┐         │
│  │             Agent Layer (LangGraph)            │         │
│  │  agents/*                                      │         │
│  └───────────────────────┼───────────────────────┘         │
│                          │                                   │
│  ┌───────────────────────┼───────────────────────┐         │
│  │              Data Access Layer                 │         │
│  │  db/repositories/* + mt5/*                     │         │
│  └───────────────────────┼───────────────────────┘         │
├──────────────────────────┼──────────────────────────────────┤
│           PostgreSQL + TimescaleDB + Redis                   │
└──────────────────────────┼──────────────────────────────────┘
                           │
                    ┌──────┴──────┐
                    │  MT5 (Wine) │
                    └─────────────┘
```

**API Boundaries:**

| Boundary | Beschreibung | Location |
|----------|--------------|----------|
| Public API | REST + WebSocket für Frontend | `api/routes/*`, `api/websocket/*` |
| Internal Services | Service-to-Service Kommunikation | Direkte Python Imports |
| MT5 Adapter | Externe MT5-Integration | `mt5/*` |
| LLM Services | Externe API-Aufrufe | `agents/analyst.py` |

**Data Boundaries:**

| Boundary | Technologie | Zugriff |
|----------|-------------|---------|
| PostgreSQL | Stammdaten (Teams, Config) | `db/repositories/*` |
| TimescaleDB | Zeitreihen (Trades, Market Data) | `db/repositories/*` |
| Redis | Sessions, Cache, Pub/Sub | `api/deps.py`, `api/websocket/*` |

### Requirements to Structure Mapping

| FR-Kategorie | Backend Location | Frontend Location |
|--------------|------------------|-------------------|
| Team-Konfiguration (FR1-5) | `teams/loader.py`, `teams/schemas.py` | `features/teams/TeamCreate.tsx` |
| Team-Instanz-Management (FR6-11) | `api/routes/teams.py`, `db/repositories/team_repo.py` | `features/teams/TeamList.tsx` |
| Agent-Rollen (FR12-16) | `agents/*.py` | - |
| Pipeline & Regeln (FR17-22) | `teams/pipeline.py`, `teams/override.py` | - |
| Trading Execution (FR23-28) | `mt5/*.py`, `agents/trader.py` | - |
| Performance Analytics (FR29-35) | `services/analytics.py`, `db/repositories/analytics_repo.py` | `features/analytics/*` |
| Dashboard (FR36-48) | `api/routes/*.py`, `api/websocket/*` | `features/dashboard/*` |
| Sicherheit (FR49-51) | `services/credentials.py`, `api/routes/auth.py` | `features/auth/*` |

### Data Flow

**Market Data Flow:**
```
MT5 → mt5/connector.py → market_data (TimescaleDB)
                       → WebSocket → Frontend Charts
```

**Trading Flow:**
```
Frontend → API → teams/pipeline.py → agents/* → mt5/orders.py → MT5
                                             ↓
                                     trades (PostgreSQL)
                                             ↓
                                     WebSocket → Frontend
```

**Alert Flow:**
```
agents/risk_manager.py → WebSocket (global room) → Frontend AlertList
```

## Architecture Validation Results

### Coherence Validation ✅

**Decision Compatibility:**

| Check | Status | Details |
|-------|--------|---------|
| Python 3.11 + FastAPI + SQLAlchemy | ✅ | Vollständig kompatibel |
| LangGraph + LangChain | ✅ | Gleiche Ökosystem-Familie |
| aiomql + asyncio | ✅ | Async-native Integration |
| PostgreSQL + TimescaleDB | ✅ | TimescaleDB ist PostgreSQL-Extension |
| React + Vite + TypeScript | ✅ | Standard-Stack |
| Socket.io (Python + JS) | ✅ | Offizielle Libraries beidseitig |

**Pattern Consistency:**
- Naming: Python snake_case, TypeScript camelCase/PascalCase ✅
- API: REST + WebSocket konsistent definiert ✅
- Logging: structlog JSON überall ✅
- Error Handling: Exception Hierarchy definiert ✅

**Structure Alignment:**
- Layer-Trennung (API → Service → Agent → Data) ✅
- Frontend Feature-basiert organisiert ✅
- Tests strukturiert (unit/integration) ✅

### Requirements Coverage Validation ✅

**Functional Requirements Coverage (54 FRs):**

| Kategorie | FRs | Architektur-Support | Status |
|-----------|-----|---------------------|--------|
| Team-Konfiguration | FR1-5 | `teams/loader.py`, YAML-Schema | ✅ |
| Team-Instanz-Management | FR6-11 | `db/models/team.py`, REST API | ✅ |
| Agent-Rollen | FR12-16 | `agents/*.py`, BaseAgent | ✅ |
| Pipeline & Regeln | FR17-22 | `teams/pipeline.py`, `override.py` | ✅ |
| Trading Execution | FR23-28 | `mt5/*.py`, Trailing SL | ✅ |
| Performance Analytics | FR29-35 | `services/analytics.py`, TimescaleDB | ✅ |
| Dashboard | FR36-48 | REST + WebSocket + React | ✅ |
| Sicherheit & Fehler | FR49-54 | Fernet, Sessions, Retry | ✅ |

**Non-Functional Requirements Coverage:**

| NFR | Architektur-Support | Status |
|-----|---------------------|--------|
| Pipeline < 1s | Async Processing, kein Blocking | ✅ |
| Dashboard < 2s | Vite Build, Lazy Loading | ✅ |
| WebSocket < 500ms | Socket.io, Redis Pub/Sub | ✅ |
| Max 20 Teams | PostgreSQL, stateless Backend | ✅ |
| Credentials verschlüsselt | Fernet Encryption | ✅ |
| Strukturiertes Logging | structlog JSON | ✅ |

### Implementation Readiness Validation ✅

**Decision Completeness:**
- [x] Alle kritischen Entscheidungen mit Versionen dokumentiert
- [x] Implementation Patterns umfassend definiert
- [x] Consistency Rules klar und durchsetzbar
- [x] Beispiele für alle wichtigen Patterns vorhanden

**Structure Completeness:**
- [x] Projektstruktur vollständig (~60 Dateien/Ordner)
- [x] Alle Dateien und Verzeichnisse definiert
- [x] Integration Points klar spezifiziert
- [x] Component Boundaries gut definiert

**Pattern Completeness:**
- [x] Alle potenziellen Konfliktpunkte adressiert
- [x] Naming Conventions umfassend
- [x] Communication Patterns vollständig spezifiziert
- [x] Process Patterns (Error Handling, Logging) komplett

### Gap Analysis Results

**Kritische Gaps:** Keine

**Wichtige Gaps (Post-MVP):**

| Gap | Priorität | Notiz |
|-----|-----------|-------|
| CI/CD Pipeline Details | Niedrig | Für MVP manuelles Deployment OK |
| Backup-Strategie | Niedrig | PostgreSQL pg_dump initial ausreichend |
| Prometheus Monitoring | Niedrig | Dashboard-Metriken reichen für MVP |

### Architecture Completeness Checklist

**✅ Requirements Analysis**
- [x] Project context thoroughly analyzed
- [x] Scale and complexity assessed
- [x] Technical constraints identified (MT5/Wine, Single Server)
- [x] Cross-cutting concerns mapped

**✅ Architectural Decisions**
- [x] Critical decisions documented with versions
- [x] Technology stack fully specified
- [x] Integration patterns defined
- [x] Performance considerations addressed

**✅ Implementation Patterns**
- [x] Naming conventions established
- [x] Structure patterns defined
- [x] Communication patterns specified
- [x] Process patterns documented

**✅ Project Structure**
- [x] Complete directory structure defined
- [x] Component boundaries established
- [x] Integration points mapped
- [x] Requirements to structure mapping complete

### Architecture Readiness Assessment

**Overall Status:** READY FOR IMPLEMENTATION

**Confidence Level:** HOCH

**Key Strengths:**
- Klare 3-Ebenen-Architektur (Agent-Rollen → Teams → Instanzen)
- Vollständige Naming Conventions für alle Schichten
- Detaillierte Projektstruktur mit FR-Mapping
- Konsistente Patterns für Error Handling und Logging
- Bewährter Tech-Stack mit guter Dokumentation

**Areas for Future Enhancement:**
- CI/CD Pipeline Automatisierung
- Monitoring mit Prometheus/Grafana
- Backup-Automation und Recovery-Prozesse
- Load Testing für Skalierungsgrenzen

### Implementation Handoff

**AI Agent Guidelines:**
1. Folge allen architektonischen Entscheidungen exakt wie dokumentiert
2. Nutze Implementation Patterns konsistent über alle Komponenten
3. Respektiere Projektstruktur und Boundaries
4. Referenziere dieses Dokument für alle architektonischen Fragen

**First Implementation Priority:**
```bash
# Backend Setup
cd backend
uv init
uv add fastapi uvicorn sqlalchemy asyncpg alembic redis pydantic structlog langgraph langchain-anthropic aiomql python-socketio

# Frontend Setup
cd frontend
npm create vite@latest . -- --template react-ts
npm install
npx tailwindcss init -p
npx shadcn@latest init
```

---

## Architecture Completion Summary

### Workflow Completion

| Feld | Wert |
|------|------|
| **Status** | COMPLETED ✅ |
| **Schritte abgeschlossen** | 8/8 |
| **Datum** | 2025-12-01 |
| **Dokument** | `/docs/architecture.md` |

### Final Architecture Deliverables

**Architektonische Entscheidungen:**
- 15+ Kernentscheidungen dokumentiert (Tech-Stack, Patterns, Security)
- Alle Versionen verifiziert
- Vollständige Implementation Patterns

**Abgedeckte Bereiche:**

| Bereich | Status |
|---------|--------|
| Project Context Analysis | ✅ |
| Technology Stack | ✅ |
| Core Architectural Decisions | ✅ |
| Implementation Patterns | ✅ |
| Project Structure | ✅ |
| Validation | ✅ |

### Nächste Schritte

1. **Epics & Stories erstellen** – FRs in implementierbare Stories aufteilen
2. **Projekt initialisieren** – Backend + Frontend Setup ausführen
3. **MVP implementieren** – Team-System mit Paper Trading

---

## Future Architecture: Multi-Broker-Support (Post-MVP)

_Dieser Abschnitt dokumentiert die architektonischen Überlegungen für eine spätere Erweiterung auf mehrere Broker (z.B. Interactive Brokers zusätzlich zu MT5/IC Markets)._

### Motivation

- **Broker-Diversifikation:** Risikominimierung durch Verteilung auf mehrere Broker
- **Asset-Erweiterung:** IB bietet Aktien, Optionen, Futures - nicht nur Forex/CFD
- **Regulatorische Flexibilität:** Verschiedene Broker für verschiedene Jurisdiktionen

### Architektur-Entscheidung: Adapter-Pattern

**Status:** GEPLANT (Post-MVP)

**Entscheidung:** Einführung eines Broker-Abstraktions-Layers mit Adapter-Pattern

**Rationale:**
- Agents bleiben broker-agnostisch
- Neue Broker durch Implementierung der Interfaces hinzufügbar
- Minimale Änderungen an bestehender Business-Logik

### Geplante Modul-Struktur

```
backend/src/broker/
├── interfaces/
│   ├── __init__.py
│   ├── base.py               # BrokerConnector ABC, BrokerType Enum
│   ├── order_executor.py     # OrderExecutor ABC
│   └── market_data.py        # MarketDataFeed ABC
├── models/
│   ├── __init__.py
│   ├── symbol.py             # NormalizedSymbol, SymbolInfo
│   ├── order.py              # OrderRequest, OrderResult, OrderStatus
│   └── position.py           # Position, AccountInfo
├── adapters/
│   ├── __init__.py
│   ├── mt5/
│   │   ├── __init__.py
│   │   ├── connector.py      # MT5Connector (aiomql)
│   │   ├── order_executor.py
│   │   ├── market_data.py
│   │   └── symbol_mapper.py
│   └── ib/
│       ├── __init__.py
│       ├── connector.py      # IBConnector (ib_insync)
│       ├── order_executor.py
│       ├── market_data.py
│       └── symbol_mapper.py
├── factory.py                # BrokerFactory
├── symbol_mapper.py          # Zentrale Symbol-Registry
├── manager.py                # BrokerManager (Connection Pool)
└── exceptions.py             # BrokerError Hierarchy
```

### Interface-Definitionen

**BrokerConnector (Basis-Interface):**

```python
from abc import ABC, abstractmethod
from enum import Enum

class BrokerType(str, Enum):
    MT5 = "mt5"
    INTERACTIVE_BROKERS = "ib"

class BrokerCapability(str, Enum):
    HEDGING = "hedging"           # MT5: ja, IB: nein (FIFO)
    TRAILING_STOP = "trailing_stop"
    BRACKET_ORDERS = "bracket_orders"
    OCO_ORDERS = "oco_orders"

class BrokerConnector(ABC):
    broker_type: BrokerType

    @abstractmethod
    async def connect(self) -> None: ...

    @abstractmethod
    async def disconnect(self) -> None: ...

    @abstractmethod
    async def is_connected(self) -> bool: ...

    @abstractmethod
    def get_capabilities(self) -> set[BrokerCapability]: ...

    @abstractmethod
    async def get_account_info(self) -> AccountInfo: ...
```

**OrderExecutor:**

```python
class OrderExecutor(ABC):
    @abstractmethod
    async def submit_order(self, order: OrderRequest) -> OrderResult: ...

    @abstractmethod
    async def cancel_order(self, order_id: str) -> bool: ...

    @abstractmethod
    async def modify_order(self, order_id: str, modifications: OrderModification) -> OrderResult: ...

    @abstractmethod
    async def get_open_positions(self) -> list[Position]: ...

    @abstractmethod
    async def close_position(self, position_id: str, partial: Decimal | None = None) -> OrderResult: ...
```

### Kritische Broker-Unterschiede

| Aspekt | MT5/IC Markets | Interactive Brokers |
|--------|----------------|---------------------|
| **API-Typ** | aiomql (IPC zu Wine) | ib_insync (TWS Gateway) |
| **Symbol-Format** | `EURUSD` | Contract-Objekt (`EUR.USD`) |
| **Position-Modell** | Hedging (mehrere pro Symbol) | FIFO (netto pro Symbol) |
| **Trailing Stop** | Native Unterstützung | Manuell implementieren |
| **Margin-Modell** | Einfacher Hebel | Portfolio Margin / Reg T |
| **Gold-Handel** | Spot (`XAUUSD`) | Futures (`GC` auf COMEX) |

### Symbol-Normalisierung

**Zentrale Design-Entscheidung:** Kanonische Symbol-Namen im Format `BASE/QUOTE`

```python
# backend/src/broker/symbol_mapper.py
SYMBOL_REGISTRY = {
    "EUR/USD": {
        BrokerType.MT5: "EURUSD",
        BrokerType.INTERACTIVE_BROKERS: {
            "symbol": "EUR",
            "currency": "USD",
            "sec_type": "CASH",
            "exchange": "IDEALPRO"
        }
    },
    "XAU/USD": {
        BrokerType.MT5: "XAUUSD",
        BrokerType.INTERACTIVE_BROKERS: {
            "symbol": "GC",
            "sec_type": "FUT",
            "exchange": "COMEX"
            # ACHTUNG: Futures haben Verfallsdatum!
        }
    }
}
```

**MVP-Vorbereitung:** Ab sofort kanonische Symbol-Namen (`EUR/USD`) in der Datenbank speichern, nicht broker-spezifische (`EURUSD`).

### Datenmodell-Erweiterungen (Post-MVP)

**Team-Instanz:**

```python
class TeamInstance(Base):
    # ... bestehende Felder ...

    # NEU: Broker-Konfiguration
    broker_type: Mapped[BrokerType] = mapped_column(
        Enum(BrokerType),
        default=BrokerType.MT5
    )
    broker_account_id: Mapped[str | None] = mapped_column(String, nullable=True)
```

**Trade-Modell:**

```python
class Trade(Base):
    # ... bestehende Felder ...

    # Broker-Tracking
    broker_type: Mapped[BrokerType]
    broker_order_id: Mapped[str]  # Native Broker-ID

    # Symbol immer kanonisch speichern
    symbol: Mapped[str]  # "EUR/USD", nicht "EURUSD"
```

### Risk Management Anpassungen

```python
class RiskManager:
    def __init__(self, broker_capabilities: set[BrokerCapability]):
        self._capabilities = broker_capabilities

    async def validate_order(
        self,
        order: OrderRequest,
        positions: list[Position]
    ) -> ValidationResult:
        warnings = []

        # FIFO-Warnung für IB
        if BrokerCapability.HEDGING not in self._capabilities:
            existing = self._find_position(positions, order.symbol)
            if existing and existing.side != order.side:
                warnings.append(
                    f"FIFO-Broker: Order wird zuerst {existing.quantity} "
                    f"{existing.side.value} Position schließen"
                )

        # Trailing Stop Fallback
        if order.trailing_stop_pct and BrokerCapability.TRAILING_STOP not in self._capabilities:
            warnings.append(
                "Broker unterstützt kein natives Trailing Stop - "
                "wird softwareseitig simuliert"
            )

        return ValidationResult(approved=True, warnings=warnings)
```

### Factory-Pattern für Broker-Instanziierung

```python
# backend/src/broker/factory.py
class BrokerFactory:
    _ADAPTERS = {
        BrokerType.MT5: (MT5Connector, MT5OrderExecutor, MT5MarketDataFeed),
        BrokerType.INTERACTIVE_BROKERS: (IBConnector, IBOrderExecutor, IBMarketDataFeed),
    }

    @classmethod
    def create(
        cls,
        broker_type: BrokerType,
        config: BrokerConfig
    ) -> tuple[BrokerConnector, OrderExecutor, MarketDataFeed]:
        connector_cls, executor_cls, feed_cls = cls._ADAPTERS[broker_type]
        connector = connector_cls(config)
        return connector, executor_cls(connector), feed_cls(connector)
```

### Exception-Hierarchie

```python
# backend/src/broker/exceptions.py
class BrokerError(TradingError):
    """Basis für alle Broker-Fehler"""
    code = "BROKER_ERROR"

class BrokerConnectionError(BrokerError):
    code = "BROKER_CONNECTION_ERROR"

class OrderRejectedError(BrokerError):
    code = "ORDER_REJECTED"

class SymbolNotSupportedError(BrokerError):
    code = "SYMBOL_NOT_SUPPORTED"

class InsufficientMarginError(BrokerError):
    code = "INSUFFICIENT_MARGIN"
```

### Migrations-Pfad

**Phase 1 (MVP-kompatibel):**
1. Kanonische Symbol-Namen in DB verwenden
2. Agent-Layer broker-agnostisch halten
3. `mt5/` Modul wie geplant implementieren

**Phase 2 (Post-MVP):**
1. `broker/interfaces/` erstellen
2. MT5-Code in `broker/adapters/mt5/` refaktorieren
3. Alembic-Migration: `broker_type` zu `team_instances` hinzufügen

**Phase 3 (Multi-Broker):**
1. `ib_insync` Dependency hinzufügen
2. `broker/adapters/ib/` implementieren
3. Symbol-Registry erweitern
4. UI für Broker-Auswahl bei Team-Erstellung

### Neue Dependencies (Post-MVP)

```toml
# pyproject.toml
[project.optional-dependencies]
ib = ["ib_insync>=0.9.86"]
```

### Architektur-Vorteile

| Aspekt | Bewertung |
|--------|-----------|
| Agent-Layer Broker-Agnostik | ✅ Bereits geplant |
| Repository-Pattern | ✅ Abstrahiert Datenzugriff |
| Virtuelles Ledger pro Agent | ✅ Unabhängig vom Broker |
| Shadow Portfolio | ✅ Cross-Broker kompatibel |
| Service-Layer | ✅ Verwendet Interfaces |

### Offene Entscheidungen (Post-MVP)

1. **Multi-Account Support:** Ein Team pro Broker-Account oder ein Team über mehrere Accounts?
2. **Position-Synchronisation:** Echtzeit-Reconciliation zwischen Broker und DB?
3. **Margin-Aggregation:** Wie wird Margin über mehrere Broker aggregiert?
4. **Failover-Strategie:** Automatischer Broker-Wechsel bei Ausfall?

---

## Architecture Completion Summary

### Workflow Completion

| Feld | Wert |
|------|------|
| **Status** | COMPLETED ✅ |
| **Schritte abgeschlossen** | 8/8 |
| **Datum** | 2025-12-01 |
| **Dokument** | `/docs/architecture.md` |

### Final Architecture Deliverables

**Architektonische Entscheidungen:**
- 15+ Kernentscheidungen dokumentiert (Tech-Stack, Patterns, Security)
- Alle Versionen verifiziert
- Vollständige Implementation Patterns
- Multi-Broker-Erweiterungspfad dokumentiert (Post-MVP)

**Abgedeckte Bereiche:**

| Bereich | Status |
|---------|--------|
| Project Context Analysis | ✅ |
| Technology Stack | ✅ |
| Core Architectural Decisions | ✅ |
| Implementation Patterns | ✅ |
| Project Structure | ✅ |
| Validation | ✅ |
| Multi-Broker Extension (Post-MVP) | ✅ |

### Nächste Schritte

1. **Epics & Stories erstellen** – FRs in implementierbare Stories aufteilen
2. **Projekt initialisieren** – Backend + Frontend Setup ausführen
3. **MVP implementieren** – Team-System mit Paper Trading
4. **(Post-MVP)** Multi-Broker-Abstraktions-Layer implementieren

---

**Architecture Status:** READY FOR IMPLEMENTATION ✅

*Dieses Architektur-Dokument dient als Single Source of Truth für alle technischen Entscheidungen während der Implementierung.*

