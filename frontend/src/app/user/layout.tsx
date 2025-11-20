"use client"

import { UserDashboard } from "@/user/UserDashboard"

export default function UserLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <UserDashboard>
      {children}
    </UserDashboard>
  )
}
