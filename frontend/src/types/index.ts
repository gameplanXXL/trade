// Type definitions for the Trading Platform

export type TeamStatus = 'active' | 'paused' | 'stopped' | 'warning' | 'critical'

export type AgentRole = 'crash_detector' | 'signal_analyst' | 'trader' | 'risk_manager'

export type AlertSeverity = 'warning' | 'crash' | 'info'

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

export interface Team {
  id: number
  name: string
  status: TeamStatus
  symbol: string
  budget: number
  current_pnl: number
  pnl_percent: number
  is_paper_trading: boolean
  created_at: string
  updated_at: string
}

export interface Trade {
  id: number
  team_id: number
  symbol: string
  action: 'BUY' | 'SELL'
  volume: number
  price: number
  executed_at: string
  profit?: number
}

export interface Alert {
  id: string
  team_id: number
  severity: AlertSeverity
  message: string
  timestamp: string
}

export interface TeamStatusUpdate {
  team_id: number
  status: TeamStatus
  current_pnl?: number
  pnl_percent?: number
}
