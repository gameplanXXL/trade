// Type definitions for the Trading Platform

export type TeamStatus = 'active' | 'paused' | 'stopped' | 'warning' | 'critical'

export type AgentRole = 'crash_detector' | 'signal_analyst' | 'trader' | 'risk_manager'

export interface TeamInstance {
  id: string
  name: string
  status: TeamStatus
  budget: number
  currentPnL: number
  pnLPercent: number
  symbol: string
  isPaperTrading: boolean
}
