---
epic: 008
story: 04
title: "Performance-Charts mit TradingView"
status: completed
story_points: 5
covers: [FR43]
---

## Story 8.4: Performance-Charts mit TradingView

Als Operator,
möchte ich Performance-Charts sehen,
damit ich Trends visuell analysieren kann.

**Acceptance Criteria:**

**Given** Team-Detail-Ansicht und Performance-Historie
**When** ich PerformanceCharts implementiere
**Then** existiert `src/features/analytics/PerformanceCharts.tsx`:
```tsx
import { createChart } from 'lightweight-charts';

export function PerformanceCharts({ teamId }: { teamId: number }) {
  const { history } = usePerformanceHistory(teamId);
  const chartRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const chart = createChart(chartRef.current!, {
      layout: { background: { color: '#0a0e1a' } },
      // ...
    });

    const pnlSeries = chart.addLineSeries({ color: '#10b981' });
    pnlSeries.setData(history.map(h => ({ time: h.timestamp, value: h.pnl })));

    return () => chart.remove();
  }, [history]);

  return (
    <div className="space-y-4">
      <div ref={chartRef} className="h-64" />
      <DrawdownChart data={history} />
    </div>
  );
}
```

**And** Charts:
  - P/L-Verlauf (Line Chart)
  - Drawdown-Verlauf (Area Chart, invertiert)
  - Win-Rate über Zeit (optional)

**And** Timeframe-Selector: 1D, 1W, 1M, All



## Tasks

- [x] TradingView Chart Setup
- [x] P/L Line Chart
- [x] Drawdown Area Chart
- [x] Timeframe Selector
- [x] Responsive Sizing
**Technical Notes:**
- TradingView Lightweight Charts
- Dark-Theme matching UX Design
- Responsive Chart-Größe

**Prerequisites:** Story 8.1, Story 6.2

