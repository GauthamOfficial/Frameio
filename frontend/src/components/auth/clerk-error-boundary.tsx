"use client"

import { useEffect } from 'react'

interface ClerkErrorBoundaryProps {
  children: React.ReactNode
}

export function ClerkErrorBoundary({ children }: ClerkErrorBoundaryProps) {

  useEffect(() => {
    // Handle chunk loading errors specifically for Clerk
    const handleChunkError = (event: ErrorEvent) => {
      if (
        event.error?.name === 'ChunkLoadError' ||
        event.message?.includes('Loading chunk') ||
        event.filename?.includes('clerk')
      ) {
        console.warn('Clerk chunk loading error detected, attempting recovery...')
        
        // Clear any cached chunks and reload
        if ('caches' in window) {
          caches.keys().then(names => {
            names.forEach(name => {
              if (name.includes('clerk') || name.includes('chunk')) {
                caches.delete(name)
              }
            })
          })
        }
        
        // Reload the page after clearing cache
        setTimeout(() => {
          window.location.reload()
        }, 1000)
      }
    }

    // Handle unhandled promise rejections
    const handleUnhandledRejection = (event: PromiseRejectionEvent) => {
      const error = event.reason
      
      if (
        error?.message?.includes('Loading chunk') ||
        error?.message?.includes('ChunkLoadError') ||
        error?.stack?.includes('clerk')
      ) {
        console.warn('Clerk chunk loading promise rejection detected')
        
        // Clear cache and reload
        if ('caches' in window) {
          caches.keys().then(names => {
            names.forEach(name => {
              if (name.includes('clerk') || name.includes('chunk')) {
                caches.delete(name)
              }
            })
          })
        }
        
        setTimeout(() => {
          window.location.reload()
        }, 1000)
        
        event.preventDefault()
      }
    }

    window.addEventListener('error', handleChunkError)
    window.addEventListener('unhandledrejection', handleUnhandledRejection)

    return () => {
      window.removeEventListener('error', handleChunkError)
      window.removeEventListener('unhandledrejection', handleUnhandledRejection)
    }
  }, [])

  return <>{children}</>
}
