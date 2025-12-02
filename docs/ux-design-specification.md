---
stepsCompleted: [1, 2, 3]
inputDocuments:
  - "/home/cneise/Project/trade/docs/prd.md"
  - "/home/cneise/Project/trade/docs/analysis/product-brief-v1.md"
  - "/home/cneise/Project/trade/docs/analysis/research/technical-ki-trading-plattform-research-2025-12-01.md"
workflowType: 'ux-design'
lastStep: 3
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
