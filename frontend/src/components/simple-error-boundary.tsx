"use client"

import { useEffect } from 'react'

interface SimpleErrorBoundaryProps {
  children: React.ReactNode
}

export function SimpleErrorBoundary({ children }: SimpleErrorBoundaryProps) {
  useEffect(() => {
    const handleError = (error: ErrorEvent) => {
      console.error('Application error:', error)
    }

    const handleUnhandledRejection = (event: PromiseRejectionEvent) => {
      console.error('Unhandled promise rejection:', event.reason)
    }

    window.addEventListener('error', handleError)
    window.addEventListener('unhandledrejection', handleUnhandledRejection)

    return () => {
      window.removeEventListener('error', handleError)
      window.removeEventListener('unhandledrejection', handleUnhandledRejection)
    }
  }, [])

  return <>{children}</>
}

