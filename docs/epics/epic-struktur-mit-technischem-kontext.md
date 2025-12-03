# Epic-Struktur mit technischem Kontext

## Epic 1: Foundation & Projekt-Setup
**User Value Statement:** Entwicklungsumgebung steht, Basis-Infrastruktur läuft, erstes Deployment möglich

**PRD Coverage:** FR49 (teilweise), FR51 (teilweise), FR53 (teilweise)

**Technischer Kontext (Architecture):**
- Backend: FastAPI + uvicorn, SQLAlchemy 2.0 + asyncpg, Alembic für Migrations
- Frontend: React 18 + Vite, Tailwind CSS + shadcn/ui, TypeScript strict
- DB: PostgreSQL 16 + TimescaleDB Extension, Redis 7
- Docker Compose für lokale Entwicklung
- Strukturiertes Logging mit structlog (JSON-Format)
- Pydantic Settings für Configuration Management
- Exception-Hierarchie (`TradingError`, `MT5ConnectionError`, etc.)

**UX Integration:** Projekt-Skeleton ermöglicht alle späteren UI-Komponenten

**Dependencies:** Keine

---

## Epic 2: Team-System & Agent-Rollen
**User Value Statement:** User kann ein Team-Template laden und die Agent-Rollen sehen, die darin definiert sind

**PRD Coverage:** FR1, FR2, FR3, FR4, FR5, FR12, FR13, FR14, FR15, FR16

**Technischer Kontext (Architecture):**
- `teams/loader.py` - YAML-Parser mit PyYAML
- `teams/schemas.py` - Pydantic Models für Team-Konfiguration
- `agents/base.py` - BaseAgent Abstract Class
- Agent-Klassen: `CrashDetector`, `LLMSignalAnalyst`, `Trader`, `RiskManager`
- LangChain Wrappers für LLM-Integration (`langchain_anthropic.ChatAnthropic`)
- `team_templates/conservative_llm.yaml` als erstes Template

**UX Integration:** Basis für Team-Template-Auswahl im Dashboard (Epic 8)

**Dependencies:** Epic 1

---

## Epic 3: Pipeline-Execution & Override-Engine
**User Value Statement:** User kann eine Team-Pipeline starten und sieht, wie Agenten sequenziell arbeiten; Override-Regeln greifen bei kritischen Situationen

**PRD Coverage:** FR17, FR18, FR19, FR20, FR21, FR22

**Technischer Kontext (Architecture):**
- `teams/pipeline.py` - Sequential Pipeline Executor
- `teams/override.py` - Priority-basierte Override-Rule-Engine
- LangGraph `StateGraph` für Agent-Orchestrierung
- Agent-Status-Enum: `NORMAL`, `WARNING`, `CRASH`
- `db/models/agent_decision.py` - Decision Audit-Log
- Logging: `log.info("pipeline_step_completed", step="crash_detector", status="NORMAL")`

**UX Integration:** Timeline-Anzeige der Agent-Aktionen (Epic 8, FR42)

**Dependencies:** Epic 2

---

## Epic 4: MT5-Integration & Paper Trading
**User Value Statement:** User kann sich mit MT5 verbinden, Kursdaten empfangen und simulierte Trades im Paper-Modus ausführen

**PRD Coverage:** FR23, FR24, FR25, FR26, FR27, FR28, FR52

**Technischer Kontext (Architecture):**
- `mt5/connector.py` - aiomql Wrapper mit Auto-Reconnect Logic
- `mt5/market_data.py` - Real-time Price Feed, TimescaleDB Hypertable
- `mt5/orders.py` - Order Management, Trailing Stoploss Implementation
- Paper Trading Simulation (kein echtes MT5-Order)
- Virtuelle Buchführung: `team_instances.current_budget`, `trades` Tabelle
- Symbol-Normalisierung: Kanonisch `EUR/USD`, MT5-spezifisch `EURUSD`

**UX Integration:** Live-Kursdaten für Charts (Epic 7)

**Dependencies:** Epic 1

---

## Epic 5: Team-Instanz-Management
**User Value Statement:** User kann Team-Instanzen erstellen, starten, stoppen und pausieren; Instanzen werden persistent gespeichert

**PRD Coverage:** FR6, FR7, FR8, FR9, FR10, FR11

**Technischer Kontext (Architecture):**
- `db/models/team.py` - TeamInstance SQLAlchemy Model
- `db/repositories/team_repo.py` - CRUD Operations (async)
- `api/routes/teams.py` - REST Endpoints
  - `POST /api/teams` - Erstellen
  - `GET /api/teams` - Liste
  - `GET /api/teams/{id}` - Details
  - `PATCH /api/teams/{id}/start` - Starten
  - `PATCH /api/teams/{id}/pause` - Pausieren
  - `DELETE /api/teams/{id}` - Stoppen
- Status-Enum: `active`, `paused`, `stopped`
- Symbole als JSON-Array, Budget als Decimal

**UX Integration:** TeamCreate-Formular, TeamList-Komponente (Epic 8)

**Dependencies:** Epic 2, Epic 4

---

## Epic 6: Performance Analytics
**User Value Statement:** User sieht Trading-Metriken (P/L, Win-Rate, Sharpe Ratio, Drawdown) für jede Team-Instanz

**PRD Coverage:** FR29, FR30, FR31, FR32, FR33, FR34, FR35

**Technischer Kontext (Architecture):**
- `services/analytics.py` - Performance-Berechnungen
  - `calculate_total_pnl(team_id)` - Gesamt-P/L
  - `calculate_win_rate(team_id)` - Gewinn-Quote
  - `calculate_sharpe_ratio(team_id)` - Risikoadjustierte Rendite
  - `calculate_max_drawdown(team_id)` - Maximaler Rückgang
- `db/repositories/analytics_repo.py` - TimescaleDB-Aggregationen
- TimescaleDB Hypertables: `trades` (1 Woche), `performance_metrics` (1 Tag)
- Agent-Aktivitäts-Tracking: `agent_decisions` mit Typ (signal, warning, rejection)

**UX Integration:**
- MetricsDisplay-Komponente mit Trading-Kennzahlen
- Performance-Charts mit TradingView Lightweight Charts
- Farbcodierung: Grün >0%, Rot <0%, Dunkelrot <-5%

**Dependencies:** Epic 4, Epic 5

---

## Epic 7: Dashboard - Übersicht & Real-time
**User Value Statement:** User öffnet Dashboard und sieht alle Team-Instanzen mit Status, P/L und Warnungen in Echtzeit

**PRD Coverage:** FR36, FR37, FR38, FR39

**Technischer Kontext (Architecture):**
- `api/websocket/handler.py` - python-socketio Handler
- `api/websocket/events.py` - Event-Definitionen
  - `team:status_changed` - Status-Updates
  - `trade:executed` - Neue Trades
  - `alert:warning` - Drawdown-Warnungen
  - `alert:crash` - Crash-Detection
- Redis Pub/Sub für Event-Distribution
- Frontend: Socket.io Client, Zustand Stores

**UX Integration (UX Design):**
- `HealthBar` - Traffic-Light (Grün/Gelb/Rot) mit Badge-Count
- `InstanceCard` - Proportionale Größe basierend auf Budget
- 3-Tier P/L-Farbcodierung: `#10b981` (Grün), `#ef4444` (Rot), Dunkelrot für <-5%
- Auto-Sorting: Kritische Instanzen automatisch oben
- Dark-Mode Default: Background `#0a0e1a`, Surface `#141b2d`

**Dependencies:** Epic 5, Epic 6

---

## Epic 8: Dashboard - Details & Konfiguration
**User Value Statement:** User kann Instanz-Details einsehen (Trade-Historie, Timeline, Charts) und neue Instanzen über die UI erstellen

**PRD Coverage:** FR40, FR41, FR42, FR43, FR44, FR45, FR46, FR47, FR48

**Technischer Kontext (Architecture):**
- `features/teams/TeamDetail.tsx` - Detail-Ansicht
- `features/teams/TeamCreate.tsx` - Erstellungs-Formular
- `features/analytics/TradeHistory.tsx` - TanStack Table mit Sortierung/Pagination
- REST API Actions:
  - `POST /api/teams` mit Body: `{ template, symbols, budget, mode }`
  - `PATCH /api/teams/{id}/pause`
  - `DELETE /api/teams/{id}`

**UX Integration (UX Design):**
- Bottom-Sheet/Modal für Details (Mobile-optimiert)
- Timeline-Komponente für Agent-Aktionen (Signale, Warnungen, Ablehnungen)
- `ConfirmationModal` für kritische Aktionen mit Smart Safeguard
- Swipe-to-Reveal für Quick Actions auf Mobile
- Touch-Targets: Minimum 48x48px

**Dependencies:** Epic 7

---

## Epic 9: Authentifizierung & Sicherheit
**User Value Statement:** User kann sich einloggen; Credentials sind sicher gespeichert

**PRD Coverage:** FR49, FR50, FR51, FR54

**Technischer Kontext (Architecture):**
- `api/routes/auth.py` - Login/Logout Endpoints
  - `POST /api/auth/login` - Session erstellen
  - `POST /api/auth/logout` - Session löschen
- `services/credentials.py` - Fernet Encryption für MT5/LLM-Keys
- Redis Sessions: `session:{token}` → User-ID
- Cookie-basierte Auth mit `httponly`, `secure` Flags
- LLM-API Retry-Logic: 3 Versuche mit exponential backoff
- Logging: Keine Secrets in Logs (`structlog` mit Filtering)

**UX Integration:**
- `features/auth/LoginForm.tsx` - Einfaches Login-Formular
- Session-Timeout-Handling im Frontend

**Dependencies:** Epic 1

---
