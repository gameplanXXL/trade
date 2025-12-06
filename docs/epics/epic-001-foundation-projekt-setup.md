# Epic 1: Foundation & Projekt-Setup ✅ COMPLETED

**Epic Goal:** Entwicklungsumgebung steht, Basis-Infrastruktur läuft, erstes Deployment möglich

**Status:** 7/7 Stories done (100%)

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

**Technical Notes:**
- Package Manager: uv (bevorzugt) oder poetry
- Python Version: 3.11+
- Settings via Pydantic Settings mit `.env` Support

**Prerequisites:** Keine

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

---

## Story 1.3: PostgreSQL + TimescaleDB Setup mit Alembic

Als Entwickler,
möchte ich eine PostgreSQL-Datenbank mit TimescaleDB und Alembic-Migrations,
damit ich Zeitreihen-Daten effizient speichern und Schema-Änderungen versionieren kann.

**Acceptance Criteria:**

**Given** das Backend-Projekt mit SQLAlchemy
**When** ich die Datenbank-Konfiguration einrichte
**Then** existiert `src/db/session.py` mit async Session Factory:
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
engine = create_async_engine(settings.database_url)
```

**And** `alembic/env.py` ist für async SQLAlchemy konfiguriert
**And** eine initiale Migration erstellt die Basis-Tabellen:
  - `users` (id, username, password_hash, created_at)
  - Aktiviert TimescaleDB Extension

**And** `docker-compose.yml` definiert PostgreSQL + TimescaleDB:
```yaml
services:
  postgres:
    image: timescale/timescaledb:latest-pg16
    environment:
      POSTGRES_DB: trading
      POSTGRES_USER: trading
      POSTGRES_PASSWORD: trading
    ports:
      - "5432:5432"
```

**And** `alembic upgrade head` läuft erfolgreich gegen Docker-DB

**Technical Notes:**
- asyncpg als DB-Driver
- Connection Pool: min=5, max=20
- TimescaleDB Extension in erster Migration aktivieren

**Prerequisites:** Story 1.1

---

## Story 1.4: Redis-Integration für Sessions und Cache

Als Entwickler,
möchte ich Redis für Session-Management und Caching,
damit ich schnellen Zugriff auf Session-Daten und temporäre Daten habe.

**Acceptance Criteria:**

**Given** das Backend-Projekt
**When** ich Redis integriere
**Then** existiert ein Redis-Client in `src/api/deps.py`:
```python
from redis.asyncio import Redis
redis_client = Redis.from_url(settings.redis_url)
```

**And** `docker-compose.yml` enthält Redis-Service:
```yaml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

**And** ein Health-Check `GET /health` prüft Redis-Verbindung
**And** Session-Operationen funktionieren:
  - `await redis.set("session:token", user_id, ex=3600)`
  - `await redis.get("session:token")`
  - `await redis.delete("session:token")`

**Technical Notes:**
- redis[hiredis] für Performance
- Connection Pool für async Operations
- Default TTL für Sessions: 24 Stunden

**Prerequisites:** Story 1.1

---

## Story 1.5: Frontend-Projekt initialisieren

Als Entwickler,
möchte ich ein React-Frontend mit Vite, Tailwind und shadcn/ui,
damit ich eine moderne, responsive UI entwickeln kann.

**Acceptance Criteria:**

**Given** ein leeres `frontend/` Verzeichnis
**When** ich das Frontend-Projekt initialisiere
**Then** existiert die Projektstruktur:
```
frontend/
├── package.json
├── vite.config.ts
├── tailwind.config.js
├── tsconfig.json
├── .env.example
└── src/
    ├── main.tsx
    ├── App.tsx
    ├── index.css
    ├── components/
    │   └── ui/           # shadcn/ui Komponenten
    ├── lib/
    │   └── utils.ts
    └── types/
```

**And** Tailwind CSS ist konfiguriert mit Custom Colors (UX Design):
```js
// tailwind.config.js
colors: {
  background: '#0a0e1a',
  surface: '#141b2d',
  border: '#1e2a47',
  success: '#10b981',
  warning: '#f59e0b',
  critical: '#ef4444',
}
```

**And** shadcn/ui ist initialisiert mit Dark-Mode Default
**And** `pnpm dev` startet den Dev-Server auf Port 5173
**And** die App zeigt "Trading Platform" als Placeholder

**Technical Notes:**
- Package Manager: pnpm
- TypeScript strict mode
- React 18 mit Vite
- Inter + JetBrains Mono Fonts (UX Design)

**Prerequisites:** Keine

---

## Story 1.6: Docker Compose für lokale Entwicklung

Als Entwickler,
möchte ich ein vollständiges Docker Compose Setup,
damit ich alle Services lokal mit einem Befehl starten kann.

**Acceptance Criteria:**

**Given** Backend und Frontend Projekte
**When** ich Docker Compose konfiguriere
**Then** existiert `docker-compose.yml` im Root:
```yaml
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    environment:
      - DATABASE_URL=postgresql+asyncpg://...
      - REDIS_URL=redis://redis:6379

  frontend:
    build: ./frontend
    ports:
      - "3000:80"

  postgres:
    image: timescale/timescaledb:latest-pg16
    # ...

  redis:
    image: redis:7-alpine
    # ...
```

**And** `docker-compose.dev.yml` für Hot-Reload:
  - Backend mit Volume Mount und `--reload`
  - Frontend mit Volume Mount und Vite HMR

**And** `docker compose up` startet alle Services
**And** Health-Checks für alle Services sind definiert

**Technical Notes:**
- Networks für Service-Isolation
- Named Volumes für DB-Persistenz
- `.env` file für Konfiguration

**Prerequisites:** Story 1.1, 1.3, 1.4, 1.5

---

## Story 1.7: Pydantic Settings und Environment Management

Als Entwickler,
möchte ich zentrale Konfiguration via Pydantic Settings,
damit alle Einstellungen typsicher und validiert sind.

**Acceptance Criteria:**

**Given** das Backend-Projekt
**When** ich Pydantic Settings implementiere
**Then** existiert `src/config/settings.py`:
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    database_url: str

    # Redis
    redis_url: str = "redis://localhost:6379"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Security
    secret_key: str
    encryption_key: str  # Fernet key

    # LLM
    anthropic_api_key: str | None = None

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
```

**And** `.env.example` dokumentiert alle Variablen
**And** Settings werden via Dependency Injection bereitgestellt
**And** Fehlende Required-Variablen verhindern App-Start mit klarer Fehlermeldung

**Technical Notes:**
- Secrets via Environment Variables, nie in Code
- Validation bei App-Start
- Type Coercion (str → int, etc.)

**Prerequisites:** Story 1.1

---

**Epic 1 Complete**

**Stories Created:** 7
**FR Coverage:** FR49 (teilweise), FR51 (teilweise), FR53 (teilweise) - Foundation für spätere vollständige Implementierung
**Technical Context Used:** Architecture Sections 2, 4, 5

---
