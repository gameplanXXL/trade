---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
inputDocuments:
  - "/docs/analysis/product-brief-v1.md"
  - "/docs/analysis/research/technical-ki-trading-plattform-research-2025-12-01.md"
workflowType: "prd"
lastStep: 10
project_name: "trade"
user_name: "Christian"
date: "2025-12-01"
status: "complete"
---

# Product Requirements Document - trade

**Author:** Christian
**Date:** 2025-12-01

## Executive Summary

Eine persönliche, adaptive Multi-Agent Day-Trading-Plattform, die verschiedene KI-Technologien (LLM und klassisches Machine Learning) kombiniert, um auf Basis aktueller Marktdaten automatisierte Handelsentscheidungen zu treffen.

Das System löst das fundamentale Problem, dass erfolgreiche Trading-Strategien sich schnell ändern und keine universelle "beste" Strategie für alle Marktbedingungen existiert. Statt auf ein einzelnes Modell zu setzen, orchestriert die Plattform mehrere KI-Agenten mit unterschiedlichen Technologien, Parametern und Strategien parallel.

**Kernprinzipien:**
- **Multi-Agent, Multi-Technologie:** LLM-basierte Agenten, LSTM-Netzwerke und Reinforcement Learning arbeiten parallel
- **Dynamisches Training:** Konfigurierbare Trainingszeiträume pro Agent – von kurzfristigen 14-Tage-Fenstern bis zu längeren Zeiträumen für spezielle Szenarien (z.B. Crash-Vorhersage)
- **Agent-Balancing:** Kontinuierliche Performance-Messung steuert Budget-Allokation – erfolgreiche Agenten erhalten mehr Kapital, schwache werden auf Paper Trading degradiert
- **Paralleles Shadow-Portfolio:** Jeder Agent führt permanent ein 10.000€ Paper-Trading-Portfolio zur objektiven Erfolgsmessung
- **Budget-Isolation:** Strikte Risikogrenzen pro Agent mit Gewinnkappung und Lock-Mechanismus

### Was macht dieses System besonders

Das System unterscheidet sich fundamental von klassischen Trading-Bots durch seinen evolutionären Ansatz: Agenten konkurrieren nicht nur am Markt, sondern auch untereinander um Ressourcen. Die kontinuierliche Performance-Messung über das Shadow-Portfolio ermöglicht objektive Bewertung unabhängig vom aktuellen Live-Budget.

Die Kombination aus dynamischen Trainingszeiträumen und Agent-Balancing schafft ein selbstoptimierendes System, das sich automatisch an veränderte Marktbedingungen anpasst – ohne manuelle Intervention.

## Project Classification

**Technical Type:** Web-App mit Backend-Orchestrierung
**Domain:** Fintech (Personal Trading)
**Complexity:** Hoch

Das Projekt kombiniert Echtzeit-Datenverarbeitung, KI/ML-Integration, Risikomanagement und ein Web-Dashboard. Die Komplexität ergibt sich aus den Anforderungen an Latenz, Zuverlässigkeit und die Orchestrierung mehrerer paralleler Agenten mit individuellen Budgets und Strategien.

## Success Criteria

### User Success

Als alleiniger Nutzer dieses Systems definiert sich Erfolg durch:

- **Zeitersparnis:** Das System trifft automatisiert Handelsentscheidungen ohne manuelle Intervention
- **Transparenz:** Jederzeit Einblick in Agent-Performance, Trades und Budget-Allokation über das Dashboard
- **Vertrauen:** Das Agent-Balancing-System identifiziert zuverlässig erfolgreiche Strategien und sortiert schwache aus
- **Kontrolle:** Konfigurierbare Parameter (Trainingszeiträume, Risikogrenzen) ohne Code-Änderungen

### Business Success

| Metrik | Ziel | Zeitraum |
|--------|------|----------|
| **Durchschnittliche Monatsrendite** | ≥ 3% | Nach Einlaufphase |
| **Maximaler Drawdown** | ≤ 25% | Pro Agent und Gesamt |
| **Erste aussagekräftige Ergebnisse** | Trend erkennbar | 3 Monate |
| **Profitable Agenten identifiziert** | Mind. 1 Agent konsistent profitabel | 6 Monate |

### Technical Success

| Anforderung | Ziel |
|-------------|------|
| **Stabilität** | System läuft zuverlässig ohne häufige Abstürze (kein HA-Cluster nötig) |
| **Parallele Agenten** | Bis zu 20 Agenten gleichzeitig |
| **Order-Sicherheit** | Jede Order mit Trailing Stoploss – Ausfallsicherheit bei Systemausfall |
| **Latenz** | Ausreichend für Day-Trading (keine HFT-Anforderungen) |
| **Wiederherstellung** | Bei Ausfall: Manueller Neustart akzeptabel, offene Positionen durch Trailing SL abgesichert |

### Measurable Outcomes

**Nach 3 Monaten:**
- [ ] Mindestens 3 Agenten mit unterschiedlichen Strategien aktiv
- [ ] Shadow-Portfolio-Daten für alle Agenten vorhanden
- [ ] Agent-Balancing hat erste Budget-Anpassungen durchgeführt
- [ ] Performance-Trends erkennbar (welche Strategien funktionieren)

**Nach 6 Monaten:**
- [ ] Mindestens 1 Agent konsistent profitabel im Live-Trading
- [ ] Durchschnittliche Monatsrendite ≥ 3% (über profitable Agenten)
- [ ] Kein Agent hat 25% Drawdown-Grenze überschritten ohne Degradierung

**Nach 12 Monaten:**
- [ ] System läuft stabil ohne größere Ausfälle
- [ ] Profitable Agenten-Konfigurationen dokumentiert
- [ ] Optional: Erweiterung auf weitere Assets/Märkte evaluiert

## Product Scope

### MVP - Minimum Viable Product

**Must Have:**
- 1 funktionierender Agent (LLM oder ML-basiert)
- MT5-Integration mit ICMarkets (Demo-Konto)
- Trailing Stoploss bei jeder Order
- Virtueller Saldo pro Agent
- Basis-Risikomanagement (25% Drawdown-Stopp, Gewinnkappung)
- Performance-Tracking (Win-Rate, P/L, Sharpe Ratio)
- Einfaches Web-Dashboard zur Überwachung

### Growth Features (Post-MVP)

- Multi-Agent-Betrieb (bis 20 Agenten)
- Agent-Balancing-System (automatische Budget-Allokation)
- Paralleles Shadow-Portfolio (10.000€ Paper Trading pro Agent)
- Verschiedene KI-Technologien (LLM + LSTM + RL)
- Dynamische Trainingszeiträume (konfigurierbar pro Agent)
- Erweiterte Crash-Vorhersage-Modelle
- Live-Trading-Freigabe nach Shadow-Portfolio-Beweis

### Vision (Future)

- Erweiterung auf weitere Assets/Märkte
- Multi-LLM Veto-System (Konsens mehrerer LLMs)
- Self-Hosted LLMs für reduzierte Kosten/Latenz
- Automatische Strategie-Evolution
- Mobile App für Monitoring

## User Journeys

### Journey 1: Christian als Operator – Der Morgen-Check

Christian startet seinen Tag mit einem Kaffee und öffnet das Trading-Dashboard auf seinem Laptop. Die Übersichtsseite zeigt ihm sofort die wichtigsten Kennzahlen der letzten 24 Stunden: Gesamtperformance aller Agenten, Anzahl der Trades, und ob es Auffälligkeiten gab.

Er sieht auf einen Blick, dass Agent "Alpha-LLM" gestern 2,1% Gewinn gemacht hat, während "Beta-LSTM" bei -0,3% liegt. Das Agent-Balancing-System hat bereits reagiert und Betas Live-Budget um 20% reduziert. Christians Blick wandert zum Shadow-Portfolio-Vergleich – dort zeigt Beta tatsächlich auch im Paper-Trading schwache Performance. Keine Fehlentscheidung des Systems.

Ein gelbes Warnsymbol zeigt ihm, dass Agent "Gamma-RL" die 15%-Drawdown-Schwelle erreicht hat – noch nicht kritisch, aber beobachtenswert. Christian klickt darauf und sieht die Trade-Historie der letzten Tage. Er entscheidet, nichts zu ändern und lässt das System weiterarbeiten. Nach 5 Minuten schließt er das Dashboard und beginnt seinen Arbeitstag.

**Revealed Requirements:**
- Dashboard-Übersicht mit Gesamtperformance
- Agent-Status auf einen Blick (Gewinn/Verlust, Budget-Status)
- Shadow-Portfolio vs. Live-Vergleich
- Warnsystem mit Schwellenwert-Indikatoren
- Trade-Historie pro Agent

---

### Journey 2: Christian als Konfigurator – Neuen Agent einrichten

Nach zwei Wochen erfolgreicher Tests mit seinem ersten LLM-Agenten will Christian einen zweiten Agenten mit einer anderen Strategie hinzufügen. Er öffnet das Dashboard und navigiert zu "Agenten verwalten".

Er klickt auf "Neuer Agent" und wählt aus einer Liste von Agent-Templates: LLM-basiert (Claude), LLM-basiert (GPT), LSTM, oder Reinforcement Learning. Er entscheidet sich für einen LSTM-Agenten für kurzfristige Kursprognosen.

Das Formular zeigt ihm die konfigurierbaren Parameter: Trainingszeitraum (er wählt 21 Tage statt der Standard-14), Startbudget für Paper-Trading (10.000€ automatisch), und die Risikogrenzen (er übernimmt die Defaults: 25% Max-Drawdown, 150% Gewinnkappung). Er gibt dem Agenten den Namen "Delta-LSTM-Short" und klickt auf "Agent starten".

Das System bestätigt: Der Agent startet im Paper-Trading-Modus und wird nach dem initialen Training seine ersten Trades machen. Christian sieht den neuen Agenten sofort in seiner Dashboard-Übersicht mit Status "Training läuft...".

**Revealed Requirements:**
- Agent-Verwaltungsbereich im Dashboard
- Template-Auswahl für verschiedene Agent-Typen
- Konfigurationsformular mit sinnvollen Defaults
- Trainingszeitraum konfigurierbar
- Live-Status-Updates während Training
- Agenten starten initial im Paper-Trading-Modus

---

### Journey 3: Christian bei Intervention – Agent wird degradiert

Drei Wochen später öffnet Christian das Dashboard und sieht sofort ein rotes Warnsymbol. Agent "Beta-LSTM" hat die 25%-Drawdown-Grenze erreicht. Das System hat automatisch reagiert: Beta wurde vom Live-Trading auf reines Paper-Trading zurückgestuft, das verbleibende Live-Budget wurde gesichert.

Christian klickt auf die Detailansicht und sieht die Timeline: Vor einer Woche begann Betas Performance zu sinken. Das Agent-Balancing hat schrittweise das Budget reduziert (erst -20%, dann -40%), aber die Verluste setzten sich fort. Gestern wurde die Grenze erreicht.

Er schaut sich Betas Trade-Entscheidungen an und bemerkt ein Muster: Der Agent hat in einer volatilen Marktphase zu aggressiv gehandelt. Christian hat zwei Optionen: Den Agenten mit neuen Parametern neu starten (längerer Trainingszeitraum, konservativere Einstellungen) oder ihn komplett deaktivieren.

Er entscheidet sich für einen Neustart mit 30-Tage-Trainingsfenster und aktiviert den "Nur Paper-Trading für 14 Tage"-Modus, bevor der Agent wieder Live-Budget erhalten kann. Das System setzt Beta zurück und beginnt das neue Training.

**Revealed Requirements:**
- Automatische Degradierung bei Grenzüberschreitung
- Detaillierte Timeline der Agent-Aktionen
- Trade-Historie mit Entscheidungsgrund
- Agent-Neustart mit geänderten Parametern
- "Bewährungsphase" vor Live-Freigabe
- Budget-Sicherung bei Degradierung

---

### Journey 4: Erstes Setup – System in Betrieb nehmen

Christian hat gerade seinen VServer eingerichtet und die Trading-Plattform installiert. Er öffnet das Dashboard zum ersten Mal und wird von einem Setup-Wizard begrüßt.

**Schritt 1: MT5-Verbindung** – Er gibt seine ICMarkets-Zugangsdaten ein. Das System testet die Verbindung und bestätigt: Demo-Konto verbunden, Kontostand 100.000€ (virtuell).

**Schritt 2: Erster Agent** – Der Wizard schlägt vor, mit einem LLM-Agenten zu starten, da diese am einfachsten zu konfigurieren sind. Christian wählt Claude als Basis-Modell, akzeptiert die Default-Parameter und gibt dem Agenten den Namen "Alpha-LLM".

**Schritt 3: Risiko-Einstellungen** – Er bestätigt die globalen Risiko-Defaults: 25% Max-Drawdown, 150% Gewinnkappung, Trailing Stoploss bei jeder Order. Der Wizard erklärt kurz, was jede Einstellung bedeutet.

**Schritt 4: Start** – Christian klickt auf "System starten". Das Dashboard wechselt zur Übersicht und zeigt: "Alpha-LLM trainiert... Erste Trades in ca. 2 Stunden." Er lehnt sich zurück – das System läuft.

**Revealed Requirements:**
- Setup-Wizard für Ersteinrichtung
- MT5-Verbindungstest
- Geführte Agent-Erstellung
- Erklärungen für Risiko-Einstellungen
- Zeitschätzung für erstes Training
- Klare Statusmeldungen

---

### Journey Requirements Summary

| Bereich | Erforderliche Capabilities |
|---------|---------------------------|
| **Dashboard-Übersicht** | Gesamtperformance, Agent-Status, Warnungen, Quick-Stats |
| **Agent-Verwaltung** | Erstellen, Konfigurieren, Starten, Stoppen, Neustart |
| **Performance-Tracking** | Live vs. Shadow, Trade-Historie, Metriken (P/L, Drawdown, Win-Rate) |
| **Warnsystem** | Schwellenwert-Indikatoren, Automatische Aktionen, Status-Timeline |
| **Risikomanagement** | Trailing Stoploss, Drawdown-Limits, Gewinnkappung, Budget-Allokation |
| **Agent-Balancing** | Automatische Budget-Anpassung, Degradierung, Bewährungsphase |
| **Onboarding** | Setup-Wizard, MT5-Verbindung, Geführte Konfiguration |

## Domain-Specific Requirements

### Personal Trading – Relevante Constraints

Da dies ein persönliches Trading-System ist (kein Handel für Dritte), entfallen klassische Fintech-Compliance-Anforderungen wie KYC/AML oder regulatorische Lizenzen. Die folgenden Aspekte sind dennoch relevant:

### Security Requirements

| Bereich | Anforderung |
|---------|-------------|
| **MT5/Broker-Credentials** | Sichere Speicherung der ICMarkets-Zugangsdaten (nicht im Klartext) |
| **LLM API-Keys** | Verschlüsselte Speicherung für OpenAI/Anthropic Keys |
| **Dashboard-Zugang** | Login-Schutz (Passwort oder lokaler Zugriff only) |
| **VServer-Zugang** | SSH-Key-Authentifizierung, kein Passwort-Login |

### Data Protection

| Bereich | Anforderung |
|---------|-------------|
| **Trade-Historie** | Lokale Speicherung auf eigenem VServer |
| **Performance-Daten** | Keine Übertragung an externe Dienste (außer Trading-APIs) |
| **Backups** | Regelmäßige Sicherung der Datenbank und Agent-Konfigurationen |
| **Logs** | Sensible Daten (Credentials) nie in Logs schreiben |

### ICMarkets-spezifische Regeln

- Automatisiertes Trading ist vollständig erlaubt (keine Einschränkungen)
- Raw Pricing Account empfohlen für engere Spreads
- API-Rate-Limits beachten (aber großzügig für Day-Trading)

## Innovation & Novel Patterns

### Detected Innovation Areas

Das System unterscheidet sich fundamental von klassischen Trading-Bots durch mehrere innovative Konzepte:

#### 1. Evolutionäres Agent-Balancing

Statt statischer Budget-Zuweisung konkurrieren Agenten um Ressourcen basierend auf ihrer Performance. Das System implementiert ein evolutionäres Prinzip:

- **Erfolgreiche Agenten** erhalten automatisch mehr Live-Budget
- **Schwache Agenten** werden schrittweise reduziert und auf Paper-Trading degradiert
- **Das System optimiert sich selbst** ohne manuelle Intervention

Dies unterscheidet sich von klassischen Ansätzen, wo Trading-Strategien manuell bewertet und angepasst werden müssen.

#### 2. Shadow-Portfolio-Validierung

Jeder Agent führt permanent ein paralleles 10.000€ Paper-Trading-Portfolio – unabhängig vom aktuellen Live-Budget. Dies ermöglicht:

- **Objektive Performance-Messung** ohne Kapitalrisiko
- **Faire Vergleichbarkeit** zwischen Agenten mit unterschiedlichen Live-Budgets
- **Früherkennung** von Performance-Problemen bevor Live-Kapital betroffen ist
- **Bewährungsprüfung** für neue oder degradierte Agenten

#### 3. Multi-Technologie-Ensemble

Statt auf eine KI-Technologie zu setzen, kombiniert das System:

- **LLM-basierte Agenten** (Claude, GPT) für qualitative Analyse und Sentiment
- **LSTM-Netzwerke** für Zeitreihen-Prognosen
- **Reinforcement Learning** für adaptive Positionsgrößen

Die Diversifikation auf Technologie-Ebene reduziert das Risiko, dass eine einzelne Modell-Schwäche das gesamte System beeinträchtigt.

#### 4. Dynamische Trainingsfenster

Statt fixer Trainingszeiträume können Agenten unterschiedliche Fenster nutzen:

- **Kurzfristig (14 Tage)** für schnelle Marktanpassung
- **Langfristig (30+ Tage)** für Crash-Vorhersage und Trend-Erkennung
- **Pro Agent konfigurierbar** je nach Strategie-Typ

### Validation Approach

| Innovation | Validierung |
|------------|-------------|
| Agent-Balancing | 3 Monate Paper-Trading mit simulierten Budget-Anpassungen |
| Shadow-Portfolio | Vergleich Shadow vs. Live-Performance über 6 Monate |
| Multi-Technologie | Paralleler Betrieb verschiedener Agent-Typen, Performance-Vergleich |
| Dynamische Fenster | A/B-Test verschiedener Trainingszeiträume pro Strategie |

### Risk Mitigation

| Risiko | Mitigation |
|--------|------------|
| Agent-Balancing verstärkt Verluste | 25% Max-Drawdown-Grenze stoppt Agenten automatisch |
| Shadow ≠ Live-Performance | Bewährungsphase (14 Tage nur Paper) vor Live-Freigabe |
| Alle Agenten versagen gleichzeitig | Technologie-Diversifikation + Trailing Stoploss bei jeder Order |
| Falsches Trainingsfenster | Shadow-Portfolio zeigt Probleme vor Live-Einsatz |

## Technical Requirements

### Architecture Overview

Das System basiert auf einer **3-Ebenen-Architektur**:

```
Agent-Rollen (Python) → Teams (YAML) → Team-Instanzen (PostgreSQL)
```

### Ebene 1: Agent-Rollen (Code)

Python-Klassen mit konfigurierbaren Parametern:

| Rolle | Klasse | Konfigurierbare Parameter |
|-------|--------|---------------------------|
| **Crash Detector** | `CrashDetector` | threshold, window_days, indicators |
| **Signal Analyst** | `LLMSignalAnalyst`, `LSTMAnalyst`, `RLAnalyst` | model, min_confidence, lookback |
| **Trader** | `Trader` | position_sizing, max_positions, trailing_stop |
| **Risk Manager** | `RiskManager` | max_drawdown, max_exposure, position_limits |

### Ebene 2: Teams (YAML-Konfiguration)

Teams definieren Rollen-Kombinationen + Pipeline + Override-Regeln:

```yaml
# teams/conservative_llm.yaml
name: "Conservative LLM Team"
version: "1.0"

roles:
  crash_detector:
    class: CrashDetector
    params:
      threshold: 0.9
      window_days: 30

  analyst:
    class: LLMSignalAnalyst
    params:
      model: "claude-3-sonnet"
      min_confidence: 0.75

  trader:
    class: Trader
    params:
      position_sizing: "conservative"
      max_positions: 2
      trailing_stop_pct: 2.0

  risk_manager:
    class: RiskManager
    params:
      max_drawdown: 0.20

# Haupt-Pipeline
pipeline:
  - crash_detector.check
  - analyst.generate_signal
  - trader.prepare_order
  - risk_manager.validate
  - trader.execute

# Override-Regeln (höhere Priorität als Pipeline)
override_rules:
  - name: "Crash Emergency"
    condition: "crash_detector.status == CRASH"
    action: "trader.close_all_positions()"
    priority: 1

  - name: "Warning Mode"
    condition: "crash_detector.status == WARNING"
    action: "trader.set_mode(HOLD)"
    priority: 2
```

### Ebene 3: Team-Instanzen (Datenbank)

Runtime-Konfiguration für konkrete Ausführungen:

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `id` | INT | Primärschlüssel |
| `team_template` | VARCHAR | Referenz auf YAML-Datei |
| `mode` | ENUM | `paper` \| `live` |
| `symbols` | JSON | `["EUR/USD", "GBP/USD"]` |
| `budget` | DECIMAL | Startbudget (z.B. 10.000€) |
| `status` | ENUM | `active` \| `paused` \| `stopped` |
| `created_at` | TIMESTAMP | Erstellungsdatum |

### Team-Analytics Datenmodell

**Performance-Tracking auf mehreren Ebenen:**

| Metrik | Granularität | Beschreibung |
|--------|--------------|--------------|
| `total_pnl` | Team | Gesamtgewinn/-verlust |
| `symbol_pnl` | Symbol | P/L pro Handelsinstrument |
| `win_rate` | Team + Symbol | Gewinnquote |
| `sharpe_ratio` | Team | Risikoadjustierte Rendite |
| `max_drawdown` | Team | Maximaler Rückgang |
| `paper_vs_live` | Modus | Vergleich Paper ↔ Live |
| `agent_activity` | Agent | Signale, Warnungen, Ablehnungen |

### Technology Stack

#### Backend

| Komponente | Technologie |
|------------|-------------|
| **Sprache** | Python 3.11+ |
| **Web Framework** | FastAPI |
| **Agent Framework** | LangGraph |
| **MT5 Integration** | aiomql |
| **Datenbank** | PostgreSQL + TimescaleDB |
| **Cache/State** | Redis |
| **Config Parsing** | PyYAML + Pydantic |

#### Frontend

| Komponente | Technologie |
|------------|-------------|
| **Framework** | Vue 3 oder React |
| **UI Library** | Tailwind CSS + shadcn/ui |
| **Charts** | TradingView Lightweight Charts |
| **Real-time** | WebSocket |

### Browser Support

Nur moderne Browser: Chrome 90+, Firefox 90+, Edge 90+, Safari 14+

### Performance Targets

| Metrik | Ziel |
|--------|------|
| Dashboard-Ladezeit | < 2 Sekunden |
| WebSocket-Latenz | < 500ms |
| Pipeline-Durchlauf | < 1 Sekunde pro Signal |

## Project Scoping & Phased Development

### MVP Strategy & Philosophy

**MVP Approach:** Platform MVP – Die Team-Architektur ist das Fundament für alles Weitere. Ein funktionierendes Team mit allen Rollen beweist das Kernkonzept.

**Begründung:** Das Team-Konzept (Rollen-Kooperation, Pipeline, Override-Regeln) ist das Differenzierungsmerkmal. Ohne dieses Fundament wäre spätere Erweiterung schwierig.

### MVP Feature Set (Phase 1)

**Ziel:** 1 vollständiges Team im Paper Trading beweist das Konzept

#### Core User Journeys Supported

| Journey | MVP-Status | Einschränkungen |
|---------|------------|-----------------|
| Morgen-Check (Operator) | ✅ Vollständig | - |
| Neuen Agent einrichten | ⚠️ Teilweise | Nur 1 Team-Template initial |
| Intervention bei Problemen | ✅ Vollständig | - |
| Erstes Setup | ✅ Vollständig | Vereinfachter Wizard |

#### Must-Have Capabilities (MVP)

**Agent-Rollen (Python-Klassen):**
- [ ] `CrashDetector` – Überwacht Markt auf Crash-Signale
- [ ] `LLMSignalAnalyst` – Generiert Trading-Signale (1 LLM-Typ: Claude)
- [ ] `Trader` – Führt Orders aus, Trailing Stoploss
- [ ] `RiskManager` – Validiert Orders, überwacht Drawdown

**Team-System:**
- [ ] YAML-Parser für Team-Konfiguration
- [ ] Pipeline-Executor (sequenzieller Ablauf)
- [ ] Override-Regel-Engine (Prioritäts-basiert)
- [ ] 1 Team-Template: "Conservative LLM"

**Team-Instanzen:**
- [ ] Erstellen/Starten/Stoppen von Instanzen
- [ ] Paper-Trading-Modus
- [ ] Symbol-Konfiguration (EUR/USD initial)
- [ ] Budget-Tracking (virtuell)

**MT5 Integration:**
- [ ] Verbindung zu ICMarkets Demo-Konto
- [ ] Market Data Feed (Kurse, Ticks)
- [ ] Order Execution (Paper Trading simuliert)
- [ ] Trailing Stoploss bei jeder Order

**Dashboard:**
- [ ] Team-Übersicht (Status, P/L)
- [ ] Performance-Metriken (Win-Rate, Drawdown, Sharpe)
- [ ] Trade-Historie
- [ ] Agent-Aktivität (Signale, Warnungen)
- [ ] WebSocket Real-time Updates

**Team-Analytics (Basis):**
- [ ] Gesamt-Performance pro Team-Instanz
- [ ] Performance pro Symbol
- [ ] Paper vs. Live Tracking (nur Paper im MVP)

#### Nicht im MVP

- ❌ Multi-Team-Betrieb (nur 1 Team-Instanz)
- ❌ Agent-Balancing (automatische Budget-Anpassung)
- ❌ Shadow-Portfolio (paralleles Paper Trading)
- ❌ LSTM- oder RL-Agenten (nur LLM)
- ❌ Live-Trading (nur Paper)
- ❌ Dynamische Trainingszeiträume
- ❌ Setup-Wizard (manuelles Setup OK)

### Post-MVP Features

#### Phase 2: Growth (Multi-Team & Live)

**Ziel:** Mehrere Teams parallel, Live-Trading-Freigabe

| Feature | Beschreibung |
|---------|--------------|
| **Multi-Team-Betrieb** | Bis zu 5 Team-Instanzen parallel |
| **Live-Trading** | Freigabe nach Paper-Trading-Beweis |
| **Shadow-Portfolio** | Paralleles 10.000€ Paper Trading pro Team |
| **Agent-Balancing** | Automatische Budget-Allokation |
| **Weitere Analyst-Typen** | LSTM-Analyst, RL-Analyst |
| **Weitere Symbole** | GBP/USD, USD/JPY, Gold |
| **Erweiterte Analytics** | Detaillierte Agent-Statistiken |

#### Phase 3: Expansion (Skalierung & Optimierung)

**Ziel:** Skalierung, Kosten-Optimierung, neue Strategien

| Feature | Beschreibung |
|---------|--------------|
| **Bis zu 20 Teams** | Volle Skalierung |
| **Self-Hosted LLMs** | vLLM + Llama für reduzierte Kosten |
| **Multi-LLM Veto** | Konsens mehrerer LLMs |
| **Dynamische Trainingsfenster** | Pro Team konfigurierbar |
| **Erweiterte Crash-Detection** | Längere Fenster, mehr Indikatoren |
| **Weitere Asset-Klassen** | Krypto, Indizes |
| **Mobile Monitoring** | Responsive Dashboard oder App |

### Risk Mitigation Strategy

#### Technical Risks

| Risiko | Wahrscheinlichkeit | Mitigation |
|--------|-------------------|------------|
| LLM-API instabil | Mittel | Retry-Logic, Fallback-Responses |
| MT5-Verbindung bricht ab | Mittel | Reconnect-Logic, Trailing SL als Absicherung |
| Pipeline-Fehler | Niedrig | Ausführliches Logging, Fehler-Recovery |
| YAML-Parsing-Fehler | Niedrig | Pydantic-Validierung beim Laden |

#### Market Risks

| Risiko | Mitigation |
|--------|------------|
| Strategie funktioniert nicht | 3 Monate Paper Trading vor Live |
| Crash-Detection versagt | Trailing Stoploss als Fallback |
| Alle Signale falsch | Risk Manager kann alle Orders ablehnen |

#### Resource Risks

| Risiko | Mitigation |
|--------|------------|
| MVP dauert zu lange | Fokus auf 1 Team-Template, minimale UI |
| LLM-Kosten zu hoch | Claude Haiku für Testing, Sonnet für Produktion |
| Komplexität unterschätzt | Strikte MVP-Grenzen, kein Scope Creep |

### MVP Success Criteria (Checkpoint)

**Nach MVP-Fertigstellung prüfen:**

- [ ] 1 Team-Instanz läuft stabil im Paper Trading
- [ ] Pipeline + Override-Regeln funktionieren korrekt
- [ ] Crash Detector erkennt simulierte Crash-Situationen
- [ ] Dashboard zeigt Live-Updates via WebSocket
- [ ] Performance-Metriken werden korrekt berechnet
- [ ] Trailing Stoploss wird bei jeder Order gesetzt

## Functional Requirements

### Team-Konfiguration

- **FR1:** User kann Team-Templates als YAML-Dateien definieren
- **FR2:** User kann Agent-Rollen mit Parametern in Team-Templates konfigurieren
- **FR3:** User kann Pipeline-Abläufe für Teams definieren (sequenzielle Schritte)
- **FR4:** User kann Override-Regeln mit Prioritäten für Teams definieren
- **FR5:** System validiert YAML-Konfiguration beim Laden und meldet Fehler

### Team-Instanz-Management

- **FR6:** User kann Team-Instanzen aus Templates erstellen
- **FR7:** User kann Symbole für Team-Instanzen konfigurieren (z.B. EUR/USD)
- **FR8:** User kann Budget für Team-Instanzen festlegen
- **FR9:** User kann Team-Instanzen starten und stoppen
- **FR10:** User kann Team-Instanzen im Paper-Trading-Modus betreiben
- **FR11:** System speichert Team-Instanzen persistent in der Datenbank

### Agent-Rollen

- **FR12:** System stellt CrashDetector-Rolle bereit (überwacht Crash-Signale)
- **FR13:** System stellt LLMSignalAnalyst-Rolle bereit (generiert Trading-Signale via LLM)
- **FR14:** System stellt Trader-Rolle bereit (führt Orders aus)
- **FR15:** System stellt RiskManager-Rolle bereit (validiert Orders, überwacht Drawdown)
- **FR16:** Jede Agent-Rolle akzeptiert konfigurierbare Parameter

### Pipeline & Regeln

- **FR17:** System führt Pipeline-Schritte sequenziell aus
- **FR18:** System evaluiert Override-Regeln nach Priorität vor Pipeline-Schritten
- **FR19:** CrashDetector kann Status "NORMAL", "WARNING" oder "CRASH" setzen
- **FR20:** Bei Status "CRASH" schließt Trader automatisch alle Positionen
- **FR21:** Bei Status "WARNING" wechselt Trader in HOLD-Modus (keine neuen Trades)
- **FR22:** RiskManager kann Orders ablehnen (REJECT) oder genehmigen (APPROVE)

### Trading Execution

- **FR23:** System verbindet sich mit MT5/ICMarkets Demo-Konto
- **FR24:** System empfängt Echtzeit-Kursdaten von MT5
- **FR25:** Trader kann BUY- und SELL-Orders platzieren
- **FR26:** System setzt automatisch Trailing Stoploss bei jeder Order
- **FR27:** System simuliert Order-Execution im Paper-Trading-Modus
- **FR28:** System führt virtuelle Buchführung pro Team-Instanz (Budget, P/L)

### Performance Analytics

- **FR29:** System berechnet Gesamt-P/L pro Team-Instanz
- **FR30:** System berechnet P/L pro Symbol
- **FR31:** System berechnet Win-Rate (Gewinn-Trades / Gesamt-Trades)
- **FR32:** System berechnet Sharpe Ratio
- **FR33:** System berechnet maximalen Drawdown
- **FR34:** System speichert Performance-Historie (täglich, wöchentlich, monatlich)
- **FR35:** System trackt Agent-Aktivität (Signale, Warnungen, Ablehnungen)

### Dashboard - Übersicht

- **FR36:** User sieht Team-Instanz-Status auf einen Blick (aktiv, pausiert, gestoppt)
- **FR37:** User sieht Gesamt-P/L und aktuelle Performance-Metriken
- **FR38:** User sieht Warnungen und Alerts (gelb für WARNING, rot für CRASH)
- **FR39:** Dashboard aktualisiert sich in Echtzeit via WebSocket

### Dashboard - Team-Details

- **FR40:** User kann Team-Instanz-Details anzeigen
- **FR41:** User sieht Trade-Historie mit allen ausgeführten Orders
- **FR42:** User sieht Timeline der Agent-Aktionen
- **FR43:** User sieht Performance-Charts (P/L-Verlauf, Drawdown)
- **FR44:** User sieht Agent-Statistiken (Analyst-Confidence, RiskManager-Entscheidungen)

### Dashboard - Konfiguration

- **FR45:** User kann neue Team-Instanz über UI erstellen
- **FR46:** User kann Team-Instanz pausieren und fortsetzen
- **FR47:** User kann Team-Instanz permanent stoppen
- **FR48:** User kann Symbole und Budget bei Erstellung festlegen

### Sicherheit & Datenschutz

- **FR49:** System speichert Credentials verschlüsselt (MT5, LLM-APIs)
- **FR50:** Dashboard erfordert Authentifizierung (Login)
- **FR51:** System schreibt keine sensiblen Daten in Logs

### Fehlerbehandlung

- **FR52:** System versucht automatisch Reconnect bei MT5-Verbindungsabbruch
- **FR53:** System loggt alle Fehler mit Kontext für Debugging
- **FR54:** Bei LLM-API-Fehler verwendet System Retry-Logic

## Non-Functional Requirements

### Performance

| Anforderung | Zielwert | Begründung |
|-------------|----------|------------|
| **Pipeline-Durchlauf** | < 1 Sekunde | Day-Trading erfordert zeitnahe Reaktion auf Signale |
| **Dashboard-Ladezeit** | < 2 Sekunden | Flüssige User Experience beim Morgen-Check |
| **WebSocket-Latenz** | < 500ms | Echtzeit-Updates für Trade-Status und Warnungen |
| **LLM-Response-Time** | < 5 Sekunden | Akzeptabel für Signal-Generierung (kein HFT) |
| **Datenbank-Queries** | < 100ms | Schnelle Abfragen für Dashboard und Analytics |

### Skalierbarkeit

| Anforderung | Zielwert |
|-------------|----------|
| **Team-Instanzen (MVP)** | 1 |
| **Team-Instanzen (Growth)** | 5 |
| **Team-Instanzen (Max)** | 20 |
| **Parallele WebSocket-Connections** | 5 (ein User, mehrere Tabs) |
| **Trade-Historie-Retention** | 1 Jahr |
| **Performance-Daten-Retention** | Unbegrenzt (aggregiert) |

### Verfügbarkeit & Zuverlässigkeit

| Anforderung | Beschreibung |
|-------------|--------------|
| **Kein HA-Cluster** | Single-Server-Deployment akzeptabel |
| **Manueller Neustart** | Bei Ausfall ist manueller Restart OK |
| **Trailing Stoploss** | Absicherung bei Systemausfall (Broker-seitig) |
| **Graceful Shutdown** | System schließt offene Connections sauber |
| **Auto-Reconnect** | Automatische MT5-Wiederverbindung |

### Sicherheit

| Anforderung | Beschreibung |
|-------------|--------------|
| **Credential-Verschlüsselung** | MT5 und LLM-API-Keys verschlüsselt gespeichert |
| **Dashboard-Auth** | Login-Schutz (Session-basiert) |
| **HTTPS** | Verschlüsselte Verbindung zum Dashboard |
| **SSH-Only** | Server-Zugang nur per SSH-Key |
| **No Secrets in Logs** | Credentials nie in Logfiles |

### Wartbarkeit

| Anforderung | Beschreibung |
|-------------|--------------|
| **Strukturiertes Logging** | JSON-Format für einfache Auswertung |
| **Log-Levels** | DEBUG, INFO, WARNING, ERROR |
| **Health-Endpoint** | `/health` für Systemstatus |
| **Config-Reload** | Team-YAML ohne Neustart aktualisierbar |
| **Datenbank-Migrations** | Versionierte Schema-Änderungen |

### Kompatibilität

| Anforderung | Beschreibung |
|-------------|--------------|
| **Browser** | Chrome 90+, Firefox 90+, Edge 90+, Safari 14+ |
| **Python** | 3.11+ |
| **PostgreSQL** | 15+ mit TimescaleDB |
| **MT5** | Aktuelle Version via aiomql |

### Monitoring & Observability

| Anforderung | Beschreibung |
|-------------|--------------|
| **Dashboard-Metriken** | System-Status direkt im Dashboard sichtbar |
| **Error-Tracking** | Fehler mit Stack-Trace und Kontext geloggt |
| **Trade-Audit-Log** | Alle Order-Aktionen nachvollziehbar |
| **Agent-Decision-Log** | Signale, Ablehnungen, Override-Auslösungen dokumentiert |

---

## Zusammenfassung & Nächste Schritte

### PRD-Status

Dieses Product Requirements Document ist **vollständig** und deckt ab:

| Abschnitt | Status |
|-----------|--------|
| Executive Summary | ✅ |
| Project Classification | ✅ |
| Success Criteria | ✅ |
| Product Scope (MVP + Phasen) | ✅ |
| User Journeys | ✅ |
| Domain-Specific Requirements | ✅ |
| Innovation & Novel Patterns | ✅ |
| Technical Requirements | ✅ |
| Functional Requirements (54 FRs) | ✅ |
| Non-Functional Requirements | ✅ |

### Empfohlene Nächste Schritte

1. **Architecture Design** – Detaillierte technische Architektur basierend auf diesem PRD
2. **UX Design** – Dashboard-Wireframes und User Flows
3. **Epics & Stories** – Herunterbrechen der FRs in implementierbare User Stories
4. **MVP Implementation** – Start mit Team-System und Paper Trading

### Dokument-Referenzen

- **Input:** `/docs/analysis/product-brief-v1.md`
- **Input:** `/docs/analysis/research/technical-ki-trading-plattform-research-2025-12-01.md`
- **Output:** Dieses Dokument (`/docs/prd.md`)

---

*Dieses PRD wurde am 2025-12-01 erstellt und dient als Grundlage für die Architektur- und Implementierungsphase.*
