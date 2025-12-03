---
epic: 001
story: 03
title: "PostgreSQL + TimescaleDB Setup mit Alembic"
status: backlog
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

