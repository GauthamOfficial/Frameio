"use client"

import { UserDashboardStructure } from "./UserDashboardStructure"
import { SimpleUserSidebar } from "./SimpleUserSidebar"

interface UserDashboardProps {
  children: React.ReactNode
}

export function UserDashboard({ children }: UserDashboardProps) {
  return (
    <UserDashboardStructure>
      <SimpleUserSidebar />
      <main className="flex-1 ml-64">
        <div className="p-6">
          {children}
        </div>
      </main>
    </UserDashboardStructure>
  )
}
