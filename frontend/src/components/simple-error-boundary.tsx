"use client"

import { useEffect } from 'react'

interface SimpleErrorBoundaryProps {
  children: React.ReactNode
}

export function SimpleErrorBoundary({ children }: SimpleErrorBoundaryProps) {
  useEffect(() => {
    const handleError = (event: ErrorEvent) => {
      // Extract useful information from ErrorEvent
      const errorInfo = {
        message: event.message || 'Unknown error',
        filename: event.filename || 'Unknown file',
        lineno: event.lineno || 0,
        colno: event.colno || 0,
        error: event.error ? {
          name: event.error.name,
          message: event.error.message,
          stack: event.error.stack
        } : null
      }
      
      // Only log if it's not a known handled error (like chunk loading errors)
      const isChunkError = event.error?.name === 'ChunkLoadError' || 
                          event.message?.includes('Loading chunk') ||
                          event.message?.includes('ChunkLoadError')
      
      if (!isChunkError) {
        console.error('Application error:', errorInfo)
      }
    }

    const handleUnhandledRejection = (event: PromiseRejectionEvent) => {
      // Extract useful information from PromiseRejectionEvent
      const rejectionInfo = {
        reason: event.reason,
        message: event.reason?.message || String(event.reason),
        stack: event.reason?.stack,
        name: event.reason?.name
      }
      
      // Only log if it's not a known handled error
      const isChunkError = event.reason?.name === 'ChunkLoadError' ||
                          event.reason?.message?.includes('Loading chunk') ||
                          event.reason?.message?.includes('ChunkLoadError')
      
      if (!isChunkError) {
        console.error('Unhandled promise rejection:', rejectionInfo)
      }
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

