"use client"

import { useOrganization } from "@/contexts/organization-context"
import { Button } from "@/components/ui/button"
import { Shield, User } from "lucide-react"
import Link from "next/link"

export function PanelNavigation() {
  const { userRole, isLoading } = useOrganization()

  if (isLoading) {
    return (
      <div className="flex items-center space-x-2">
        <div className="w-8 h-8 bg-muted rounded-lg animate-pulse"></div>
        <div className="w-20 h-4 bg-muted rounded animate-pulse"></div>
      </div>
    )
  }

  if (!userRole) {
    return null
  }

  return (
    <div className="flex items-center space-x-2">
      {userRole === 'Admin' ? (
        <Button asChild variant="outline" size="sm">
          <Link href="/admin" className="flex items-center space-x-2">
            <Shield className="h-4 w-4" />
            <span>Admin Panel</span>
          </Link>
        </Button>
      ) : (
        <Button asChild variant="outline" size="sm">
          <Link href="/user" className="flex items-center space-x-2">
            <User className="h-4 w-4" />
            <span>User Panel</span>
          </Link>
        </Button>
      )}
    </div>
  )
}
