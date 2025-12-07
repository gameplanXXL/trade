import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { apiClient } from '@/lib/api'
import { useAuthStore } from '@/stores/authStore'
import type { LoginInput, LoginResponse, User } from '@/types'

// Login mutation
export function useLogin() {
  const setUser = useAuthStore((state) => state.setUser)
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (credentials: LoginInput) => {
      const response = await apiClient.post<LoginResponse, LoginInput>(
        '/api/auth/login',
        credentials
      )
      return response.data
    },
    onSuccess: (data) => {
      setUser(data.user)
      // Clear any cached error state from previous auth check
      queryClient.removeQueries({ queryKey: ['currentUser'] })
      navigate('/dashboard')
    },
  })
}

// Logout mutation
export function useLogout() {
  const clearAuth = useAuthStore((state) => state.clearAuth)
  const navigate = useNavigate()

  return useMutation({
    mutationFn: async () => {
      await apiClient.post('/api/auth/logout')
    },
    onSuccess: () => {
      clearAuth()
      navigate('/login')
    },
  })
}

// Response type for /api/auth/me endpoint
interface MeResponse {
  data: User
}

// Fetch current user (for initial auth check)
export function useCurrentUser(options?: { enabled?: boolean }) {
  const setUser = useAuthStore((state) => state.setUser)

  return useQuery({
    queryKey: ['currentUser'],
    queryFn: async (): Promise<User> => {
      const response = await apiClient.get<User>('/api/auth/me')
      // Backend returns {data: User}, apiClient wraps as {data: {data: User}}
      // But if backend already has 'data' key, apiClient returns as-is: {data: {data: User}}
      // So response.data could be User directly or {data: User}
      const user = 'data' in response.data
        ? (response.data as unknown as { data: User }).data
        : response.data
      if (!user || typeof user !== 'object' || !('id' in user)) {
        throw new Error('Invalid user data in response')
      }
      setUser(user)
      return user
    },
    enabled: options?.enabled ?? true,
    retry: false,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes (formerly cacheTime)
  })
}

// Hook to handle unauthorized events globally
export function useAuthListener() {
  const clearAuth = useAuthStore((state) => state.clearAuth)
  const navigate = useNavigate()

  useEffect(() => {
    const handleUnauthorized = () => {
      clearAuth()
      navigate('/login')
    }

    window.addEventListener('auth:unauthorized', handleUnauthorized)

    return () => {
      window.removeEventListener('auth:unauthorized', handleUnauthorized)
    }
  }, [clearAuth, navigate])
}

// Main useAuth hook for components
export function useAuth() {
  const { user, isAuthenticated } = useAuthStore()
  const loginMutation = useLogin()
  const logoutMutation = useLogout()

  return {
    user,
    isAuthenticated,
    login: loginMutation.mutateAsync,
    logout: logoutMutation.mutate,
    isLoggingIn: loginMutation.isPending,
    isLoggingOut: logoutMutation.isPending,
  }
}
