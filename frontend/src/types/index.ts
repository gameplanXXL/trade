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
  current_budget?: number
  current_pnl: number
  pnl_percent: number
  is_paper_trading: boolean
  mode?: 'live' | 'paper'
  win_rate?: number
  max_drawdown?: number
  created_at: string
  updated_at: string
}

export interface Trade {
  id: number
  team_instance_id: number
  ticket: number
  symbol: string
  side: 'BUY' | 'SELL'
  size: number
  entry_price: number
  exit_price: number | null
  stop_loss: number | null
  take_profit: number | null
  pnl: number | null
  spread_cost: number
  status: 'open' | 'closed'
  opened_at: string
  closed_at: string | null
  magic_number: number
  comment: string | null
}

export interface TradeListMeta {
  timestamp: string
  total: number
  page: number
  page_size: number
}

export interface TradeListResponse {
  data: Trade[]
  meta: TradeListMeta
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
