# Trade Backend

Multi-Agent Day-Trading Platform Backend

## Setup

```bash
# Install dependencies
uv sync

# Run development server
uv run uvicorn src.main:app --reload
```

## Health Check

```bash
curl http://localhost:8000/health
# Response: {"status": "ok"}
```
