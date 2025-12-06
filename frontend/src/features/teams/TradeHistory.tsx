import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

interface TradeHistoryProps {
  teamId: number
}

export function TradeHistory({ teamId }: TradeHistoryProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Trade History</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-center py-8 text-text-secondary">
          Trade history for team #{teamId} will be displayed here.
          <div className="text-sm text-text-muted mt-2">
            This component will be implemented in a future story.
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
