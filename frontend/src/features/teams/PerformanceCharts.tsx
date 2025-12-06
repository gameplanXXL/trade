import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

interface PerformanceChartsProps {
  teamId: number
}

export function PerformanceCharts({ teamId }: PerformanceChartsProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Performance Charts</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-center py-8 text-text-secondary">
          Performance charts for team #{teamId} will be displayed here.
          <div className="text-sm text-text-muted mt-2">
            This component will be implemented in a future story.
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
