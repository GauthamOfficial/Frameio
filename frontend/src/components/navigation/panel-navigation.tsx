"use client"

import { useOrganization } from "@/contexts/organization-context"
import { Button } from "@/components/ui/button"
import { User } from "lucide-react"
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
      <Button asChild variant="outline" size="sm">
        <Link href="/dashboard" className="flex items-center space-x-2">
          <User className="h-4 w-4" />
          <span>Designer Panel</span>
        </Link>
      </Button>
    </div>
  )
}
