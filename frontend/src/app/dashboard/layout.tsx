"use client"

import { OrganizationProvider } from "@/contexts/organization-context"
import { ProtectedRoute } from "@/components/auth/protected-route"
import { DashboardStructure } from "@/components/dashboard/dashboard-structure"

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <ProtectedRoute>
      <OrganizationProvider>
        <DashboardStructure>
          {children}
        </DashboardStructure>
      </OrganizationProvider>
    </ProtectedRoute>
  )
}
