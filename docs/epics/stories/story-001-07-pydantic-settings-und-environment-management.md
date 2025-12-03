---
epic: 001
story: 07
title: "Pydantic Settings und Environment Management"
status: backlog
story_points: 2
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

