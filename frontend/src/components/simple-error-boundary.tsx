"use client"

import { useEffect } from 'react'

interface SimpleErrorBoundaryProps {
  children: React.ReactNode
}

export function SimpleErrorBoundary({ children }: SimpleErrorBoundaryProps) {
  useEffect(() => {
    const handleError = (error: ErrorEvent) => {
      console.error('Application error:', {
        message: error.message,
        filename: error.filename,
        lineno: error.lineno,
        colno: error.colno,
        error: error.error
      })
    }

    const handleUnhandledRejection = (event: PromiseRejectionEvent) => {
      console.error('Unhandled promise rejection:', {
        reason: event.reason,
        promise: event.promise
      })
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

