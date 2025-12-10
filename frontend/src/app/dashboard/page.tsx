"use client"

import { OverviewCards } from "@/components/dashboard/overview-cards"
import { SavedPosters } from "@/components/dashboard/saved-posters"
import { BrandingKitHistory } from "@/components/dashboard/branding-kit-history"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { useOrganization } from "@/contexts/organization-context"
import { useApp } from "@/contexts/app-context"
import { DashboardErrorBoundary } from "@/components/common/error-boundary"
import { Plus, TrendingUp, Calendar, Image, User, Settings, Palette } from "lucide-react"
import { useRouter } from "next/navigation"

export default function DashboardPage() {
  const { userRole, isLoading } = useOrganization()
  const { userRole: appUserRole, permissions } = useApp()
  // const { showSuccess } = useToastHelpers() // Removed unused variable
  const router = useRouter()

  const getRoleBadgeVariant = (role: string | null) => {
    switch (role) {
      case 'Designer':
        return 'secondary'
      default:
        return 'outline'
    }
  }

  const getQuickActions = () => {
    const actions = [
      { name: "Generate AI Poster", href: "/dashboard/poster-generator", icon: Image },
      { name: "Brandkit", href: "/dashboard/branding-kit", icon: Palette },
      { name: "Schedule Post", href: "/dashboard/scheduler", icon: Calendar },
      { name: "View Analytics", href: "/dashboard/analytics", icon: TrendingUp },
    ]

    // Add admin action if user has admin permissions
    if (appUserRole === 'Admin' || permissions.includes('admin_access')) {
      actions.push({ name: "Admin Panel", href: "/admin", icon: Settings })
    }

    return actions
  }

  const handleQuickAction = (href: string) => {
    router.push(href)
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="w-8 h-8 bg-primary rounded-lg mx-auto mb-4 animate-pulse"></div>
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    )
  }

  return (
    <DashboardErrorBoundary>
      <div className="space-y-4 sm:space-y-6 md:space-y-8">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div className="flex-1 min-w-0">
            <div className="flex flex-wrap items-center gap-2 sm:gap-3 mb-2">
              <h1 className="text-2xl sm:text-3xl font-bold text-foreground">Dashboard</h1>
              {userRole && (
                <Badge variant={getRoleBadgeVariant(userRole)} className="text-xs shrink-0">
                  <User className="mr-1 h-3 w-3" />
                  {userRole}
                </Badge>
              )}
            </div>
            <p className="text-sm sm:text-base text-muted-foreground">
              Welcome back! Here&apos;s what&apos;s happening with your textile marketing.
            </p>
          </div>
          <Button 
            className="bg-textile-accent w-full sm:w-auto shrink-0 text-sm sm:text-base"
            onClick={() => router.push('/dashboard/poster-generator')}
          >
            <Plus className="mr-2 h-4 w-4 shrink-0" />
            <span className="hidden min-[475px]:inline">Create New Post</span>
            <span className="min-[475px]:hidden">New Post</span>
          </Button>
        </div>

        {/* Overview Cards */}
        <OverviewCards />

        {/* Quick Actions */}
        <Card className="textile-hover textile-shadow">
          <CardHeader>
            <CardTitle className="text-lg sm:text-xl">Quick Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 min-[475px]:grid-cols-2 sm:flex sm:flex-wrap gap-2 sm:gap-3">
              {getQuickActions().map((action, index) => {
                const Icon = action.icon
                return (
                  <Button 
                    key={index}
                    className="w-full sm:flex-1 sm:min-w-[150px] justify-start text-sm sm:text-base" 
                    variant="outline"
                    onClick={() => handleQuickAction(action.href)}
                  >
                    <Icon className="mr-2 h-4 w-4 shrink-0" />
                    <span className="truncate">{action.name}</span>
                  </Button>
                )
              })}
            </div>
          </CardContent>
        </Card>

        {/* Saved Posters - All Generated Posters */}
        <SavedPosters limit={undefined} />

        {/* Branding Kit History */}
        <BrandingKitHistory limit={undefined} />
      </div>
    </DashboardErrorBoundary>
  )
}
