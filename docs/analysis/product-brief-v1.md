# Product Brief: KI-Trading-Plattform

**Datum:** 2025-12-01
**Autor:** Christian
**Version:** 1.0 (Entwurf)
**Status:** Konzeptphase

---

## 1. Vision

Eine adaptive Multi-Agent Day-Trading-Plattform, die verschiedene KI-Technologien (LLM und klassisches Machine Learning) nutzt, um auf Basis aktueller Marktdaten automatisiert Handelsentscheidungen zu treffen. Das System lernt kontinuierlich aus den letzten 14 Tagen Kursdaten und passt sich an veränderte Marktbedingungen an.

---

## 2. Problemstellung

### Marktdynamik
- Erfolgreiche Trading-Strategien ändern sich schnell
- Statische Algorithmen verlieren über Zeit an Effektivität
- Manuelle Anpassung ist zeitaufwändig und fehleranfällig

### Technische Herausforderungen
- Einzelne KI-Modelle haben spezifische Stärken und Schwächen
- Keine universelle "beste" Strategie für alle Marktbedingungen
- Risikomanagement erfordert strikte Kontrollen

---

## 3. Lösung

### Kernansatz
Ein Multi-Agent-System, bei dem mehrere KI-Agenten mit unterschiedlichen Technologien, Parametern und Strategien parallel operieren. Jeder Agent wird kontinuierlich auf Basis aktueller Marktdaten (14-Tage-Fenster) trainiert.

### Differenzierung
| Aspekt | Traditionell | Diese Plattform |
|--------|--------------|-----------------|
| Strategie | Statisch | Adaptiv (14-Tage-Lernen) |
| Modelle | Ein Modell | Multi-Agent, Multi-Technologie |
| Risiko | Global | Pro Agent mit Budget-Isolation |
| Gewinn | Reinvestiert | Kappung & Lock-Mechanismus |

---

## 4. Kernfunktionen

### 4.1 Multi-Agent-Architektur

- **Parallele Agenten:** Mehrere KI-Agenten laufen gleichzeitig
- **Technologie-Mix:**
  - LLM-basierte Agenten (GPT, Claude, Open-Source LLMs)
  - Klassische ML-Modelle (LSTM, Reinforcement Learning, etc.)
- **Modell-Flexibilität:** Cloud-APIs und Self-Hosted Modelle (Ollama, vLLM)
- **Konfigurierbarkeit:** Unterschiedliche Parameter/Prompts pro Agent

### 4.2 Adaptives Lernen

- **Trainingsdaten:** Kursdaten der letzten 14 Tage
- **Kontinuierliches Re-Training:** Agenten passen sich an aktuelle Marktbedingungen an
- **Backtesting:** Validierung auf historischen Daten vor Live-Einsatz

### 4.3 Risikomanagement (pro Agent)

| Regel | Beschreibung | Beispiel |
|-------|--------------|----------|
| **Startbudget** | Initiales Trading-Kapital pro Agent | 10.000 € |
| **Max. Verlustgrenze** | Agent stoppt bei Unterschreitung | 25% → Stopp bei 7.500 € |
| **Gewinnkappung** | Aktives Trading-Kapital begrenzt | 150% → Max. 15.000 € aktiv |
| **Gewinn-Lock** | Überschuss wird "gesperrt" | Bei 20.000 € → 5.000 € gesperrt |
| **Trade-Sicherheit** | Automatische Absicherung | Stop Loss, Take Profit |

### 4.4 Virtueller Saldo pro Agent

Da mehrere Agenten auf einem physischen Konto operieren:
- Jeder Agent führt einen **eigenen virtuellen Saldo**
- Buchführung über Trades, Gewinne, Verluste pro Agent
- Unabhängige Regelanwendung (Verlustgrenze, Gewinnkappung)

### 4.5 Dual-Umgebung

| Umgebung | Zweck | Konto |
|----------|-------|-------|
| **Test-System** | Strategie-Validierung, Paper Trading | Demo-Konto |
| **Live-System** | Echtes Trading | Live-Konto |

### 4.6 Performance-Tracking

- Erfolgsmetriken pro Agent (Win-Rate, Profit/Loss, Sharpe Ratio, etc.)
- Vergleichsanalysen zwischen Agenten
- Historische Performance-Dashboards

---

## 5. Technische Anforderungen

### 5.1 Plattform & Hosting

| Komponente | Anforderung |
|------------|-------------|
| **Broker** | ICMarkets |
| **Trading-Plattform** | MetaTrader 5 |
| **Hosting** | VServer (Linux) |
| **Web-Interface** | Browser-basiertes Dashboard |

### 5.2 Integrationen

- **MT5 API:** Für Order-Execution und Marktdaten
- **LLM APIs:** OpenAI, Anthropic, lokale Modelle
- **ML Frameworks:** Python (TensorFlow/PyTorch/scikit-learn)
- **Datenbank:** Für Trade-Historie, Agent-Salden, Logs

### 5.3 Architektur-Überlegungen

```
┌─────────────────────────────────────────────────────────────┐
│                     Web Dashboard                            │
├─────────────────────────────────────────────────────────────┤
│                   Agent Orchestrator                         │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │
│  │Agent A  │  │Agent B  │  │Agent C  │  │Agent N  │        │
│  │(LLM)    │  │(LSTM)   │  │(RL)     │  │(...)    │        │
│  │Budget:  │  │Budget:  │  │Budget:  │  │Budget:  │        │
│  │10.000€  │  │10.000€  │  │10.000€  │  │10.000€  │        │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘        │
│       └────────────┴────────────┴────────────┘              │
│                         │                                    │
│              ┌──────────┴──────────┐                        │
│              │  Risk Manager       │                        │
│              │  - Verlustgrenzen   │                        │
│              │  - Gewinnkappung    │                        │
│              │  - Stop Loss/TP     │                        │
│              └──────────┬──────────┘                        │
├─────────────────────────┼───────────────────────────────────┤
│              ┌──────────┴──────────┐                        │
│              │  MT5 Connector      │                        │
│              └──────────┬──────────┘                        │
└─────────────────────────┼───────────────────────────────────┘
                          │
                   ┌──────┴──────┐
                   │  ICMarkets  │
                   └─────────────┘
```

---

## 6. Erfolgskriterien

### Kurzfristig (MVP)
- [ ] Ein Agent kann automatisiert traden (Test-Umgebung)
- [ ] Risikomanagement-Regeln werden eingehalten
- [ ] Performance-Tracking funktioniert

### Mittelfristig
- [ ] Mehrere Agenten laufen parallel
- [ ] Verschiedene KI-Technologien im Einsatz
- [ ] Web-Dashboard zur Überwachung

### Langfristig
- [ ] Nachweislich profitable Strategien identifiziert
- [ ] System läuft stabil im Live-Betrieb
- [ ] Skalierbar auf weitere Assets/Märkte

---

## 7. Offene Fragen (für Recherche)

1. **MT5-Integration:** Beste Methode für Python-Anbindung?
2. **LLM für Trading:** Welche Ansätze existieren? Wie prompting?
3. **ML-Modelle:** Welche Architekturen für Day-Trading geeignet?
4. **Self-Hosted LLMs:** Performance für Echtzeit-Entscheidungen?
5. **Bestehende Lösungen:** Open-Source Projekte als Basis?
6. **Regulatorik:** API-Limits bei ICMarkets? Rechtliche Aspekte?

---

## 8. Nächste Schritte

1. **Technische Recherche** zu allen offenen Fragen
2. Architektur-Entscheidungen treffen
3. MVP-Scope definieren
4. Implementierung starten

---

*Dieses Dokument dient als Grundlage für die weitere Produktentwicklung und wird nach der technischen Recherche aktualisiert.*
