import { BrowserRouter, Routes, Route, useParams, Navigate } from 'react-router-dom'
import { DashboardView } from '@/features/dashboard'
import { TeamDetail } from '@/features/teams'
import { TeamCreate } from '@/features/teams/TeamCreate'
import { LoginForm } from '@/features/auth'
import { ProtectedRoute } from '@/components/ProtectedRoute'
import { Toaster } from '@/components/ui/toaster'

function TeamDetailWrapper() {
  const { teamId } = useParams<{ teamId: string }>()
  return <TeamDetail teamId={Number(teamId)} />
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public Routes */}
        <Route path="/login" element={<LoginForm />} />

        {/* Protected Routes */}
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Navigate to="/dashboard" replace />
            </ProtectedRoute>
          }
        />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <DashboardView />
            </ProtectedRoute>
          }
        />
        <Route
          path="/teams/create"
          element={
            <ProtectedRoute>
              <TeamCreate />
            </ProtectedRoute>
          }
        />
        <Route
          path="/teams/:teamId"
          element={
            <ProtectedRoute>
              <TeamDetailWrapper />
            </ProtectedRoute>
          }
        />
      </Routes>
      <Toaster />
    </BrowserRouter>
  )
}

export default App
