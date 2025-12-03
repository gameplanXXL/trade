---
epic: 001
story: 03
title: "PostgreSQL + TimescaleDB Setup mit Alembic"
status: done
story_points: 3
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

## Tasks

- [x] Task 1: Story-Status auf in-progress setzen
- [x] Task 2: docker-compose.yml mit PostgreSQL/TimescaleDB erstellen
- [x] Task 3: src/db/session.py mit async Engine/Session erstellen
- [x] Task 4: alembic/env.py für async SQLAlchemy konfigurieren
- [x] Task 5: Initiale Migration mit users-Tabelle und TimescaleDB erstellen
- [x] Task 6: Docker starten und Migration testen

## Dev Agent Record

### Agent Model Used
Claude Opus 4.5 (claude-opus-4-5-20251101)

### Completion Notes
Alle Acceptance Criteria erfüllt:
- ✅ `src/db/session.py` mit async Engine und Session Factory
- ✅ `alembic/env.py` für async SQLAlchemy konfiguriert
- ✅ Initiale Migration erstellt users-Tabelle und aktiviert TimescaleDB
- ✅ `docker-compose.yml` mit PostgreSQL + TimescaleDB + Redis
- ✅ `alembic upgrade head` erfolgreich ausgeführt

### Verified Database State
```
Tables: users, alembic_version
TimescaleDB Extension: v2.24.0 aktiviert
Users Table: id, username, password_hash, created_at
Index: ix_users_username (unique)
```

## File List
- `docker-compose.yml` - PostgreSQL/TimescaleDB + Redis Container (NEU)
- `backend/src/db/__init__.py` - Database Modul (NEU)
- `backend/src/db/session.py` - Async Engine und Session Factory (NEU)
- `backend/src/db/models.py` - SQLAlchemy User Model (NEU)
- `backend/alembic/env.py` - Async Alembic Konfiguration (NEU)
- `backend/alembic/script.py.mako` - Migration Template (NEU)
- `backend/alembic/versions/20251203_0001_initial_schema.py` - Initiale Migration (NEU)

## Change Log
- 2025-12-03: Story gestartet, Status: in-progress
- 2025-12-03: Story abgeschlossen, Status: done

