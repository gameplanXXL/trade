---
epic: 009
story: 05
title: "Secrets-Filterung in Logs"
status: backlog
story_points: 2
covers: [FR51]
---

## Story 9.5: Secrets-Filterung in Logs

Als Operator,
möchte ich, dass keine Secrets in Logs erscheinen,
damit Credentials nicht versehentlich exponiert werden.

**Acceptance Criteria:**

**Given** structlog-Setup
**When** ich Secret-Filtering implementiere
**Then** existiert in `src/core/logging.py`:
```python
SENSITIVE_KEYS = {'password', 'api_key', 'secret', 'token', 'authorization'}

def filter_sensitive_data(_, __, event_dict: dict) -> dict:
    """Ersetzt sensitive Werte mit ***REDACTED***"""
    for key in list(event_dict.keys()):
        if any(sensitive in key.lower() for sensitive in SENSITIVE_KEYS):
            event_dict[key] = "***REDACTED***"
    return event_dict

structlog.configure(
    processors=[
        filter_sensitive_data,
        structlog.processors.JSONRenderer(),
    ]
)
```

**And** Gefilterte Keys:
  - `password`, `passwd`
  - `api_key`, `apikey`
  - `secret`
  - `token`
  - `authorization`

**And** Test verifiziert Filterung

**Technical Notes:**
- Case-insensitive Matching
- Recursive für nested Dicts (optional)
- Auch in Exception-Messages filtern

**Prerequisites:** Story 1.2

