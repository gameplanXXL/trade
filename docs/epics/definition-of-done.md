# Definition of Done (DoD)

Diese Kriterien müssen erfüllt sein, bevor eine Story als "done" markiert wird.

---

## Story-Level DoD

### Code-Qualität

- [ ] **Code implementiert** - Alle Acceptance Criteria erfüllt
- [ ] **Code Review** - Self-Review durchgeführt (Solo-Projekt)
- [ ] **Naming Conventions** - Gemäß CLAUDE.md (snake_case, PascalCase, etc.)
- [ ] **Type Hints** - Python: Vollständige Type Annotations
- [ ] **TypeScript Strict** - Frontend: Keine `any` Types

### Testing

- [ ] **Unit Tests** - Neue Funktionalität getestet (min. Happy Path)
- [ ] **Tests grün** - `pytest` / `pnpm test` erfolgreich
- [ ] **Keine Regressionen** - Bestehende Tests weiterhin grün

### Dokumentation

- [ ] **Docstrings** - Öffentliche Funktionen/Klassen dokumentiert
- [ ] **Code-Kommentare** - Nur wo Logik nicht selbsterklärend

### Integration

- [ ] **Lint erfolgreich** - `ruff check` / `pnpm lint` ohne Fehler
- [ ] **Build erfolgreich** - Anwendung startet ohne Fehler
- [ ] **Manuelle Verifizierung** - Feature funktioniert wie erwartet

### Git

- [ ] **Commit gepusht** - Gemäß CLAUDE.md Git-Workflow
- [ ] **Commit-Message** - Beschreibend, auf Deutsch

---

## Epic-Level DoD

- [ ] **Alle Stories done** - Jede Story im Epic erfüllt Story-DoD
- [ ] **Integration getestet** - Stories arbeiten zusammen
- [ ] **Retrospective** - Lessons Learned dokumentiert (optional)

---

## Story-Status Workflow

```
backlog → drafted → ready-for-dev → in-progress → review → done
```

| Status | Bedeutung |
|--------|-----------|
| `backlog` | Story existiert nur in Epic-Datei |
| `drafted` | Story-Datei erstellt |
| `ready-for-dev` | Story approved, kann implementiert werden |
| `in-progress` | Entwicklung läuft |
| `review` | Implementierung fertig, wartet auf Review |
| `done` | DoD erfüllt, Story abgeschlossen |

---

## Ausnahmen

### MVP-Vereinfachungen

Für das MVP gelten folgende Vereinfachungen:

- **Test Coverage** - Fokus auf kritische Pfade, nicht 100%
- **Documentation** - Inline-Docs ausreichend, keine separate API-Docs
- **Error Handling** - Graceful Degradation, nicht alle Edge Cases

### Technische Schulden

Wenn eine Story mit bekannten Einschränkungen abgeschlossen wird:

1. TODO-Kommentar im Code mit Erklärung
2. Issue/Notiz für Post-MVP erstellen
3. In Retrospective dokumentieren

---

## Checkliste für Entwickler

Vor dem Markieren als "done":

```bash
# Backend
cd backend
uv run ruff check .
uv run pytest
uv run uvicorn src.main:app  # Startet ohne Fehler?

# Frontend
cd frontend
pnpm lint
pnpm test
pnpm build  # Build erfolgreich?

# Git
git add -A
git commit -m "Story X.Y: Beschreibung"
git push
```
