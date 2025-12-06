import type { Team } from '@/types'
import { Card, CardContent } from '@/components/ui/card'
import { TrendingUp } from 'lucide-react'
import { InstanceCard } from './InstanceCard'
import { useMemo } from 'react'

interface TeamGridProps {
  teams: Team[]
}

/**
 * TeamGrid Component
 *
 * Displays team instance cards with proportional sizing:
 * - Desktop: Auto-fit grid with proportional sizes based on budget
 * - Mobile: Stack (1 column)
 * - Critical instances sorted to top
 */
export function TeamGrid({ teams }: TeamGridProps) {
  // Calculate total budget for proportional sizing
  const totalBudget = useMemo(() => {
    return teams.reduce((sum, team) => {
      const budget = team.current_budget ?? team.budget
      return sum + budget
    }, 0)
  }, [teams])

  // Sort teams: critical status first, then by status severity
  const sortedTeams = useMemo(() => {
    const statusPriority = {
      critical: 0,
      warning: 1,
      stopped: 2,
      paused: 3,
      active: 4,
    }

    return [...teams].sort((a, b) => {
      const priorityA = statusPriority[a.status] ?? 999
      const priorityB = statusPriority[b.status] ?? 999
      return priorityA - priorityB
    })
  }, [teams])

  // Handle team actions
  const handleAction = (teamId: number, action: 'details' | 'pause' | 'close') => {
    // TODO: Implement action handlers
    console.log(`Team ${teamId}: ${action}`)
  }

  if (teams.length === 0) {
    return (
      <div className="mx-auto max-w-7xl px-6 py-12">
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12 text-center">
            <div className="mb-6 rounded-full bg-surface-elevated p-6">
              <TrendingUp className="h-12 w-12 text-accent" />
            </div>
            <h3 className="mb-2 text-xl font-semibold text-text-primary">
              No Teams Configured
            </h3>
            <p className="max-w-md text-text-secondary">
              Create your first trading team to start monitoring the markets
              with AI-powered agents.
            </p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-7xl px-6 py-8">
      <h2 className="mb-6 text-2xl font-bold text-text-primary">Active Teams</h2>

      {/* Responsive Grid with proportional sizing */}
      <div className="grid auto-rows-fr grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
        {sortedTeams.map((team) => (
          <InstanceCard
            key={team.id}
            team={team}
            totalBudget={totalBudget}
            onAction={(action) => handleAction(team.id, action)}
          />
        ))}
      </div>
    </div>
  )
}

