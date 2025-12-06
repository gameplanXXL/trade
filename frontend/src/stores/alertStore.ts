import { create } from 'zustand'
import type { Alert } from '@/types'

interface AlertStore {
  // State
  alerts: Alert[]
  alertHistory: Alert[]

  // Actions
  addAlert: (alert: Alert) => void
  removeAlert: (alertId: string) => void
  clearAlerts: () => void
  getAlertHistory: () => Alert[]
}

const MAX_VISIBLE_ALERTS = 5
const MAX_HISTORY_SIZE = 100

export const useAlertStore = create<AlertStore>((set, get) => ({
  // Initial State
  alerts: [],
  alertHistory: [],

  // Add new alert to the list and history
  addAlert: (alert) =>
    set((state) => {
      // Add to history (keep last MAX_HISTORY_SIZE items)
      const newHistory = [alert, ...state.alertHistory].slice(0, MAX_HISTORY_SIZE)

      // Add to visible alerts (max MAX_VISIBLE_ALERTS will be shown by AlertList)
      const newAlerts = [alert, ...state.alerts]

      return {
        alerts: newAlerts,
        alertHistory: newHistory,
      }
    }),

  // Remove alert from visible list (but keep in history)
  removeAlert: (alertId) =>
    set((state) => ({
      alerts: state.alerts.filter((alert) => alert.id !== alertId),
    })),

  // Clear all visible alerts (history remains)
  clearAlerts: () => set({ alerts: [] }),

  // Get alert history
  getAlertHistory: () => get().alertHistory,
}))

export default useAlertStore
