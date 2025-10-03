"use client"

import { OrganizationProvider } from "@/contexts/organization-context"
import { ProtectedRoute } from "@/components/auth/protected-route"
import { RouteGuard } from "@/components/auth/route-guard"
import { AdminLayoutStructure } from "@/components/admin/admin-layout-structure"

interface AdminLayoutProps {
  children: React.ReactNode
}

export function AdminLayout({ children }: AdminLayoutProps) {
  return (
    <ProtectedRoute>
      <OrganizationProvider>
        <RouteGuard allowedRoles={['Admin']} redirectTo="/dashboard">
          <AdminLayoutStructure>
            {children}
          </AdminLayoutStructure>
        </RouteGuard>
      </OrganizationProvider>
    </ProtectedRoute>
  )
}
