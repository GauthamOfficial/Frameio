"use client"

import { ErrorBoundary } from "./error-boundary"

interface ErrorBoundaryWrapperProps {
  children: React.ReactNode
}

export function ErrorBoundaryWrapper({ children }: ErrorBoundaryWrapperProps) {
  return (
    <ErrorBoundary>
      {children}
    </ErrorBoundary>
  )
}

