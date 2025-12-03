# Functional Requirements Inventory

## Team-Konfiguration
- **FR1:** User kann Team-Templates als YAML-Dateien definieren
- **FR2:** User kann Agent-Rollen mit Parametern in Team-Templates konfigurieren
- **FR3:** User kann Pipeline-Abläufe für Teams definieren (sequenzielle Schritte)
- **FR4:** User kann Override-Regeln mit Prioritäten für Teams definieren
- **FR5:** System validiert YAML-Konfiguration beim Laden und meldet Fehler

## Team-Instanz-Management
- **FR6:** User kann Team-Instanzen aus Templates erstellen
- **FR7:** User kann Symbole für Team-Instanzen konfigurieren (z.B. EUR/USD)
- **FR8:** User kann Budget für Team-Instanzen festlegen
- **FR9:** User kann Team-Instanzen starten und stoppen
- **FR10:** User kann Team-Instanzen im Paper-Trading-Modus betreiben
- **FR11:** System speichert Team-Instanzen persistent in der Datenbank

## Agent-Rollen
- **FR12:** System stellt CrashDetector-Rolle bereit (überwacht Crash-Signale)
- **FR13:** System stellt LLMSignalAnalyst-Rolle bereit (generiert Trading-Signale via LLM)
- **FR14:** System stellt Trader-Rolle bereit (führt Orders aus)
- **FR15:** System stellt RiskManager-Rolle bereit (validiert Orders, überwacht Drawdown)
- **FR16:** Jede Agent-Rolle akzeptiert konfigurierbare Parameter

## Pipeline & Regeln
- **FR17:** System führt Pipeline-Schritte sequenziell aus
- **FR18:** System evaluiert Override-Regeln nach Priorität vor Pipeline-Schritten
- **FR19:** CrashDetector kann Status "NORMAL", "WARNING" oder "CRASH" setzen
- **FR20:** Bei Status "CRASH" schließt Trader automatisch alle Positionen
- **FR21:** Bei Status "WARNING" wechselt Trader in HOLD-Modus (keine neuen Trades)
- **FR22:** RiskManager kann Orders ablehnen (REJECT) oder genehmigen (APPROVE)

## Trading Execution
- **FR23:** System verbindet sich mit MT5/ICMarkets Demo-Konto
- **FR24:** System empfängt Echtzeit-Kursdaten von MT5
- **FR25:** Trader kann BUY- und SELL-Orders platzieren
- **FR26:** System setzt automatisch Trailing Stoploss bei jeder Order
- **FR27:** System simuliert Order-Execution im Paper-Trading-Modus
- **FR28:** System führt virtuelle Buchführung pro Team-Instanz (Budget, P/L)

## Performance Analytics
- **FR29:** System berechnet Gesamt-P/L pro Team-Instanz
- **FR30:** System berechnet P/L pro Symbol
- **FR31:** System berechnet Win-Rate (Gewinn-Trades / Gesamt-Trades)
- **FR32:** System berechnet Sharpe Ratio
- **FR33:** System berechnet maximalen Drawdown
- **FR34:** System speichert Performance-Historie (täglich, wöchentlich, monatlich)
- **FR35:** System trackt Agent-Aktivität (Signale, Warnungen, Ablehnungen)

## Dashboard - Übersicht
- **FR36:** User sieht Team-Instanz-Status auf einen Blick (aktiv, pausiert, gestoppt)
- **FR37:** User sieht Gesamt-P/L und aktuelle Performance-Metriken
- **FR38:** User sieht Warnungen und Alerts (gelb für WARNING, rot für CRASH)
- **FR39:** Dashboard aktualisiert sich in Echtzeit via WebSocket

## Dashboard - Team-Details
- **FR40:** User kann Team-Instanz-Details anzeigen
- **FR41:** User sieht Trade-Historie mit allen ausgeführten Orders
- **FR42:** User sieht Timeline der Agent-Aktionen
- **FR43:** User sieht Performance-Charts (P/L-Verlauf, Drawdown)
- **FR44:** User sieht Agent-Statistiken (Analyst-Confidence, RiskManager-Entscheidungen)

## Dashboard - Konfiguration
- **FR45:** User kann neue Team-Instanz über UI erstellen
- **FR46:** User kann Team-Instanz pausieren und fortsetzen
- **FR47:** User kann Team-Instanz permanent stoppen
- **FR48:** User kann Symbole und Budget bei Erstellung festlegen

## Sicherheit & Datenschutz
- **FR49:** System speichert Credentials verschlüsselt (MT5, LLM-APIs)
- **FR50:** Dashboard erfordert Authentifizierung (Login)
- **FR51:** System schreibt keine sensiblen Daten in Logs

## Fehlerbehandlung
- **FR52:** System versucht automatisch Reconnect bei MT5-Verbindungsabbruch
- **FR53:** System loggt alle Fehler mit Kontext für Debugging
- **FR54:** Bei LLM-API-Fehler verwendet System Retry-Logic

---
