---
stepsCompleted: [1, 2, 3, 4, 5]
inputDocuments:
  - "/home/cneise/Project/trade/docs/prd.md"
  - "/home/cneise/Project/trade/docs/analysis/product-brief-v1.md"
  - "/home/cneise/Project/trade/docs/analysis/research/technical-ki-trading-plattform-research-2025-12-01.md"
workflowType: 'ux-design'
lastStep: 5
project_name: 'trade'
user_name: 'Christian'
date: '2025-12-01'
---

# UX Design Specification trade

**Author:** Christian
**Date:** 2025-12-01

---

## Executive Summary

### Project Vision

Eine adaptive Multi-Agent Day-Trading-Plattform, die Team-basierte KI-Systeme orchestriert. Teams bestehen aus spezialisierten Rollen (Crash Detector, Signal Analyst, Trader, Risk Manager), die über Pipelines und Override-Regeln zusammenarbeiten. Jedes Team kann mehrere Instanzen haben, die mit unterschiedlichen Parametern (Symbole, Budget, Paper/Live) parallel laufen. Der Fokus liegt auf Portfolio-Performance-Überwachung mit Trading-Standard-Metriken.

### Target Users

**Christian (Solo Operator)** – Expert-Level Technical User
- Braucht schnellen Gesundheits-Check aller Team-Instanzen (Morgen-Routine: 5 Minuten)
- Muss kritische Situationen (Drawdown, Crashes) sofort erkennen ohne Push-Notifications
- Interveniert selten, aber wenn nötig: schnelle Emergency-Actions (Positionen schließen)
- Nutzt Web-Dashboard auf Desktop und Mobile (responsive design kritisch)

### Key Design Challenges

1. **Information Density**: Bis zu 20 Team-Instanzen mit je Portfolio-Metriken auf einem Screen – ohne Überladung
2. **Critical Alert Visibility**: Drawdown <-5% und Crash-Warnings müssen sofort ins Auge springen
3. **Mobile Constraints**: Dieselbe Information-Dichte und Emergency-Actions auf kleineren Screens
4. **Real-time Updates**: Dashboard muss Live-Status reflektieren ohne manuelle Refreshes

### Design Opportunities

1. **Mission Control Aesthetic**: Trading-Terminal-Look (Bloomberg/Professional Tools) mit klarer Farbcodierung
2. **Progressive Disclosure**: Übersicht zeigt nur P/L + Status → Drill-Down für Details (Sharpe, Trades, Timeline)
3. **Emergency-First UX**: One-Click-Actions für kritische Situationen mit Smart-Safeguards
4. **Visual Hierarchy**: "Gesunde" Instanzen bleiben ruhig, Probleme dominieren visuell (Farbe, Größe, Animation)

---

## Core User Experience

### Defining Experience

**Kern-Erfahrung: Portfolio Performance Comparison Dashboard**

Das zentrale Nutzererlebnis ist der **Performance-Vergleich zwischen Team-Instanzen** mit visueller Darstellung der Budget-Evolution. Der User öffnet das Dashboard und sieht auf einen Blick:
1. Welche Instanzen profitabel sind (Grün/Rot-Codierung)
2. Wie das System Budget automatisch umverteilt (Kartengrößen proportional zu Budget)
3. Wo kritische Situationen existieren (visuelle Priorität für <-5% Drawdown)

Die Instanz-Übersicht ist die kritischste Interaktion – sie muss in <2 Sekunden den vollständigen Systemstatus kommunizieren.

### Platform Strategy

**Responsive Progressive Web App (PWA)**

- **Eine Codebase** für Desktop und Mobile mit responsive breakpoints
- **Desktop-First Design** (primäre Nutzung), mobile-optimiert für unterwegs
- **Installierbar** als PWA für App-like Experience ohne Store-Abhängigkeit
- **Online-Only** – Trading-Daten erfordern Live-Verbindung, keine Offline-Funktionalität
- **WebSocket Live-Updates** – Dashboard aktualisiert sich automatisch ohne Manual Refresh
- **Touch + Mouse optimiert** – Touch-Gestures auf Mobile (Swipe), Hover-States auf Desktop

### Effortless Interactions

**1. "Ist alles OK?" Status (Zero-Thought Recognition)**
- **Aggregierte Health-Bar** oben: Grün (alle OK), Gelb (Warnungen), Rot (kritisch <-5%)
- **Auto-Sorting**: Kritische Instanzen automatisch oben, dann nach P/L sortiert
- **Visual Hierarchy**: Probleme dominieren (größer, animiert), gesunde Instanzen zurückhaltend

**2. Performance-Vergleich (Scanning Efficiency)**
- **Proportionale Karten-Größe**: Budget visuell als Kartengröße → Erfolgreiche = größer
- **P/L prominent**: Große Zahlen, 3-Stufen-Farbcode (Grün >0%, Rot <0%, Dunkelrot <-5%)
- **Quick-Filters**: "Live/Paper", "Probleme", "Top Performer" – Ein-Klick-Filterung

**3. Emergency Actions (Speed + Safety)**
- **One-Click "Close Positions"**: Prominent in jeder Instanz-Karte, immer sichtbar
- **Smart Safeguard**: Modal mit Zusammenfassung (X Positionen, Y€ Exposure) + Confirm
- **Mobile Swipe-Actions**: Links-Swipe = Quick Actions (Close, Pause, Details)

**4. Seamless Cross-Device**
- **Responsive Layout**: Desktop = Grid (3-4 Spalten), Mobile = Vertikale Liste
- **State Sync**: Dashboard-Filter und View-State über Devices synchronisiert
- **Touch-Optimized Targets**: Mobile = 48px Mindestgröße, großzügige Abstände

### Critical Success Moments

**1. Der "Aha!"-Moment: Budget-Evolution Visual**
Beim ersten Öffnen sieht der User sofort: Erfolgreiche Instanzen haben **größere Karten** → System optimiert sich selbst. Die visuell proportionale Budget-Darstellung macht das evolutionäre Prinzip intuitiv erlebbar.

**2. Kritische Warnung erkennen (<2 Sekunden)**
Drawdown <-5% muss sofort ins Auge springen: Dunkelrote Karte, größer als andere, optional pulsierend. User öffnet Dashboard und weiß **ohne zu lesen**, dass es ein Problem gibt.

**3. Emergency Response (<5 Sekunden)**
Von "Problem erkannt" zu "Positionen geschlossen": Kritische Karte → One-Click Close → Smart Confirm → Ausgeführt. Muss auf Mobile genauso schnell funktionieren wie auf Desktop.

**4. Täglicher Morgen-Check (5 Minuten-Ziel)**
User öffnet Dashboard → Health-Bar checken (3 Sek) → Instanzen scannen (30 Sek) → Optional: 2-3 Details öffnen (2 Min) → Schließen. Effizienz durch Auto-Sorting und Visual Hierarchy.

### Experience Principles

**1. Status-First, Details-On-Demand**
Übersicht zeigt nur kritische Metriken (P/L, Budget, Status). Alle anderen Daten (Sharpe Ratio, Trade-Historie, Agent-Timeline) nur auf Drill-Down. Progressive Disclosure verhindert Information Overload.

**2. Visual Darwinism**
Erfolg und Misserfolg sind visuell sofort erkennbar. Budget-Proportionen, Farbcodierung und Auto-Sorting erzählen die Geschichte ohne Zahlen lesen zu müssen. Das evolutionäre Prinzip wird zur visuellen Sprache.

**3. Emergency-Ready**
Kritische Actions (Positionen schließen, Pause) sind immer einen Klick entfernt, aber mit Smart Safeguards geschützt. Balance zwischen Geschwindigkeit und Fehlerprävention.

**4. Platform-Agnostic Efficiency**
Dieselben Core-Tasks müssen auf Desktop und Mobile gleich effizient sein. Responsive Design ist nicht nur Layout-Anpassung, sondern Interaction-Pattern-Optimierung pro Device.

---

## Desired Emotional Response

### Primary Emotional Goals

**1. Gelassenheit & Kontrolle (Calm Confidence)**
Der User soll sich sicher fühlen, dass das System läuft und er alles im Griff hat, ohne permanent überwachen zu müssen. Das Gegenteil von ständiger Angst, etwas zu verpassen oder die Kontrolle zu verlieren.

**2. Vertrauen durch Transparenz (Trust through Visibility)**
Der User soll verstehen, was passiert – Budget-Umverteilung, Degradierungen, Performance-Entwicklung. "Das System trifft gute Entscheidungen, und ich kann nachvollziehen warum." Kein Black-Box-Gefühl.

**3. Responsive Power (Emergency Readiness)**
Bei Problemen: Sofortige Handlungsfähigkeit. "Wenn ich eingreifen muss, kann ich das schnell und sicher tun." Gegenteil von Hilflosigkeit in kritischen Situationen.

### Emotional Journey Mapping

**Morgen-Check (Normal-Zustand):**
Gefühl: **Bestätigung** ("Alles läuft wie erwartet")
- Dashboard öffnen → Grüne Health-Bar sehen → Instanzen scannen → Zufriedenheit → Dashboard schließen

**Problem-Erkennung:**
Gefühl: **Alert, aber nicht Panik**
- Dashboard öffnen → Rote Warnung sofort sichtbar → Sofortiges Verständnis was los ist → Handlungsfähigkeit spüren

**Nach Intervention:**
Gefühl: **Erfolgreich gehandelt** ("Problem gelöst, System stabilisiert")
- Positionen geschlossen → Bestätigung erhalten → Entspannung → Vertrauen in eigene Reaktionsfähigkeit

**Erfolg-Moment (Budget-Evolution):**
Gefühl: **Faszination** ("Das System optimiert sich selbst!")
- Größere Karten für profitable Instanzen sehen → Stolz auf das System → Vertrauen in den Algorithmus

### Micro-Emotions

| Situation | Gewünschte Emotion | Zu vermeidende Emotion |
|-----------|-------------------|------------------------|
| Dashboard-Öffnen | Ruhe, Übersicht | Überwältigung, Verwirrung |
| Instanzen-Scan | Effizienz, Klarheit | Frustration, Informations-Overload |
| Kritische Warnung | Fokussierte Aufmerksamkeit | Panik, Hilflosigkeit |
| Emergency Action | Schnelle Kontrolle | Angst vor Fehlklick |
| Budget-Evolution sehen | Zufriedenheit, Vertrauen | Skepsis gegenüber Algorithmus |

### Design Implications

**Gelassenheit durch Visual Hierarchy:**
- Gesunde Instanzen bleiben visuell zurückhaltend mit ruhigen Farben
- Nur Probleme "schreien" visuell durch Farbe, Größe und optional Animation
- User fühlt sich nicht ständig in Alarmbereitschaft, sondern kann entspannt scannen

**Vertrauen durch Datentransparenz:**
- Budget-Größe ist visuell proportional zu Kartengrößen
- Timeline zeigt Entscheidungshistorie (Degradierungen, Budget-Anpassungen)
- Trading-Metriken folgen Standards (Sharpe Ratio, Drawdown, Win Rate)
- User versteht "warum" das System so handelt, nicht nur "was" es tut

**Responsive Power durch One-Click + Safeguard:**
- Emergency-Buttons sind immer sichtbar und prominent platziert
- Smart Confirmation mit Zusammenfassung (X Positionen, Y€ Exposure) verhindert Panik-Klicks
- Mobile Actions genauso schnell verfügbar wie auf Desktop
- User fühlt sich handlungsfähig ohne Angst vor irreversiblen Fehlern

**Calm Efficiency durch Progressive Disclosure:**
- Übersicht zeigt minimal: P/L + Status + Budget
- Detaillierte Daten (Sharpe Ratio, Trade-Historie, Agent-Timeline) nur auf Anfrage
- Auto-Sorting nach Kritikalität reduziert Such-Aufwand
- User kann schnell scannen ohne Overwhelm

### Emotional Design Principles

**1. "Set it and Trust it"**
Das System soll sich selbsterklärend gut anfühlen. User öffnet Dashboard, sieht grüne Ampel und Erfolgs-Pattern (große Karten = profitable Instanzen), schließt beruhigt wieder. Vertrauen entsteht durch konsistente, positive Erfahrungen.

**2. "Alert without Alarm"**
Probleme kommunizieren Dringlichkeit ohne Panik zu erzeugen. Rote Farbe und klare Zahlen, aber kein blinkendes Chaos oder aggressive Animationen. User wird aufmerksam gemacht und behält dabei die Kontrolle.

**3. "Understand the Why"**
Jede System-Entscheidung (Budget-Umverteilung, Degradierung, Pause) ist nachvollziehbar. Timelines, Metriken und Historie geben Kontext. User vertraut, weil er versteht – nicht blind, sondern informiert.

**4. "Fast when it Matters"**
Im Notfall: Zero Friction zu kritischen Actions. Ein Klick zu "Positionen schließen", aber mit intelligentem Safeguard der Fehlklicks verhindert. User fühlt sich mächtig und handlungsfähig, nicht ängstlich oder gehemmt.

---

## UX Pattern Analysis & Inspiration

### Inspiring Products Analysis

**1. Bloomberg Terminal / TradingView**
- **Problem gelöst**: Information-Dense Financial Dashboards ohne Overwhelm
- **UX-Erfolg**: Hierarchische Informationsarchitektur – kritische Daten prominent, Details on-demand
- **Visuelle Strategie**: Professionelle Dark-Mode-Ästhetik, Farbcodierung (Grün=Gewinn, Rot=Verlust) ist universell verständlich
- **Innovative Patterns**: Multi-Panel-Layouts mit anpassbaren Widgets, Real-time Updates ohne Performance-Einbußen

**2. Grafana / Datadog Monitoring Dashboards**
- **Problem gelöst**: Complex System Monitoring mit sofortiger Problem-Erkennung
- **UX-Erfolg**: Health-Status-Indikatoren auf oberster Ebene (Ampel-System), automatisches Alert-Routing
- **Visuelle Strategie**: Traffic-Light-Patterns (Grün/Gelb/Rot), progressive Disclosure von Metrics
- **Innovative Patterns**: Time-Series-Visualisierung, Threshold-based Alerts mit visueller Klarheit

**3. Stripe Dashboard**
- **Problem gelöst**: Komplexe Finanz-Daten für technische User zugänglich machen
- **UX-Erfolg**: Klarheit durch Weißraum, fokussierte Datenvisualisierung, elegante Drill-Downs
- **Visuelle Strategie**: Minimal aber informativ, große Zahlen für Key Metrics, subtile Animationen
- **Innovative Patterns**: Inline-Editing, Smart-Defaults, Progressive Onboarding

### Transferable UX Patterns

**Navigation Patterns:**

**1. Dashboard-Centric Architecture (Bloomberg/Grafana)**
- **Anwendung**: Hauptseite = Instanz-Übersicht, Sidebar für Navigation zu Settings/History
- **Warum**: User verbringen 80% der Zeit im Dashboard – es sollte die primäre Navigation sein
- **Adaption**: Desktop = Persistent Sidebar, Mobile = Bottom Navigation oder Hamburger

**2. Multi-Level Drill-Down (TradingView/Stripe)**
- **Anwendung**: Übersicht → Instanz-Karte → Detailansicht → Trade-Historie
- **Warum**: Progressive Disclosure reduziert Overwhelm, erfüllt "Status-First, Details-On-Demand"
- **Adaption**: Breadcrumbs für Navigation zurück, schnelle Modal-Overlays statt Full-Page-Transitions

**Interaction Patterns:**

**1. Traffic-Light Health Indicators (Grafana)**
- **Anwendung**: Aggregierte Health-Bar (Grün/Gelb/Rot) ganz oben im Dashboard
- **Warum**: Zero-Thought Recognition – User sieht sofort "Alles OK" vs. "Problem"
- **Adaption**: + Badge mit Anzahl kritischer Instanzen bei Rot/Gelb

**2. Contextual Quick-Actions (Stripe)**
- **Anwendung**: Hover über Instanz-Karte → Quick-Actions einblenden (Close Positions, Pause, Details)
- **Warum**: Emergency-Ready ohne UI-Clutter – Actions sind versteckt bis gebraucht
- **Adaption**: Mobile = Swipe-to-Reveal statt Hover

**3. Smart Confirmation Modals (Banking Apps)**
- **Anwendung**: "Close Positions" → Modal mit Zusammenfassung (3 Positionen, 4.500€ Exposure, Confirm/Cancel)
- **Warum**: Balance zwischen Speed und Safety – User sieht Konsequenzen vor Bestätigung
- **Adaption**: Kritische Actions = Rot-Button + Zusammenfassung, normale Actions = Standard-Modal

**Visual Patterns:**

**1. Proportional Data Visualization (Treemaps/Bloomberg)**
- **Anwendung**: Kartengröße proportional zu Budget → Visuelle Budget-Evolution
- **Warum**: "Visual Darwinism" – erfolgreiche Instanzen dominieren visuell ohne Zahlen lesen zu müssen
- **Adaption**: CSS Grid mit dynamischen Grid-Area-Sizes, mindestens Min-Size für lesbare Karten

**2. Three-Tier Color Coding (Trading Terminals)**
- **Anwendung**: P/L-Farbcodierung: Grün >0%, Rot <0%, Dunkelrot <-5%
- **Warum**: Sofortige Kritikalitäts-Erkennung – dunkelrote Karten = "Ich muss reagieren"
- **Adaption**: + Optional subtile Pulsing-Animation für <-5% Drawdown

**3. High-Contrast Dark Mode (Professional Tools)**
- **Anwendung**: Dunkler Hintergrund, helle Key-Metrics, Farben nur für Status
- **Warum**: Reduziert Eye-Strain bei langer Nutzung, Zahlen springen hervor
- **Adaption**: Light-Mode als Option, aber Dark = Default für Trading-Aesthetics

### Anti-Patterns to Avoid

**1. Aggressive Animations / Blinking Alerts**
- **Problem**: Erzeugt Panik statt fokussierte Aufmerksamkeit
- **Besser**: Statische rote Farbe + größere Karte, optional subtiles Pulsing
- **Grund**: "Alert without Alarm" – User soll aufmerksam werden, nicht in Panik verfallen

**2. Flat Information Hierarchy**
- **Problem**: Alle Metriken gleich prominent → Information Overload
- **Besser**: P/L + Budget + Status prominent, Sharpe Ratio / Win Rate nur in Details
- **Grund**: "Status-First, Details-On-Demand" – Übersicht muss scanbar bleiben

**3. Modal-Hell / Zu viele Confirmations**
- **Problem**: Jede Action erfordert 3 Klicks → User frustriert
- **Besser**: Normale Actions = direkt, nur kritische = Smart Confirmation
- **Grund**: "Fast when it Matters" – Emergency Actions dürfen nicht durch unnötige Dialoge blockiert werden

**4. Desktop-Only Mobile Experience**
- **Problem**: Kleine Buttons, Hover-Dependencies → Mobile unbrauchbar
- **Besser**: Touch-Optimized Targets (48px), Swipe-Gestures statt Hover
- **Grund**: "Platform-Agnostic Efficiency" – Mobile muss gleichwertig funktionieren

**5. Hidden Critical Information**
- **Problem**: Wichtige Warnungen in Notifications versteckt → User verpasst sie
- **Besser**: Kritische Alerts dominieren Dashboard visuell (größer, rot, oben)
- **Grund**: "Understand the Why" – Transparenz bedeutet sichtbare Probleme, nicht versteckte

### Design Inspiration Strategy

**Was zu adoptieren:**

1. **Traffic-Light Health System (Grafana)** → Aggregierte Status-Anzeige oben
2. **Proportional Card Sizing (Treemaps)** → Budget-Evolution visuell erlebbar
3. **Dark-Mode Trading Aesthetic (Bloomberg)** → Professionelles Look & Feel
4. **Smart Confirmation Pattern (Banking)** → Emergency Actions mit Safeguard

**Was zu adaptieren:**

1. **Multi-Panel Layouts (Bloomberg)** → Vereinfachen: Ein Haupt-Grid, keine anpassbaren Widgets (MVP)
2. **Contextual Actions (Stripe)** → Desktop = Hover, Mobile = Swipe (Platform-spezifisch)
3. **Time-Series Charts (TradingView)** → Nur in Detailansicht, nicht in Übersicht (Progressive Disclosure)

**Was zu vermeiden:**

1. **Bloomberg-Komplexität** → Zu viele Panels = Overwhelm für Solo-Operator
2. **Aggressive Alerts** → Blinkende/Sound-Notifications passen nicht zu "Calm Confidence"
3. **Flat Metric-Dump** → Alle 10 Trading-Metriken auf Übersicht = Information Overload

---

## Design System & Technical Foundation

### Design System Choice

**Empfehlung: Tailwind CSS + shadcn/ui**

**Begründung:**
- **Schnelle Development**: Utility-first CSS + vorgefertigte Components accelerate MVP
- **Customizable**: Vollständig anpassbar für Trading-Terminal-Aesthetic ohne locked-in Themes
- **Modern Stack**: Passt zu Tech-Stack (Vue 3 / React)
- **Dark Mode Native**: First-class Dark-Mode-Support (default für Trading-UI)
- **Responsive Built-in**: Mobile-optimized Components mit Touch-Targets
- **Accessibility**: ARIA-compliant Components out-of-the-box

**Alternative Komponenten:**
- **Charts**: TradingView Lightweight Charts (Performance-optimiert für Real-time)
- **Tables**: TanStack Table (Sortierung, Filtering für Trade-Historie)
- **Notifications**: React-Hot-Toast / Vue-Toast-Notification (subtile Alerts)

### Component Strategy

**Core Components:**

1. **InstanceCard** (Haupt-Component)
   - Props: `id`, `teamName`, `budget`, `pnl`, `status`, `mode` (live/paper), `positions`
   - Variants: `normal`, `warning` (< 0% P/L), `critical` (<-5% P/L)
   - Size: Dynamisch basierend auf Budget (CSS Grid `grid-area`)
   - Actions: Close Positions, Pause, Details

2. **HealthBar** (Global Status)
   - Status: `green` (alle OK), `yellow` (Warnungen), `red` (kritisch)
   - Badge: Anzahl kritischer/warnender Instanzen
   - Position: Fixed top, immer sichtbar

3. **ConfirmationModal** (Smart Safeguard)
   - Variants: `normal`, `critical` (rote Buttons für Positionen schließen)
   - Summary: Dynamische Zusammenfassung der Aktion
   - Actions: Confirm, Cancel (Cancel = default focus)

4. **MetricsDisplay** (Trading-Kennzahlen)
   - Metrics: P/L, Win Rate, Sharpe Ratio, Max Drawdown
   - Formatting: Farb-codiert, große Zahlen, Trend-Indikatoren (↑↓)

5. **TradeHistoryTable** (Details-View)
   - Columns: Time, Symbol, Type (Buy/Sell), Size, Entry, Exit, P/L
   - Features: Sortierung, Pagination, Export

### Information Architecture

**Hauptnavigation:**

```
Dashboard (/)
├── Instanz-Übersicht (Default-View)
├── Instanz-Details (/instance/:id)
│   ├── Portfolio-Metriken
│   ├── Trade-Historie
│   ├── Timeline (Agent-Aktionen)
│   └── Settings
├── Neue Instanz erstellen (/instances/new)
├── Team-Templates (/templates)
└── System-Settings (/settings)
    ├── MT5-Verbindung
    ├── Risiko-Einstellungen
    └── Dashboard-Präferenzen
```

**Navigation Pattern:**
- **Desktop**: Persistent Sidebar (links), Dashboard = primäre Fläche
- **Mobile**: Bottom Navigation (Dashboard, Neue Instanz, Settings), Hamburger für erweiterte Options

**Breadcrumbs:**
Dashboard > Instanz "Alpha-LLM EUR/USD" > Trade-Historie

### Visual Foundation

**Color Palette:**

**Base (Dark Mode Default):**
- Background: `#0a0e1a` (sehr dunkelblau, reduziert Eye-Strain)
- Surface: `#141b2d` (Cards, Modals)
- Border: `#1e2a47` (subtile Trennung)
- Text Primary: `#e4e7eb` (hoher Kontrast)
- Text Secondary: `#8b92a5` (weniger wichtige Info)

**Status Colors:**
- Success/Profit: `#10b981` (Grün, Standard für >0% P/L)
- Warning: `#f59e0b` (Orange/Gelb, 0% bis -5% P/L)
- Critical/Loss: `#ef4444` (Rot, <-5% P/L)
- Info: `#3b82f6` (Blau, neutrale Informationen)

**Trading-Specific:**
- Live-Badge: `#8b5cf6` (Lila, auffällig aber nicht alarm-auslösend)
- Paper-Badge: `#6b7280` (Grau, zurückhaltend)
- Positive Trend: `#10b981` (↑)
- Negative Trend: `#ef4444` (↓)

**Typography:**

- **Primary Font**: Inter (Headings, UI) – Modern, hohe Lesbarkeit
- **Monospace Font**: JetBrains Mono (Zahlen, Code) – Trading-Daten, klare Ziffern-Differenzierung
- **Size Scale**:
  - H1 (Pagina-Title): 24px / 1.5rem
  - H2 (Section): 20px / 1.25rem
  - Body: 14px / 0.875rem
  - Small (Labels): 12px / 0.75rem
  - Large Numbers (P/L): 32px / 2rem (monospace)

**Spacing System:**
- Base Unit: 4px
- Scale: 4px, 8px, 12px, 16px, 24px, 32px, 48px, 64px
- Card Padding: 16px (mobile), 24px (desktop)
- Grid Gap: 16px (mobile), 24px (desktop)

**Responsive Breakpoints:**
- Mobile: < 640px (1 Spalte)
- Tablet: 640px - 1024px (2 Spalten)
- Desktop: > 1024px (3-4 Spalten, dynamisch basierend auf Budget-Proportionen)

### Responsive & Accessibility

**Mobile Optimizations:**

1. **Instanz-Karten**: Vertikale Liste statt Grid
2. **Touch-Targets**: Minimum 48x48px für alle interaktiven Elemente
3. **Swipe-Gestures**: Links-Swipe = Quick Actions einblenden
4. **Bottom Sheet**: Instanz-Details als Bottom-Sheet statt Full-Page
5. **Reduced Motion**: Respektiert `prefers-reduced-motion` für Animationen

**Accessibility Features:**

1. **Keyboard Navigation**:
   - Tab-Order: Health-Bar → Filter → Instanz-Karten (kritische zuerst) → Actions
   - Shortcuts: `/` = Suche, `Esc` = Modal schließen, `?` = Help-Overlay

2. **Screen Reader Support**:
   - ARIA-Labels für Status-Icons
   - Live-Regions für Real-time Updates (WebSocket)
   - Semantic HTML (main, nav, article, aside)

3. **Visual Indicators**:
   - Nicht nur Farbe: Kritische Instanzen = Größer + Icon + Farbe
   - Focus States: 2px Outline für alle interaktiven Elemente
   - High-Contrast Mode: Unterstützt `prefers-contrast`

4. **Text Scaling**:
   - Relative Units (rem/em) für alle Font-Sizes
   - Layout bricht nicht bei 200% Browser-Zoom

### Key User Journeys

**Journey 1: Morgen-Check (5 Minuten)**

1. Dashboard öffnen (URL oder PWA-Icon)
2. **Health-Bar scannen** (3 Sek) → Grün = weiter scrollen, Rot = fokussieren
3. **Instanzen-Grid scannen** (30 Sek):
   - Kritische (rot, groß) automatisch oben
   - P/L-Zahlen scannen (große Monospace-Zahlen)
   - Budget-Evolution erkennen (Kartengröße proportional)
4. **Optional: Details öffnen** (2 Min):
   - Klick auf Karte → Modal/Bottom-Sheet
   - Metriken checken (Sharpe, Drawdown)
   - Timeline scannen (Was hat das System entschieden?)
5. **Dashboard schließen** → Zurück zu anderem Workflow

**Journey 2: Emergency Intervention (<5 Sekunden)**

1. Dashboard öffnen → **Rote Karte sofort sichtbar** (größer, oben)
2. **Hover/Tap auf Karte** → Quick-Actions einblenden
3. **"Close Positions" klicken**
4. **Smart Confirmation Modal**:
   - "3 Positionen schließen"
   - "Exposure: 4.500€"
   - "Confirm" (Rot) / "Cancel" (Default)
5. **Confirm klicken** → Positionen geschlossen
6. **Feedback**: Toast-Notification "Positionen geschlossen", Karte aktualisiert sich

**Journey 3: Neue Instanz erstellen (3 Minuten)**

1. Sidebar → "Neue Instanz" oder FAB (Mobile)
2. **Formular**:
   - Team-Template auswählen (Dropdown mit Preview)
   - Symbol konfigurieren (EUR/USD, GBP/USD, ...)
   - Budget festlegen (Slider oder Input)
   - Modus wählen (Paper/Live Toggle mit Warnung bei Live)
3. **Validierung**: Frontend-Validierung, Smart-Defaults
4. **"Instanz starten"** → Backend erstellt Instanz
5. **Redirect** zu Dashboard → Neue Instanz erscheint (Status: "Starting...")

---

## Implementation Recommendations

### Technical Stack

**Frontend:**
- Framework: Vue 3 (Composition API) oder React 18
- Styling: Tailwind CSS + shadcn/ui
- State Management: Pinia (Vue) / Zustand (React)
- Real-time: WebSocket (native) oder Socket.io
- Charts: TradingView Lightweight Charts
- Build: Vite

**Backend Integration:**
- REST API: FastAPI endpoints
- WebSocket: Instanz-Status-Updates, Trade-Notifications
- Authentication: JWT-basiert (Session-Token)

### Performance Targets

| Metrik | Ziel |
|--------|------|
| Initial Load (Desktop) | < 1.5s |
| Initial Load (Mobile) | < 2.5s |
| WebSocket Latency | < 300ms |
| Instanz-Karte Render | < 50ms (20 Karten) |
| Modal Open Animation | 200ms (smooth) |

### Next Steps for Implementation

1. **Setup Design Tokens**: Tailwind Config mit Custom Colors, Spacing, Typography
2. **Component Library aufbauen**: InstanceCard, HealthBar, ConfirmationModal (Storybook)
3. **Dashboard-Layout implementieren**: Grid-System mit dynamischen Größen
4. **WebSocket-Integration**: Real-time Updates für P/L und Status
5. **Mobile Responsive Testing**: Touch-Gestures, Bottom-Sheet, Swipe-Actions

---

## UX Design Specification Status

**Completed Sections:**
- ✅ Executive Summary
- ✅ Core User Experience
- ✅ Desired Emotional Response
- ✅ UX Pattern Analysis & Inspiration
- ✅ Design System & Technical Foundation
- ✅ Component Strategy
- ✅ Information Architecture
- ✅ Visual Foundation
- ✅ Responsive & Accessibility
- ✅ Key User Journeys
- ✅ Implementation Recommendations

**Dieses UX Design Document ist bereit für:**
- Architektur-Integration
- UI-Prototyping (Figma/Wireframes)
- Frontend-Implementation
- Epics & Stories Creation

---

*UX Design Specification erstellt am 2025-12-02 von Sally (UX Designer Agent)*
