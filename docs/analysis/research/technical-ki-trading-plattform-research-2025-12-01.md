---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8]
inputDocuments: ["/docs/analysis/product-brief-v1.md"]
workflowType: "research"
lastStep: 8
research_type: "technical"
research_topic: "KI-basierte Multi-Agent Day-Trading-Plattform (MT5/ICMarkets)"
research_goals: "Technische Machbarkeit, Implementierungsansätze, Architektur-Entscheidungen"
user_name: "Christian"
date: "2025-12-01"
current_year: "2025"
web_research_enabled: true
source_verification: true
status: "Abgeschlossen"
---

# Technische Recherche: KI-basierte Multi-Agent Day-Trading-Plattform

**Datum:** 2025-12-01
**Autor:** Christian
**Recherche-Typ:** Technisch
**Status:** ✅ Abgeschlossen

---

## Executive Summary

Diese technische Recherche untersucht die Machbarkeit einer KI-basierten Multi-Agent Day-Trading-Plattform für MetaTrader 5 und ICMarkets. Die Analyse zeigt, dass alle technischen Komponenten verfügbar und integrierbar sind. Besonders vielversprechend sind die Kombinationen aus LLM-basierten Agenten und klassischen ML-Modellen (Hybrid-Ansatz), unterstützt durch etablierte Multi-Agent-Frameworks wie LangGraph oder TradingAgents.

**Kernerkenntnisse:**
- ✅ MT5-Python-Integration ist ausgereift und produktionsreif
- ✅ ICMarkets erlaubt automatisiertes Trading ohne Einschränkungen
- ✅ Multi-LLM-Systeme zeigen überlegene Performance gegenüber Einzelmodellen
- ✅ Self-Hosted LLMs sind für Trading praktikabel (vLLM empfohlen)
- ⚠️ Klassisches Backtesting ist bei adaptiven Systemen nur bedingt aussagekräftig
- 💡 Walk-Forward-Analyse und Combinatorial Purged Cross-Validation (CPCV) empfohlen

---

## Inhaltsverzeichnis

1. [MT5-Python-Integration](#1-mt5-python-integration)
2. [KI/ML für Trading](#2-kiml-für-trading)
3. [Multi-Agent-Frameworks](#3-multi-agent-frameworks)
4. [Self-Hosted LLMs](#4-self-hosted-llms)
5. [Backtesting bei adaptiven Systemen](#5-backtesting-bei-adaptiven-systemen)
6. [Open-Source Trading-Bots & Frameworks](#6-open-source-trading-bots--frameworks)
7. [ICMarkets-Spezifika](#7-icmarkets-spezifika)
8. [Architektur-Empfehlungen](#8-architektur-empfehlungen)
9. [Technologie-Stack-Empfehlung](#9-technologie-stack-empfehlung)
10. [Risiken und Herausforderungen](#10-risiken-und-herausforderungen)
11. [Quellen](#11-quellen)

---

## 1. MT5-Python-Integration

### Offizielle Bibliothek: MetaTrader5

Die offizielle Python-Bibliothek von MetaQuotes ermöglicht direkte Kommunikation mit dem MT5-Terminal via Interprozesskommunikation.

**Capabilities:**
- Verbindung zu MT5-Konten (Demo und Live)
- Echtzeit- und historische Marktdaten (Quotes, Bars, Ticks)
- Order-Platzierung und -Management
- Positions- und Kontoinformationen

**Installation:**
```bash
pip install MetaTrader5
```

**Anforderungen:**
- MT5-Terminal muss lokal laufen
- "Algorithmisches Trading erlauben" in MT5 aktivieren (Tools → Options → Expert Advisors)

### Alternative Bibliotheken

| Bibliothek | Beschreibung | Besonderheit |
|------------|--------------|--------------|
| **PythonMetaTrader5** | Produktionsreifer Wrapper (PyPI, Sept. 2025) | Saubere SL/TP-Handhabung |
| **aiomql** | Asynchrone Bibliothek | Ideal für Multi-Agent-Systeme, pandas-ta kompatibel |
| **REST API (metatraderapi.cloud)** | Externe API-Lösung | Unabhängig vom lokalen MT5-Terminal |

### Empfehlung für dein Projekt

**Primär:** `aiomql` - Die asynchrone Natur passt perfekt zu Multi-Agent-Architekturen, wo mehrere Agenten parallel Orders platzieren.

**Fallback:** Offizielle `MetaTrader5` Bibliothek für maximale Stabilität.

**Konfidenz:** [Hoch] - Gut dokumentiert, aktiv maintained, produktionserprobt.

---

## 2. KI/ML für Trading

### 2.1 LLM-basierte Trading-Agenten (2025)

#### Claude für Trading
- **Claude for Financial Services** (Juli 2025): Compliance-Automatisierung, Audit-Trails
- Stärken: Bessere Code-Generierung (pandas, NumPy), Multi-Step-Reasoning
- Claude benötigt ~8 Iterationen für Strategieentwicklung vs. ~20 bei GPT-4o

#### Multi-LLM Veto-Systeme
Ein vielversprechender Ansatz: Mehrere LLMs (DeepSeek-Reasoner, Claude Opus 4, GPT-4o, Grok-4) generieren einen Ensemble-Konsens-Score als qualitative Risiko-Filterung.

**Berichtete Performance (Walk-Forward 2023-2025):**
| Asset | Return | Sharpe Ratio |
|-------|--------|--------------|
| BTC/USD | 1.842% | 6.08 |
| ETH/USD | 1.758% | 6.20 |
| SOL/USD | 1.186% | 5.10 |

⚠️ **Hinweis:** Diese Ergebnisse stammen aus einem einzelnen Projekt und sollten mit Vorsicht betrachtet werden.

#### Kommerzielle Implementierungen
- **Bitrue** (Nov. 2025): Nutzer wählen zwischen GPT-5, Gemini 2.5 Pro, Claude Sonnet 4.5, Grok 4, DeepSeek v3.1, Qwen3-Max
- Erfolgsraten: GPT-5 (74%), Gemini 2.5 Pro (71%)

### 2.2 Klassisches Machine Learning

#### LSTM-Netzwerke
- Sliding-Window-Ansatz (60 Tage In-Sample → Tag 61 Prediction)
- LSTM-Hybride: 23.27% RMSE-Verbesserung, bis zu 1978% Portfolio-Returns

#### Reinforcement Learning
- **CLSTM-PPO Modell:** LSTM für Feature-Extraktion → PPO-Agent für Trading
- **GPT-4o + DDQN:** Sharpe Ratio von 2.43 (übertrifft klassische RL-Modelle allein)

#### Empfohlene Hybrid-Architektur
```
┌─────────────────────────────────────────────┐
│           LLM Layer (Qualitativ)            │
│  - Sentiment-Analyse                        │
│  - News-Interpretation                      │
│  - Risiko-Veto                              │
├─────────────────────────────────────────────┤
│           ML Layer (Quantitativ)            │
│  - LSTM für Kursprognose                    │
│  - RL für Positionsgrößen                   │
│  - Technische Indikatoren                   │
└─────────────────────────────────────────────┘
```

**Konfidenz:** [Hoch] - Vielfach in Forschung und Praxis validiert.

---

## 3. Multi-Agent-Frameworks

### Framework-Vergleich (2025)

| Framework | Stärke | Ansatz | Trading-Eignung |
|-----------|--------|--------|-----------------|
| **LangGraph** | Marktführer, reifes Ökosystem | Graph-basiert, stateful | ⭐⭐⭐⭐⭐ |
| **AutoGen** | Microsoft, asynchron | Konversations-basiert | ⭐⭐⭐⭐ |
| **CrewAI** | Schnell, unabhängig | Rollen-basiert | ⭐⭐⭐⭐ |
| **TradingAgents** | Speziell für Trading | Multi-Agent LLM | ⭐⭐⭐⭐⭐ |

### TradingAgents (Spezialisiert)

Ein Open-Source Multi-Agent-Framework, das die Dynamik echter Trading-Firmen nachbildet:

**Rollen:**
1. Fundamentals Analyst
2. Sentiment Analyst
3. News Analyst
4. Technical Analyst
5. Researcher (Bull + Bear)
6. Trader
7. Risk Manager

**Technologie:** LangGraph-basiert, nutzt o1-preview + gpt-4o

**Performance:** Übertrifft Baseline-Modelle in Cumulative Returns, Sharpe Ratio und Max Drawdown.

### Empfehlung

**Für dein Projekt:** LangGraph als Basis + Architektur-Inspiration von TradingAgents

**Begründung:**
- LangGraph bietet maximale Flexibilität
- TradingAgents zeigt bewährte Agent-Rollen
- Beide sind Open Source und aktiv maintained

**Konfidenz:** [Hoch] - Etablierte Frameworks mit Enterprise-Adoption.

---

## 4. Self-Hosted LLMs

### Ollama vs. vLLM

| Kriterium | Ollama | vLLM |
|-----------|--------|------|
| **Zielgruppe** | Entwickler, Single-User | Produktion, Multi-User |
| **Throughput** | 1-3 req/sec | 120-160 req/sec |
| **Time-to-First-Token** | Höher | 50-80ms |
| **Parallelität** | Max. 4 Requests | Continuous Batching |
| **Setup-Komplexität** | Niedrig | Mittel |

**Benchmark (Red Hat, Berkeley):** vLLM erreicht bis zu 10x höheren Throughput bei gleicher Hardware.

### vLLM Features (2025)
- **PagedAttention:** 50%+ weniger Speicherfragmentierung
- **vLLM V1 (Jan. 2025):** 1.7x Speedup, Zero-Overhead Prefix Caching
- Quantisierung für reduzierten GPU-Speicher

### Empfehlung für Trading

**vLLM** ist die klare Empfehlung für dein Projekt:
- Niedrige Latenz kritisch für Trading-Entscheidungen
- Multi-Agent-System generiert viele parallele Requests
- Quantisierte Modelle (z.B. Llama 3 8B Q4) für schnelle Inferenz

**Hardware-Anforderung:**
- Minimum: 1x RTX 3090/4090 (24GB VRAM) oder A100
- Empfohlen: 2x RTX 4090 oder 1x A100 80GB für größere Modelle

**Konfidenz:** [Hoch] - Benchmark-Daten von Red Hat und Berkeley.

---

## 5. Backtesting bei adaptiven Systemen

### Das Problem

Bei adaptiven KI-Systemen, die sich alle 14 Tage neu trainieren, ist klassisches Backtesting problematisch:
- **Overfitting-Risiko:** Strategie performt historisch perfekt, versagt live
- **Regime-Änderungen:** Märkte ändern sich schneller als Re-Training
- **Look-Ahead Bias:** ML-Modelle können unbeabsichtigt zukünftige Daten "sehen"

### Empfohlene Alternativen

#### 1. Walk-Forward Optimization (WFO)
```
In-Sample (Training) → Out-of-Sample (Validation) → Rollen → Wiederholen
```
- Reduziert Overfitting durch Rolling-Window
- **Limitation:** Reagiert mit Verzögerung auf Regime-Änderungen

#### 2. Combinatorial Purged Cross-Validation (CPCV)
- **Überlegene Methode** laut aktueller Forschung
- Niedrigere "Probability of Backtest Overfitting" (PBO)
- Bessere "Deflated Sharpe Ratio" (DSR)
- Varianten: Bagged CPCV, Adaptive CPCV

#### 3. Echtzeit-Paper-Trading
- 2025-Trend: Grenze zwischen Backtesting und Live-Trading verschwimmt
- Strategien auf Live-Daten ohne echtes Kapital testen
- Kontinuierliche Feedback-Schleife

### Validierungs-Richtlinien

| Kriterium | Schwellenwert |
|-----------|---------------|
| Out-of-Sample vs. In-Sample Degradation | < 30% |
| Profitabilität über verschiedene Marktbedingungen | Konsistent |
| "Perfekte" Backtests | Mit extremem Misstrauen behandeln |

### Empfehlung für dein Projekt

1. **Primär:** Walk-Forward-Analyse mit 14-Tage Rolling Windows (passend zu deinem Re-Training-Zyklus)
2. **Zusätzlich:** CPCV für kritische Strategie-Validierung
3. **Kontinuierlich:** Paper-Trading auf Demo-Konto vor Live-Einsatz
4. **Akzeptanz:** Backtesting als Hygiene-Check, nicht als Erfolgsgarantie

**Konfidenz:** [Hoch] - Wissenschaftlich fundiert, 2025-Forschung.

---

## 6. Open-Source Trading-Bots & Frameworks

### Für Krypto (adaptierbar für Forex)

| Framework | Beschreibung | KI-Integration | GitHub |
|-----------|--------------|----------------|--------|
| **Freqtrade** | Größte Community | FreqAI (ML-Optimierung) | [github.com/freqtrade](https://github.com/freqtrade/freqtrade) |
| **Jesse** | Python-fokussiert | GPT-Assistent | [github.com/jesse-ai](https://github.com/jesse-ai/jesse) |
| **OctoBot** | Modular | GPT-Strategie-Hilfe | - |

### Für LLM-Trading

| Projekt | Fokus | Besonderheit |
|---------|-------|--------------|
| **TradingAgents** | Multi-Agent LLM | Simulates Trading Firm | [github.com/TauricResearch](https://github.com/TauricResearch/TradingAgents) |
| **FinRL** | Deep RL | Quantitative Finance | AI4Finance Foundation |
| **FinGPT** | Financial LLM | Trained Models on HuggingFace | AI4Finance Foundation |
| **FinMem** | LLM + Memory | Layered Memory Design | - |

### MT5-spezifische Projekte

- **how_to_build_a_metatrader5_trading_bot_expert_advisor** - Educational mit Videos
- **aiomql** - Async Framework für MT5

### Empfehlung

**Build vs. Buy:** Eigene Entwicklung auf Basis von:
- **LangGraph** (Agent-Orchestrierung)
- **aiomql** (MT5-Integration)
- **Architektur-Inspiration** von TradingAgents

**Begründung:** Freqtrade/Jesse sind primär auf Krypto ausgerichtet. Für MT5/Forex ist eine Custom-Lösung flexibler.

**Konfidenz:** [Mittel-Hoch] - Abhängig von Entwicklungsressourcen.

---

## 7. ICMarkets-Spezifika

### Automatisiertes Trading

✅ **Vollständig erlaubt** - Keine Trading-Einschränkungen

**Features:**
- Expert Advisors (EAs) unterstützt
- Scalping und High-Frequency-Trading erlaubt
- Keine Mindest-Order-Distanz
- Freeze Level: 0
- Hedging erlaubt (kein FIFO)

### Server-Infrastruktur

- **Standort:** Equinix NY4 Data Center (New York)
- **Latenz:** Optimal für algorithmisches Trading
- Cross-Connected für schnelle Execution

### Kontotypen

| Typ | Spreads | Kommission |
|-----|---------|------------|
| Raw Pricing | Ab 0.0 Pips | $3.50/Lot |
| Standard | Ab 1.0 Pips | Keine |

**Empfehlung:** Raw Pricing Account für algorithmisches Trading (engere Spreads wichtiger als Kommissionsersparnis bei Day-Trading).

**Konfidenz:** [Hoch] - Offizielle ICMarkets-Dokumentation.

---

## 8. Architektur-Empfehlungen

### Gesamtarchitektur

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           Web Dashboard (React/Vue)                      │
│                    - Agent-Status, Performance-Charts                    │
│                    - Konfiguration, Logs                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                              FastAPI Backend                             │
│                    - REST API für Dashboard                              │
│                    - WebSocket für Echtzeit-Updates                      │
├─────────────────────────────────────────────────────────────────────────┤
│                         Agent Orchestrator (LangGraph)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Agent A    │  │   Agent B    │  │   Agent C    │  │   Agent N    │ │
│  │  (LLM-based) │  │ (LSTM-based) │  │  (RL-based)  │  │   (...)      │ │
│  │              │  │              │  │              │  │              │ │
│  │ Budget: 10k€ │  │ Budget: 10k€ │  │ Budget: 10k€ │  │ Budget: Xk€  │ │
│  │ Locked: 0€   │  │ Locked: 0€   │  │ Locked: 0€   │  │ Locked: Y€   │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘ │
│         └─────────────────┼─────────────────┼─────────────────┘         │
│                           │                 │                            │
├───────────────────────────┼─────────────────┼────────────────────────────┤
│                    Risk Manager (Global)                                 │
│        - Stop Loss / Take Profit Enforcement                             │
│        - Budget-Limits pro Agent                                         │
│        - Gewinn-Lock Mechanismus                                         │
│        - Gesamt-Exposure-Kontrolle                                       │
├───────────────────────────┼─────────────────┼────────────────────────────┤
│                    Virtual Ledger (PostgreSQL)                           │
│        - Virtueller Saldo pro Agent                                      │
│        - Trade-Historie                                                  │
│        - Gewinn-Lock-Tracking                                            │
├───────────────────────────┼─────────────────┼────────────────────────────┤
│                    MT5 Connector (aiomql)                                │
│        - Async Order Execution                                           │
│        - Market Data Feed                                                │
│        - Position Sync                                                   │
├───────────────────────────┼─────────────────┼────────────────────────────┤
│                    ICMarkets (Real Account)                              │
└─────────────────────────────────────────────────────────────────────────┘
```

### Komponenten-Details

#### 1. Agent Orchestrator
- **Framework:** LangGraph
- **Aufgabe:** Agent-Lifecycle, Kommunikation, Scheduling
- **Re-Training:** Automatisch alle 14 Tage basierend auf aktuellen Kursdaten

#### 2. Risk Manager
- Zentrale Komponente für ALLE Agenten
- Implementiert die Budget-Regeln (25% Max-Verlust, 150% Gewinn-Kappung)
- Kann Agent-Orders ablehnen oder modifizieren

#### 3. Virtual Ledger
- Jeder Agent hat eigenen virtuellen Saldo
- Physisch nur ein ICMarkets-Konto
- Reconciliation zwischen Virtual Ledger und realem Konto

#### 4. LLM Services
- **Cloud:** OpenAI, Anthropic für komplexe Analysen
- **Self-Hosted (vLLM):** Für latenz-kritische Entscheidungen

---

## 9. Technologie-Stack-Empfehlung

### Backend

| Komponente | Technologie | Begründung |
|------------|-------------|------------|
| Sprache | Python 3.11+ | Ökosystem, MT5-Support |
| Web Framework | FastAPI | Async, WebSocket, OpenAPI |
| Agent Framework | LangGraph | Flexibel, Multi-Agent-native |
| MT5 Integration | aiomql | Async, Feature-reich |
| Datenbank | PostgreSQL + TimescaleDB | Zeitreihen-optimiert |
| Cache | Redis | State, Message Queue |
| Task Queue | Celery oder Dramatiq | Scheduled Tasks (Re-Training) |

### KI/ML

| Komponente | Technologie | Begründung |
|------------|-------------|------------|
| LLM (Cloud) | Claude API, OpenAI API | Qualität |
| LLM (Self-Hosted) | vLLM + Llama 3 | Latenz, Kosten |
| ML Framework | PyTorch | Flexibilität |
| Time Series | PyTorch Forecasting, TSAI | LSTM, Transformer |
| RL | Stable-Baselines3 | PPO, DDQN |
| Indicators | pandas-ta | 300+ Indikatoren |

### Frontend

| Komponente | Technologie |
|------------|-------------|
| Framework | React oder Vue 3 |
| Charts | TradingView Lightweight Charts |
| Echtzeit | WebSocket |

### Infrastruktur

| Komponente | Empfehlung |
|------------|------------|
| VServer | Hetzner Dedicated (AX161) oder Cloud GPU |
| GPU | RTX 4090 oder A100 (für vLLM) |
| OS | Ubuntu 22.04 LTS |
| Container | Docker + Docker Compose |
| Monitoring | Prometheus + Grafana |

---

## 10. Risiken und Herausforderungen

### Technische Risiken

| Risiko | Wahrscheinlichkeit | Impact | Mitigation |
|--------|-------------------|--------|------------|
| MT5-Terminal-Instabilität | Mittel | Hoch | Watchdog, Auto-Restart |
| LLM-Halluzinationen | Mittel | Hoch | Multi-LLM Veto, Fact-Checking |
| Latenz-Probleme | Mittel | Mittel | vLLM, Co-Location |
| API-Rate-Limits | Niedrig | Mittel | Caching, Self-Hosted LLMs |

### Finanzielle Risiken

| Risiko | Mitigation |
|--------|------------|
| Drawdown | 25% Max-Verlust-Regel (bereits geplant) |
| Korrelierte Agent-Verluste | Diversifikation der Strategien |
| Technischer Ausfall während Trade | Automatische SL/TP auf MT5-Seite |

### Regulatorische Risiken

| Aspekt | Status |
|--------|--------|
| Automatisiertes Trading | ✅ Von ICMarkets erlaubt |
| Persönliches Trading | ✅ Keine Lizenz erforderlich |
| Für Dritte handeln | ⚠️ Lizenzpflicht prüfen |

---

## 11. Quellen

### MT5-Integration
- [MQL5 Python Integration Dokumentation](https://www.mql5.com/en/docs/python_metatrader5)
- [MetaTrader API Complete Guide 2025](https://metatraderapi.cloud/guides/metatrader-api-complete-guide/)
- [aiomql GitHub](https://github.com/Ichinga-Samuel/aiomql)
- [PythonMetaTrader5 PyPI](https://pypi.org/project/PythonMetaTrader5/)

### LLM Trading
- [Claude 4.1 for Trading Guide](https://blog.pickmytrade.trade/claude-4-1-for-trading-guide/)
- [Multi-LLM Cryptocurrency Trading Case Study](https://medium.com/@frankmorales_91352/the-evolution-of-algorithmic-trading-a-case-study-of-a-multi-llm-enhanced-cryptocurrency-trading-2941f6844068)
- [Bitrue AI Trading Feature (SiliconANGLE)](https://siliconangle.com/2025/11/19/crypto-exchange-bitrue-launches-ai-powered-trading-feature-using-gpt-5-gemini-claude/)
- [TradingAgents GitHub](https://github.com/TauricResearch/TradingAgents)

### ML für Trading
- [LSTM Stock Market Prediction (ArXiv)](https://arxiv.org/html/2505.05325v1)
- [AI and ML for Stock Market 2025 (AInvest)](https://www.ainvest.com/news/harnessing-ai-machine-learning-stock-market-prediction-2025-analysis-language-models-deep-learning-short-medium-term-forecasting-2512/)
- [Deep LSTM with RL for FX Trading (MDPI)](https://www.mdpi.com/2076-3417/9/20/4460)

### Multi-Agent Frameworks
- [Top AI Agent Frameworks 2025 (Medium)](https://medium.com/@iamanraghuvanshi/agentic-ai-3-top-ai-agent-frameworks-in-2025-langchain-autogen-crewai-beyond-2fc3388e7dec)
- [CrewAI vs LangGraph vs AutoGen (DataCamp)](https://www.datacamp.com/tutorial/crewai-vs-langgraph-vs-autogen)
- [LangGraph Multi-Agent Workflows](https://blog.langchain.com/langgraph-multi-agent-workflows/)

### Self-Hosted LLMs
- [Ollama vs vLLM Performance (Red Hat)](https://developers.redhat.com/articles/2025/08/08/ollama-vs-vllm-deep-dive-performance-benchmarking)
- [Local LLM Hosting 2025 Guide](https://www.glukhov.org/post/2025/11/hosting-llms-ollama-localai-jan-lmstudio-vllm-comparison/)
- [vLLM GitHub](https://github.com/vllm-project/vllm)

### Backtesting
- [Backtest Overfitting ML Era (ScienceDirect)](https://www.sciencedirect.com/science/article/abs/pii/S0950705124011110)
- [Walk-Forward Optimization (QuantInsti)](https://blog.quantinsti.com/walk-forward-optimization-introduction/)
- [Walk-Forward Analysis Deep Dive (IBKR)](https://www.interactivebrokers.com/campus/ibkr-quant-news/the-future-of-backtesting-a-deep-dive-into-walk-forward-analysis/)

### Open-Source Trading
- [Freqtrade GitHub](https://github.com/freqtrade/freqtrade)
- [Jesse Trading](https://jesse.trade/)
- [AI in Finance Awesome List](https://github.com/georgezouq/awesome-ai-in-finance)

### ICMarkets
- [ICMarkets MT5 Plattform](https://www.icmarkets.com/global/en/forex-trading-platform-metatrader/metatrader-5)
- [ICMarkets Automated Trading Systems (BrokerChooser)](https://brokerchooser.com/broker-reviews/ic-markets-review/automated-trading-systems)

---

## Nächste Schritte

1. **Architektur-Design** detaillieren (PRD erstellen)
2. **MVP-Scope** definieren (einzelner Agent, Paper-Trading)
3. **Technologie-Prototyp** bauen (MT5-Verbindung, LangGraph-Setup)
4. **Paper-Trading** auf ICMarkets Demo-Konto

---

*Recherche abgeschlossen: 2025-12-01*
