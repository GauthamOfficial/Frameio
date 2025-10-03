"use client"

import { Sidebar } from "./sidebar"
import { TopNav } from "./top-nav"
import { cn } from "@/lib/utils"

interface DashboardStructureProps {
  children: React.ReactNode
  className?: string
}

export function DashboardStructure({ children, className }: DashboardStructureProps) {
  return (
    <div className="min-h-screen bg-background fabric-texture">
      <Sidebar />
      <div className="md:ml-64">
        <TopNav />
        <main className={cn("p-6", className)}>
          {children}
        </main>
      </div>
    </div>
  )
}
