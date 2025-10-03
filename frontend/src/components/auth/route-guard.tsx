"use client"

import { useOrganization } from "@/contexts/organization-context"
import { useRouter, usePathname } from "next/navigation"
import { useEffect } from "react"

interface RouteGuardProps {
  children: React.ReactNode
  allowedRoles: string[]
  redirectTo: string
}

export function RouteGuard({ children, allowedRoles, redirectTo }: RouteGuardProps) {
  const { userRole, isLoading } = useOrganization()
  const router = useRouter()
  const pathname = usePathname()

  useEffect(() => {
    if (!isLoading && userRole) {
      // Check if user has access to current route
      if (!allowedRoles.includes(userRole)) {
        console.log(`Access denied: ${userRole} cannot access ${pathname}`)
        router.push(redirectTo)
      }
    }
  }, [userRole, isLoading, allowedRoles, redirectTo, pathname, router])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="w-8 h-8 bg-primary rounded-lg mx-auto mb-4 animate-pulse"></div>
          <p className="text-muted-foreground">Checking access...</p>
        </div>
      </div>
    )
  }

  if (!userRole || !allowedRoles.includes(userRole)) {
    return null
  }

  return <>{children}</>
}
