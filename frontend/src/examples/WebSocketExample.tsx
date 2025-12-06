import { useEffect, useState } from 'react'
import { useWebSocket } from '@/hooks/useWebSocket'
import { useTeamStore } from '@/stores/teamStore'

/**
 * Example component demonstrating WebSocket usage
 *
 * This is a reference implementation showing how to:
 * - Use the WebSocket hook
 * - Subscribe to team updates
 * - Display real-time alerts
 * - Join/leave team rooms
 */
export function WebSocketExample() {
  const { isConnected, joinTeam, leaveTeam } = useWebSocket()
  const { teams, alerts, removeAlert } = useTeamStore()
  const [selectedTeamId, setSelectedTeamId] = useState<number | null>(null)

  // Join/leave team room when selection changes
  useEffect(() => {
    if (selectedTeamId !== null) {
      joinTeam(selectedTeamId)
      return () => {
        leaveTeam(selectedTeamId)
      }
    }
  }, [selectedTeamId, joinTeam, leaveTeam])

  return (
    <div className="p-6 space-y-6">
      {/* Connection Status */}
      <div className="border rounded-lg p-4">
        <h2 className="text-lg font-semibold mb-2">WebSocket Status</h2>
        <div className="flex items-center gap-2">
          <div
            className={`w-3 h-3 rounded-full ${
              isConnected ? 'bg-green-500' : 'bg-red-500'
            }`}
          />
          <span>{isConnected ? 'Connected' : 'Disconnected'}</span>
        </div>
      </div>

      {/* Team Selection */}
      <div className="border rounded-lg p-4">
        <h2 className="text-lg font-semibold mb-2">Select Team</h2>
        <select
          className="w-full border rounded p-2"
          value={selectedTeamId ?? ''}
          onChange={(e) =>
            setSelectedTeamId(e.target.value ? Number(e.target.value) : null)
          }
        >
          <option value="">-- Select a team --</option>
          {teams.map((team) => (
            <option key={team.id} value={team.id}>
              {team.name} - {team.status}
            </option>
          ))}
        </select>
      </div>

      {/* Selected Team Info */}
      {selectedTeamId && (
        <div className="border rounded-lg p-4">
          <h2 className="text-lg font-semibold mb-2">Team Details</h2>
          {teams
            .filter((t) => t.id === selectedTeamId)
            .map((team) => (
              <div key={team.id} className="space-y-2">
                <p>
                  <strong>Name:</strong> {team.name}
                </p>
                <p>
                  <strong>Status:</strong> {team.status}
                </p>
                <p>
                  <strong>Symbol:</strong> {team.symbol}
                </p>
                <p>
                  <strong>P&L:</strong> ${team.current_pnl.toFixed(2)} (
                  {team.pnl_percent.toFixed(2)}%)
                </p>
                <p className="text-sm text-gray-500">
                  This data updates in real-time via WebSocket
                </p>
              </div>
            ))}
        </div>
      )}

      {/* Real-time Alerts */}
      <div className="border rounded-lg p-4">
        <h2 className="text-lg font-semibold mb-2">
          Real-time Alerts ({alerts.length})
        </h2>
        {alerts.length === 0 ? (
          <p className="text-gray-500">No alerts</p>
        ) : (
          <div className="space-y-2">
            {alerts.map((alert) => (
              <div
                key={alert.id}
                className={`border-l-4 p-3 rounded ${
                  alert.severity === 'crash'
                    ? 'border-red-500 bg-red-50'
                    : alert.severity === 'warning'
                    ? 'border-yellow-500 bg-yellow-50'
                    : 'border-blue-500 bg-blue-50'
                }`}
              >
                <div className="flex justify-between items-start">
                  <div>
                    <p className="font-semibold">{alert.severity.toUpperCase()}</p>
                    <p>{alert.message}</p>
                    <p className="text-sm text-gray-500">
                      {new Date(alert.timestamp).toLocaleString()}
                    </p>
                  </div>
                  <button
                    onClick={() => removeAlert(alert.id)}
                    className="text-gray-500 hover:text-gray-700"
                  >
                    ✕
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Live Teams Grid */}
      <div className="border rounded-lg p-4">
        <h2 className="text-lg font-semibold mb-2">All Teams (Live)</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {teams.map((team) => (
            <div
              key={team.id}
              className="border rounded p-3 hover:shadow-lg transition-shadow cursor-pointer"
              onClick={() => setSelectedTeamId(team.id)}
            >
              <div className="flex justify-between items-start mb-2">
                <h3 className="font-semibold">{team.name}</h3>
                <span
                  className={`text-xs px-2 py-1 rounded ${
                    team.status === 'active'
                      ? 'bg-green-100 text-green-800'
                      : team.status === 'paused'
                      ? 'bg-yellow-100 text-yellow-800'
                      : team.status === 'critical'
                      ? 'bg-red-100 text-red-800'
                      : 'bg-gray-100 text-gray-800'
                  }`}
                >
                  {team.status}
                </span>
              </div>
              <p className="text-sm text-gray-600">{team.symbol}</p>
              <p
                className={`text-lg font-semibold ${
                  team.current_pnl >= 0 ? 'text-green-600' : 'text-red-600'
                }`}
              >
                ${team.current_pnl.toFixed(2)}
              </p>
              <p className="text-sm text-gray-500">
                {team.pnl_percent.toFixed(2)}%
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default WebSocketExample
