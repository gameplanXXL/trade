---
epic: 001
story: 04
title: "Redis-Integration für Sessions und Cache"
status: backlog
story_points: 2
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

