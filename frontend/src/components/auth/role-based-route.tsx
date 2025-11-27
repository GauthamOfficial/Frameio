"use client"

import { useOrganization } from "@/contexts/organization-context"
import { useRouter } from "next/navigation"
import { useEffect } from "react"

interface RoleBasedRouteProps {
  children: React.ReactNode
  allowedRoles: string[]
  redirectTo?: string
}

export function RoleBasedRoute({ 
  children, 
  allowedRoles
}: RoleBasedRouteProps) {
  const { userRole, isLoading } = useOrganization()
  const router = useRouter()

  useEffect(() => {
    if (!isLoading && userRole) {
      if (!allowedRoles.includes(userRole)) {
        // Redirect to dashboard for all users
        router.push('/dashboard')
      }
    }
  }, [userRole, isLoading, allowedRoles, router])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="w-8 h-8 bg-primary rounded-lg mx-auto mb-4 animate-pulse"></div>
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    )
  }

  if (!userRole || !allowedRoles.includes(userRole)) {
    return null
  }

  return <>{children}</>
}
