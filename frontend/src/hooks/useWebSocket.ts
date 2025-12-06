import { useEffect, useCallback, useRef } from 'react'
import { wsClient } from '@/lib/socket'
import { useTeamStore } from '@/stores/teamStore'
import type { Alert, Trade, TeamStatusUpdate } from '@/types'

/**
 * Custom hook to manage WebSocket connection and event subscriptions
 *
 * Automatically connects to WebSocket server and subscribes to real-time events.
 * Updates are synchronized with the Zustand team store.
 *
 * @param autoConnect - Whether to auto-connect on mount (default: true)
 * @returns Object with connection status and manual control functions
 */
export function useWebSocket(autoConnect = true) {
  const { updateTeamStatus, addAlert } = useTeamStore()
  const isInitializedRef = useRef(false)

  // WebSocket event handlers
  const handleTeamStatusChanged = useCallback(
    (data: TeamStatusUpdate) => {
      console.log('Team status changed:', data)
      updateTeamStatus(data.team_id, data)
    },
    [updateTeamStatus]
  )

  const handleTradeExecuted = useCallback((data: Trade) => {
    console.log('Trade executed:', data)
    // Trade updates will be reflected in team status changes
    // Could add a separate trades store if needed
  }, [])

  const handleAlert = useCallback(
    (data: Alert) => {
      console.log('Alert received:', data)
      addAlert(data)
    },
    [addAlert]
  )

  // Connect and subscribe to events
  useEffect(() => {
    if (!autoConnect || isInitializedRef.current) {
      return
    }

    isInitializedRef.current = true

    // Connect to WebSocket server
    wsClient.connect()

    // Subscribe to events
    wsClient.onTeamStatusChanged(handleTeamStatusChanged)
    wsClient.onTradeExecuted(handleTradeExecuted)
    wsClient.onAlert(handleAlert)

    // Cleanup on unmount
    return () => {
      wsClient.offTeamStatusChanged(handleTeamStatusChanged)
      wsClient.offTradeExecuted(handleTradeExecuted)
      wsClient.offAlert(handleAlert)
      wsClient.disconnect()
      isInitializedRef.current = false
    }
  }, [autoConnect, handleTeamStatusChanged, handleTradeExecuted, handleAlert])

  // Manual control functions
  const connect = useCallback(() => {
    wsClient.connect()
  }, [])

  const disconnect = useCallback(() => {
    wsClient.disconnect()
  }, [])

  const joinTeam = useCallback((teamId: number) => {
    wsClient.joinTeam(teamId)
  }, [])

  const leaveTeam = useCallback((teamId: number) => {
    wsClient.leaveTeam(teamId)
  }, [])

  return {
    isConnected: wsClient.isConnected(),
    connect,
    disconnect,
    joinTeam,
    leaveTeam,
  }
}

export default useWebSocket
