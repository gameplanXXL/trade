import { useEffect } from 'react'
import { Navigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import { useCurrentUser, useAuthListener } from '@/hooks/useAuth'
import { Loader2 } from 'lucide-react'

interface ProtectedRouteProps {
  children: React.ReactNode
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  const clearAuth = useAuthStore((state) => state.clearAuth)
  const { isLoading, isError } = useCurrentUser()

  // Set up global auth listener for 401 events
  useAuthListener()

  // Clear auth state when user check fails (e.g., 401 response)
  useEffect(() => {
    if (isError) {
      clearAuth()
    }
  }, [isError, clearAuth])

  // If already authenticated via store (e.g., after login), skip loading
  if (isAuthenticated) {
    return <>{children}</>
  }

  // Show loading spinner while checking auth status (but not if there was an error)
  if (isLoading && !isError) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <Loader2 className="h-8 w-8 animate-spin text-accent" />
      </div>
    )
  }

  // Redirect to login if not authenticated
  return <Navigate to="/login" replace />
}
