# trade - Epic Breakdown

## Table of Contents

- [trade - Epic Breakdown](#table-of-contents)
  - [Overview](./overview.md)
    - [Epics Summary](./overview.md#epics-summary)
  - [Functional Requirements Inventory](./functional-requirements-inventory.md)
    - [Team-Konfiguration](./functional-requirements-inventory.md#team-konfiguration)
    - [Team-Instanz-Management](./functional-requirements-inventory.md#team-instanz-management)
    - [Agent-Rollen](./functional-requirements-inventory.md#agent-rollen)
    - [Pipeline & Regeln](./functional-requirements-inventory.md#pipeline-regeln)
    - [Trading Execution](./functional-requirements-inventory.md#trading-execution)
    - [Performance Analytics](./functional-requirements-inventory.md#performance-analytics)
    - [Dashboard - Übersicht](./functional-requirements-inventory.md#dashboard-bersicht)
    - [Dashboard - Team-Details](./functional-requirements-inventory.md#dashboard-team-details)
    - [Dashboard - Konfiguration](./functional-requirements-inventory.md#dashboard-konfiguration)
    - [Sicherheit & Datenschutz](./functional-requirements-inventory.md#sicherheit-datenschutz)
    - [Fehlerbehandlung](./functional-requirements-inventory.md#fehlerbehandlung)
  - [FR Coverage Map](./fr-coverage-map.md)
  - [Epic-Struktur mit technischem Kontext](./epic-struktur-mit-technischem-kontext.md)
  - [Epic 001: Foundation & Projekt-Setup](./epic-001-foundation-projekt-setup.md)
  - [Epic 002: Team-System & Agent-Rollen](./epic-002-team-system-agent-rollen.md)
  - [Epic 003: Pipeline-Execution & Override-Engine](./epic-003-pipeline-execution-override-engine.md)
  - [Epic 004: MT5-Integration & Paper Trading](./epic-004-mt5-integration-paper-trading.md)
  - [Epic 005: Team-Instanz-Management](./epic-005-team-instanz-management.md)
  - [Epic 006: Performance Analytics](./epic-006-performance-analytics.md)
  - [Epic 007: Dashboard - Übersicht & Real-time](./epic-007-dashboard-uebersicht-real-time.md)
  - [Epic 008: Dashboard - Details & Konfiguration](./epic-008-dashboard-details-konfiguration.md)
  - [Epic 009: Authentifizierung & Sicherheit](./epic-009-authentifizierung-sicherheit.md)

## Projekt-Metriken

| Metrik | Wert |
|--------|------|
| **Epics** | 9 |
| **Stories** | 49 |
| **Story Points** | 156 |
| **Ø Story Points** | 3.2 |

## Referenzen

- [Definition of Done](./definition-of-done.md)
- [FR Coverage Map](./fr-coverage-map.md)
- [Stories-Verzeichnis](./stories/)

## Stories

Stories werden als separate Dateien im `stories/` Ordner verwaltet.

**Dateinamenskonvention:** `story-XXX-YY-beschreibung.md`
- XXX = Epic-Nummer (dreistellig)
- YY = Story-Nummer (zweistellig)

**Story Frontmatter:**
```yaml
---
epic: 001
story: 01
title: "Story Title"
status: backlog
story_points: 3
covers: [FR1, FR2]
---
```
