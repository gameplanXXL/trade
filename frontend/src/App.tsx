import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Activity, TrendingUp, Shield, Zap } from 'lucide-react'

function App() {
  return (
    <div className="min-h-screen bg-background p-8">
      <div className="mx-auto max-w-6xl">
        {/* Header */}
        <header className="mb-12 text-center">
          <h1 className="mb-4 text-4xl font-bold tracking-tight text-text-primary">
            Trading Platform
          </h1>
          <p className="text-lg text-text-secondary">
            Multi-Agent Day-Trading Platform
          </p>
        </header>

        {/* Status Cards */}
        <div className="mb-8 grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-text-secondary">
                System Status
              </CardTitle>
              <Activity className="h-4 w-4 text-success" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-success">Online</div>
              <p className="text-xs text-text-muted">All systems operational</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-text-secondary">
                Active Teams
              </CardTitle>
              <TrendingUp className="h-4 w-4 text-accent" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">0</div>
              <p className="text-xs text-text-muted">No teams configured</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-text-secondary">
                Risk Level
              </CardTitle>
              <Shield className="h-4 w-4 text-warning" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-text-muted">--</div>
              <p className="text-xs text-text-muted">No active positions</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-text-secondary">
                Pipeline
              </CardTitle>
              <Zap className="h-4 w-4 text-text-muted" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-text-muted">Idle</div>
              <p className="text-xs text-text-muted">Waiting for configuration</p>
            </CardContent>
          </Card>
        </div>

        {/* Main Content Area */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Welcome to the Trading Platform</CardTitle>
            <CardDescription>
              This is a placeholder for the main dashboard. Configure your first team to get started.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <div className="mb-6 rounded-full bg-surface-elevated p-6">
                <TrendingUp className="h-12 w-12 text-accent" />
              </div>
              <h3 className="mb-2 text-xl font-semibold">No Teams Configured</h3>
              <p className="mb-6 max-w-md text-text-secondary">
                Create your first trading team to start monitoring the markets with AI-powered agents.
              </p>
              <Button>Create Team</Button>
            </div>
          </CardContent>
        </Card>

        {/* Footer */}
        <footer className="text-center text-sm text-text-muted">
          <p>Multi-Agent Trading Platform v0.1.0</p>
        </footer>
      </div>
    </div>
  )
}

export default App
