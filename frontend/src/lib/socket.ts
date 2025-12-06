import { io, Socket } from 'socket.io-client'
import type { Trade, Alert, TeamStatusUpdate } from '../types'

type TeamStatusCallback = (data: TeamStatusUpdate) => void
type TradeCallback = (data: Trade) => void
type AlertCallback = (data: Alert) => void

class WebSocketClient {
  private socket: Socket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000 // Start with 1 second
  private maxReconnectDelay = 30000 // Max 30 seconds
  private isConnecting = false

  connect(): void {
    if (this.socket?.connected || this.isConnecting) {
      return
    }

    this.isConnecting = true
    const wsUrl = import.meta.env.VITE_WS_URL || 'http://localhost:8000'

    this.socket = io(wsUrl, {
      path: '/ws/socket.io',
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionAttempts: this.maxReconnectAttempts,
      reconnectionDelay: this.reconnectDelay,
      reconnectionDelayMax: this.maxReconnectDelay,
    })

    this.socket.on('connect', () => {
      console.log('WebSocket connected')
      this.isConnecting = false
      this.reconnectAttempts = 0
      this.reconnectDelay = 1000
    })

    this.socket.on('disconnect', (reason) => {
      console.log('WebSocket disconnected:', reason)
      this.isConnecting = false

      // Auto-reconnect with exponential backoff
      if (reason === 'io server disconnect') {
        // Server disconnected, manual reconnect required
        this.scheduleReconnect()
      }
    })

    this.socket.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error)
      this.isConnecting = false
      this.scheduleReconnect()
    })
  }

  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached')
      return
    }

    this.reconnectAttempts++
    const delay = Math.min(
      this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1),
      this.maxReconnectDelay
    )

    console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`)

    setTimeout(() => {
      this.connect()
    }, delay)
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect()
      this.socket = null
    }
    this.isConnecting = false
    this.reconnectAttempts = 0
  }

  joinTeam(teamId: number): void {
    if (!this.socket?.connected) {
      console.warn('Cannot join team: socket not connected')
      return
    }
    this.socket.emit('join_team', { team_id: teamId })
  }

  leaveTeam(teamId: number): void {
    if (!this.socket?.connected) {
      console.warn('Cannot leave team: socket not connected')
      return
    }
    this.socket.emit('leave_team', { team_id: teamId })
  }

  onTeamStatusChanged(callback: TeamStatusCallback): void {
    if (!this.socket) {
      console.warn('Cannot subscribe to team status: socket not initialized')
      return
    }
    this.socket.on('team:status_changed', callback)
  }

  onTradeExecuted(callback: TradeCallback): void {
    if (!this.socket) {
      console.warn('Cannot subscribe to trades: socket not initialized')
      return
    }
    this.socket.on('trade:executed', callback)
  }

  onAlert(callback: AlertCallback): void {
    if (!this.socket) {
      console.warn('Cannot subscribe to alerts: socket not initialized')
      return
    }
    this.socket.on('alert:warning', callback)
    this.socket.on('alert:crash', callback)
  }

  offTeamStatusChanged(callback?: TeamStatusCallback): void {
    if (!this.socket) return
    this.socket.off('team:status_changed', callback)
  }

  offTradeExecuted(callback?: TradeCallback): void {
    if (!this.socket) return
    this.socket.off('trade:executed', callback)
  }

  offAlert(callback?: AlertCallback): void {
    if (!this.socket) return
    this.socket.off('alert:warning', callback)
    this.socket.off('alert:crash', callback)
  }

  isConnected(): boolean {
    return this.socket?.connected ?? false
  }
}

// Singleton instance
export const wsClient = new WebSocketClient()

export default WebSocketClient
