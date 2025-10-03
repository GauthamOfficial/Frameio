"use client"

import { OrganizationProvider } from "@/contexts/organization-context"
import { ProtectedRoute } from "@/components/auth/protected-route"
import { RouteGuard } from "@/components/auth/route-guard"
import { UserLayoutStructure } from "@/components/dashboard/user-layout-structure"

interface DashboardLayoutProps {
  children: React.ReactNode
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  return (
    <ProtectedRoute>
      <OrganizationProvider>
        <RouteGuard allowedRoles={['Designer', 'Manager']} redirectTo="/admin">
          <UserLayoutStructure>
            {children}
          </UserLayoutStructure>
        </RouteGuard>
      </OrganizationProvider>
    </ProtectedRoute>
  )
}
