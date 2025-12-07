import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import './index.css'
import App from './App.tsx'

// Suppress noisy development messages
if (import.meta.env.DEV) {
  const shouldSuppress = (args: unknown[]): boolean => {
    const msg = typeof args[0] === 'string' ? args[0] : ''
    return (
      msg.includes('Download the React DevTools') ||
      msg.includes('Query data cannot be undefined')
    )
  }

  const originalLog = console.log
  const originalWarn = console.warn
  const originalInfo = console.info
  const originalDebug = console.debug

  console.log = (...args: unknown[]) => {
    if (!shouldSuppress(args)) originalLog.apply(console, args)
  }
  console.warn = (...args: unknown[]) => {
    if (!shouldSuppress(args)) originalWarn.apply(console, args)
  }
  console.info = (...args: unknown[]) => {
    if (!shouldSuppress(args)) originalInfo.apply(console, args)
  }
  console.debug = (...args: unknown[]) => {
    if (!shouldSuppress(args)) originalDebug.apply(console, args)
  }
}

// Create a query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
})

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </StrictMode>,
)
