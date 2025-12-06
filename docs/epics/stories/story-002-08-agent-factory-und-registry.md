---
epic: 002
story: 08
title: "Agent-Factory und Registry"
status: completed
story_points: 2
covers: [FR16]
---

## Story 2.8: Agent-Factory und Registry

Als Entwickler,
möchte ich eine Factory zum Erstellen von Agenten aus Config,
damit Teams dynamisch aus YAML instanziiert werden können.

**Acceptance Criteria:**

**Given** alle Agent-Implementierungen
**When** ich die Factory implementiere
**Then** existiert `src/agents/__init__.py`:
```python
AGENT_REGISTRY = {
    "CrashDetector": CrashDetector,
    "LLMSignalAnalyst": LLMSignalAnalyst,
    "Trader": Trader,
    "RiskManager": RiskManager,
}

def create_agent(class_name: str, params: dict) -> BaseAgent:
    """Erstellt Agent-Instanz aus Config"""
    if class_name not in AGENT_REGISTRY:
        raise ValidationError(f"Unknown agent: {class_name}")
    return AGENT_REGISTRY[class_name](params)
```

**And** Team-Loader verwendet Factory für Agent-Erstellung
**And** Unbekannte Agent-Klassen geben klaren Fehler

**Technical Notes:**
- Registry ermöglicht einfache Erweiterung
- Post-MVP: LSTMAnalyst, RLAnalyst hinzufügen

**Prerequisites:** Story 2.4, 2.5, 2.6, 2.7

