import { useMutation, useQueryClient } from '@tanstack/react-query'
import type { Team } from '@/types'

interface ApiResponse {
  data: Team
  meta: {
    timestamp: string
  }
}

interface ErrorResponse {
  error: {
    code: string
    message: string
  }
}

/**
 * Pause a team
 */
async function pauseTeam(teamId: number): Promise<Team> {
  const response = await fetch(`http://localhost:8000/api/teams/${teamId}/pause`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
    },
  })

  if (!response.ok) {
    const error: ErrorResponse = await response.json()
    throw new Error(error.error.message || 'Failed to pause team')
  }

  const data: ApiResponse = await response.json()
  return data.data
}

export function usePauseTeam() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: pauseTeam,
    onMutate: async (teamId) => {
      // Cancel any outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['teams'] })
      await queryClient.cancelQueries({ queryKey: ['team', teamId] })

      // Snapshot the previous value
      const previousTeams = queryClient.getQueryData(['teams'])
      const previousTeam = queryClient.getQueryData(['team', teamId])

      // Optimistically update to the new value
      queryClient.setQueryData(['teams'], (old: any) => {
        if (!old?.data) return old
        return {
          ...old,
          data: old.data.map((team: Team) =>
            team.id === teamId ? { ...team, status: 'paused' as const } : team
          ),
        }
      })

      queryClient.setQueryData(['team', teamId], (old: any) => {
        if (!old?.data) return old
        return {
          ...old,
          data: { ...old.data, status: 'paused' as const },
        }
      })

      return { previousTeams, previousTeam }
    },
    onError: (err, teamId, context) => {
      // Rollback on error
      if (context?.previousTeams) {
        queryClient.setQueryData(['teams'], context.previousTeams)
      }
      if (context?.previousTeam) {
        queryClient.setQueryData(['team', teamId], context.previousTeam)
      }
    },
    onSettled: (data, error, teamId) => {
      queryClient.invalidateQueries({ queryKey: ['teams'] })
      queryClient.invalidateQueries({ queryKey: ['team', teamId] })
    },
  })
}

/**
 * Resume a team
 */
async function resumeTeam(teamId: number): Promise<Team> {
  const response = await fetch(`http://localhost:8000/api/teams/${teamId}/start`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
    },
  })

  if (!response.ok) {
    const error: ErrorResponse = await response.json()
    throw new Error(error.error.message || 'Failed to resume team')
  }

  const data: ApiResponse = await response.json()
  return data.data
}

export function useResumeTeam() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: resumeTeam,
    onMutate: async (teamId) => {
      await queryClient.cancelQueries({ queryKey: ['teams'] })
      await queryClient.cancelQueries({ queryKey: ['team', teamId] })

      const previousTeams = queryClient.getQueryData(['teams'])
      const previousTeam = queryClient.getQueryData(['team', teamId])

      queryClient.setQueryData(['teams'], (old: any) => {
        if (!old?.data) return old
        return {
          ...old,
          data: old.data.map((team: Team) =>
            team.id === teamId ? { ...team, status: 'active' as const } : team
          ),
        }
      })

      queryClient.setQueryData(['team', teamId], (old: any) => {
        if (!old?.data) return old
        return {
          ...old,
          data: { ...old.data, status: 'active' as const },
        }
      })

      return { previousTeams, previousTeam }
    },
    onError: (err, teamId, context) => {
      if (context?.previousTeams) {
        queryClient.setQueryData(['teams'], context.previousTeams)
      }
      if (context?.previousTeam) {
        queryClient.setQueryData(['team', teamId], context.previousTeam)
      }
    },
    onSettled: (data, error, teamId) => {
      queryClient.invalidateQueries({ queryKey: ['teams'] })
      queryClient.invalidateQueries({ queryKey: ['team', teamId] })
    },
  })
}

/**
 * Stop a team
 */
async function stopTeam(teamId: number): Promise<Team> {
  const response = await fetch(`http://localhost:8000/api/teams/${teamId}/stop`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
    },
  })

  if (!response.ok) {
    const error: ErrorResponse = await response.json()
    throw new Error(error.error.message || 'Failed to stop team')
  }

  const data: ApiResponse = await response.json()
  return data.data
}

export function useStopTeam() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: stopTeam,
    onMutate: async (teamId) => {
      await queryClient.cancelQueries({ queryKey: ['teams'] })
      await queryClient.cancelQueries({ queryKey: ['team', teamId] })

      const previousTeams = queryClient.getQueryData(['teams'])
      const previousTeam = queryClient.getQueryData(['team', teamId])

      queryClient.setQueryData(['teams'], (old: any) => {
        if (!old?.data) return old
        return {
          ...old,
          data: old.data.map((team: Team) =>
            team.id === teamId ? { ...team, status: 'stopped' as const } : team
          ),
        }
      })

      queryClient.setQueryData(['team', teamId], (old: any) => {
        if (!old?.data) return old
        return {
          ...old,
          data: { ...old.data, status: 'stopped' as const },
        }
      })

      return { previousTeams, previousTeam }
    },
    onError: (err, teamId, context) => {
      if (context?.previousTeams) {
        queryClient.setQueryData(['teams'], context.previousTeams)
      }
      if (context?.previousTeam) {
        queryClient.setQueryData(['team', teamId], context.previousTeam)
      }
    },
    onSettled: (data, error, teamId) => {
      queryClient.invalidateQueries({ queryKey: ['teams'] })
      queryClient.invalidateQueries({ queryKey: ['team', teamId] })
    },
  })
}

/**
 * Close all positions for a team
 */
async function closePositions(teamId: number): Promise<{ closed_count: number }> {
  const response = await fetch(`http://localhost:8000/api/teams/${teamId}/positions/close`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
  })

  if (!response.ok) {
    const error: ErrorResponse = await response.json()
    throw new Error(error.error.message || 'Failed to close positions')
  }

  const data = await response.json()
  return data.data
}

export function useClosePositions() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: closePositions,
    onSuccess: (data, teamId) => {
      // Invalidate team data to refetch updated positions
      queryClient.invalidateQueries({ queryKey: ['teams'] })
      queryClient.invalidateQueries({ queryKey: ['team', teamId] })
      queryClient.invalidateQueries({ queryKey: ['trades', teamId] })
    },
  })
}
