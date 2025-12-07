import { io, Socket } from 'socket.io-client'
import type { Trade, Alert, TeamStatusUpdate } from '../types'

type TeamStatusCallback = (data: TeamStatusUpdate) => void
type TradeCallback = (data: Trade) => void
type AlertCallback = (data: Alert) => void

class WebSocketClient {
  private socket: Socket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 3 // Reduced to minimize console spam
  private reconnectDelay = 2000 // Start with 2 seconds
  private maxReconnectDelay = 30000 // Max 30 seconds
  private shouldBeConnected = false

  connect(): void {
    this.shouldBeConnected = true

    // Already connected or connecting
    if (this.socket?.connected) {
      return
    }

    // Reuse existing socket if available (handles StrictMode remount)
    if (this.socket) {
      if (!this.socket.connected) {
        this.socket.connect()
      }
      return
    }

    const wsUrl = import.meta.env.VITE_WS_URL || 'http://localhost:8000'

    this.socket = io(wsUrl, {
      path: '/ws/socket.io',
      transports: ['websocket', 'polling'],
      autoConnect: false, // Don't connect immediately - wait for explicit connect()
      reconnection: false, // We handle reconnection manually
    })

    this.socket.on('connect', () => {
      if (!this.shouldBeConnected) {
        // Component unmounted during connection - disconnect silently
        this.socket?.disconnect()
        return
      }
      this.reconnectAttempts = 0
      this.reconnectDelay = 1000
    })

    this.socket.on('disconnect', (reason) => {
      if (this.shouldBeConnected && reason === 'io server disconnect') {
        // Server disconnected us - try to reconnect
        this.scheduleReconnect()
      }
    })

    this.socket.on('connect_error', () => {
      // Only try to reconnect if we still want to be connected
      if (this.shouldBeConnected) {
        this.scheduleReconnect()
      }
    })

    // Now actually connect
    this.socket.connect()
  }

  private scheduleReconnect(): void {
    if (!this.shouldBeConnected) {
      return
    }

    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      // Silently stop - no need to spam console
      return
    }

    this.reconnectAttempts++
    const delay = Math.min(
      this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1),
      this.maxReconnectDelay
    )

    setTimeout(() => {
      if (this.shouldBeConnected && this.socket && !this.socket.connected) {
        this.socket.connect()
      }
    }, delay)
  }

  disconnect(): void {
    this.shouldBeConnected = false
    this.reconnectAttempts = 0
    // Don't destroy socket - just disconnect. Allows clean reconnect on remount.
    if (this.socket?.connected) {
      this.socket.disconnect()
    }
  }

  joinTeam(teamId: number): void {
    if (!this.socket?.connected) {
      return
    }
    this.socket.emit('join_team', { team_id: teamId })
  }

  leaveTeam(teamId: number): void {
    if (!this.socket?.connected) {
      return
    }
    this.socket.emit('leave_team', { team_id: teamId })
  }

  onTeamStatusChanged(callback: TeamStatusCallback): void {
    if (!this.socket) {
      return
    }
    this.socket.on('team:status_changed', callback)
  }

  onTradeExecuted(callback: TradeCallback): void {
    if (!this.socket) {
      return
    }
    this.socket.on('trade:executed', callback)
  }

  onAlert(callback: AlertCallback): void {
    if (!this.socket) {
      return
    }
    this.socket.on('alert:crash', callback)
    this.socket.on('alert:warning', callback)
    this.socket.on('alert:info', callback)
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
    this.socket.off('alert:crash', callback)
    this.socket.off('alert:warning', callback)
    this.socket.off('alert:info', callback)
  }

  isConnected(): boolean {
    return this.socket?.connected ?? false
  }
}

// Singleton instance
export const wsClient = new WebSocketClient()

export default WebSocketClient
