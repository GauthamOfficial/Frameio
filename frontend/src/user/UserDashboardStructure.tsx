"use client"

import { ReactNode } from "react"

interface UserDashboardStructureProps {
  children: ReactNode
}

export function UserDashboardStructure({ children }: UserDashboardStructureProps) {
  return (
    <div className="min-h-screen bg-background">
      <div className="flex">
        {children}
      </div>
    </div>
  )
}
