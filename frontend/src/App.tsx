import { BrowserRouter, Routes, Route, useParams } from 'react-router-dom'
import { DashboardView } from '@/features/dashboard'
import { TeamDetail } from '@/features/teams'

function TeamDetailWrapper() {
  const { teamId } = useParams<{ teamId: string }>()
  return <TeamDetail teamId={Number(teamId)} />
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<DashboardView />} />
        <Route path="/teams/:teamId" element={<TeamDetailWrapper />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
