import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import type { Team } from '@/types'

interface TeamSettingsProps {
  team: Team
}

export function TeamSettings({ team }: TeamSettingsProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Team Settings</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-center py-8 text-text-secondary">
          Settings for team "{team.name}" will be displayed here.
          <div className="text-sm text-text-muted mt-2">
            This component will be implemented in a future story.
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
