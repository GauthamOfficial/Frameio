"use client"

import { OverviewCards } from "@/components/dashboard/overview-cards"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { useOrganization } from "@/contexts/organization-context"
import { Plus, TrendingUp, Calendar, Image, User } from "lucide-react"

export default function DashboardPage() {
  const { userRole, isLoading } = useOrganization()

  const getRoleBadgeVariant = (role: string | null) => {
    switch (role) {
      case 'Designer':
        return 'secondary'
      default:
        return 'outline'
    }
  }

  const getQuickActions = () => {
    return [
      { name: "Generate AI Poster", href: "/dashboard/poster-generator", icon: Image },
      { name: "Schedule Post", href: "/dashboard/scheduler", icon: Calendar },
      { name: "View Analytics", href: "/dashboard/analytics", icon: TrendingUp },
    ]
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
    <div className="space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center space-x-3 mb-2">
              <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
              {userRole && (
                <Badge variant={getRoleBadgeVariant(userRole)} className="text-xs">
                  <User className="mr-1 h-3 w-3" />
                  {userRole}
                </Badge>
              )}
            </div>
            <p className="text-muted-foreground">
              Welcome back! Here&apos;s what&apos;s happening with your textile marketing.
            </p>
          </div>
          <Button className="bg-textile-accent">
            <Plus className="mr-2 h-4 w-4" />
            Create New Post
          </Button>
        </div>

        {/* Overview Cards */}
        <OverviewCards />

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Recent Activity */}
          <Card className="lg:col-span-2 textile-hover textile-shadow">
            <CardHeader>
              <CardTitle className="flex items-center">
                <TrendingUp className="mr-2 h-5 w-5 text-chart-1" />
                Recent Activity
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center space-x-4 p-3 rounded-lg bg-muted/50">
                  <div className="w-10 h-10 bg-chart-1 rounded-lg flex items-center justify-center">
                    <Image className="h-5 w-5 text-white" />
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium">New poster generated for Diwali Collection</p>
                    <p className="text-xs text-muted-foreground">2 hours ago</p>
                  </div>
                </div>
                <div className="flex items-center space-x-4 p-3 rounded-lg bg-muted/50">
                  <div className="w-10 h-10 bg-chart-2 rounded-lg flex items-center justify-center">
                    <Calendar className="h-5 w-5 text-white" />
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium">3 posts scheduled for this week</p>
                    <p className="text-xs text-muted-foreground">4 hours ago</p>
                  </div>
                </div>
                <div className="flex items-center space-x-4 p-3 rounded-lg bg-muted/50">
                  <div className="w-10 h-10 bg-chart-3 rounded-lg flex items-center justify-center">
                    <TrendingUp className="h-5 w-5 text-white" />
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium">Engagement rate increased by 15%</p>
                    <p className="text-xs text-muted-foreground">1 day ago</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card className="textile-hover textile-shadow">
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {getQuickActions().map((action, index) => {
                const Icon = action.icon
                return (
                  <Button 
                    key={index}
                    className="w-full justify-start" 
                    variant="outline"
                    onClick={() => window.location.href = action.href}
                  >
                    <Icon className="mr-2 h-4 w-4" />
                    {action.name}
                  </Button>
                )
              })}
            </CardContent>
          </Card>
        </div>

        {/* Recent Posts */}
        <Card className="textile-hover textile-shadow">
          <CardHeader>
            <CardTitle>Recent Posts</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="aspect-square bg-muted rounded-lg flex items-center justify-center">
                <Image className="h-8 w-8 text-muted-foreground" />
              </div>
              <div className="aspect-square bg-muted rounded-lg flex items-center justify-center">
                <Image className="h-8 w-8 text-muted-foreground" />
              </div>
              <div className="aspect-square bg-muted rounded-lg flex items-center justify-center">
                <Image className="h-8 w-8 text-muted-foreground" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
  )
}
