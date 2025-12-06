---
epic: 001
story: 06
title: "Docker Compose für lokale Entwicklung"
status: done
story_points: 2
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

## Implementation Notes (2025-12-06)

**Story vollständig umgesetzt:**

- ✅ `docker-compose.yml` mit allen Services:
  - `backend` auf Port 8000 mit Health-Check
  - `frontend` auf Port 3000
  - `postgres` (timescale/timescaledb:latest-pg16) auf Port 5432
  - `redis` (redis:7-alpine) auf Port 6379
- ✅ `docker-compose.dev.yml` für Hot-Reload:
  - Backend mit Volume Mount und `--reload`
  - Frontend mit Volume Mount und HMR auf Port 5173
- ✅ Health-Checks für alle Services definiert
- ✅ Named Volumes: `postgres_data`, `redis_data`
- ✅ Network: `trade-network` (bridge)
- ✅ Service-Dependencies mit `condition: service_healthy`
