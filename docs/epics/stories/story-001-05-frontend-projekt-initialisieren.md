---
epic: 001
story: 05
title: "Frontend-Projekt initialisieren"
status: backlog
story_points: 3
---

## Story 1.5: Frontend-Projekt initialisieren

Als Entwickler,
möchte ich ein React-Frontend mit Vite, Tailwind und shadcn/ui,
damit ich eine moderne, responsive UI entwickeln kann.

**Acceptance Criteria:**

**Given** ein leeres `frontend/` Verzeichnis
**When** ich das Frontend-Projekt initialisiere
**Then** existiert die Projektstruktur:
```
frontend/
├── package.json
├── vite.config.ts
├── tailwind.config.js
├── tsconfig.json
├── .env.example
└── src/
    ├── main.tsx
    ├── App.tsx
    ├── index.css
    ├── components/
    │   └── ui/           # shadcn/ui Komponenten
    ├── lib/
    │   └── utils.ts
    └── types/
```

**And** Tailwind CSS ist konfiguriert mit Custom Colors (UX Design):
```js
// tailwind.config.js
colors: {
  background: '#0a0e1a',
  surface: '#141b2d',
  border: '#1e2a47',
  success: '#10b981',
  warning: '#f59e0b',
  critical: '#ef4444',
}
```

**And** shadcn/ui ist initialisiert mit Dark-Mode Default
**And** `pnpm dev` startet den Dev-Server auf Port 5173
**And** die App zeigt "Trading Platform" als Placeholder

**Technical Notes:**
- Package Manager: pnpm
- TypeScript strict mode
- React 18 mit Vite
- Inter + JetBrains Mono Fonts (UX Design)

**Prerequisites:** Keine

