---
stepsCompleted: [1, 2, 3]
inputDocuments:
  - "/docs/prd.md"
  - "/docs/analysis/research/technical-ki-trading-plattform-research-2025-12-01.md"
workflowType: 'architecture'
lastStep: 3
project_name: 'trade'
user_name: 'Christian'
date: '2025-12-01'
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

