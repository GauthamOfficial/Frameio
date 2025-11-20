"use client"

import { Sidebar } from "./sidebar"
import { TopNav } from "./top-nav"
import { ProtectedRoute } from "@/components/auth/protected-route"
import { cn } from "@/lib/utils"

interface DashboardLayoutProps {
  children: React.ReactNode
  className?: string
}

export function DashboardLayout({ children, className }: DashboardLayoutProps) {
  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-background fabric-texture">
        <Sidebar />
        <div className="md:ml-64">
          <TopNav />
          <main className={cn("p-6", className)}>
            {children}
          </main>
        </div>
      </div>
    </ProtectedRoute>
  )
}
