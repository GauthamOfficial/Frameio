"use client"

import { useRouter } from "next/navigation"
import { useEffect } from "react"

export function PanelRedirect() {
  const router = useRouter()

  useEffect(() => {
    // Default redirect to dashboard - the individual layouts will handle role-based routing
    router.push('/dashboard')
  }, [router])

  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-center">
        <div className="w-8 h-8 bg-primary rounded-lg mx-auto mb-4 animate-pulse"></div>
        <p className="text-muted-foreground">Redirecting to your panel...</p>
      </div>
    </div>
  )
}