"use client"

import { useState } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { useOrganization } from "@/contexts/organization-context"
import { 
  LayoutDashboard, 
  Image, 
  BookOpen, 
  Palette, 
  Share2, 
  Calendar,
  Library,
  BarChart3,
  Settings,
  Menu,
  X,
  Users,
  CreditCard,
  Building
} from "lucide-react"

const getNavigationItems = (userRole: string | null, permissions: string[]) => {
  const baseItems = [
    { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard, permission: null },
    { name: "AI Poster Generator", href: "/dashboard/poster-generator", icon: Image, permission: "manage_designs" },
    { name: "Catalog Builder", href: "/dashboard/catalog-builder", icon: BookOpen, permission: "manage_designs" },
    { name: "Branding Kit", href: "/dashboard/branding-kit", icon: Palette, permission: "manage_designs" },
    { name: "Social Media Posts", href: "/dashboard/social-media", icon: Share2, permission: "manage_designs" },
    { name: "Scheduler", href: "/dashboard/scheduler", icon: Calendar, permission: "manage_designs" },
    { name: "Templates Library", href: "/dashboard/templates", icon: Library, permission: "view_templates" },
    { name: "Analytics", href: "/dashboard/analytics", icon: BarChart3, permission: "view_analytics" },
  ]

  const adminItems = [
    { name: "User Management", href: "/dashboard/users", icon: Users, permission: "manage_users" },
    { name: "Organization Settings", href: "/dashboard/organization", icon: Building, permission: "manage_organization" },
    { name: "Billing", href: "/dashboard/billing", icon: CreditCard, permission: "view_billing" },
  ]

  // Filter items based on permissions
  const filteredBaseItems = baseItems.filter(item => 
    !item.permission || permissions.includes(item.permission)
  )

  const filteredAdminItems = adminItems.filter(item => 
    permissions.includes(item.permission)
  )

  return [...filteredBaseItems, ...filteredAdminItems]
}

interface SidebarProps {
  className?: string
}

export function Sidebar({ className }: SidebarProps) {
  const [isMobileOpen, setIsMobileOpen] = useState(false)
  const pathname = usePathname()
  const { userRole, permissions, isLoading } = useOrganization()

  // Debug logging
  console.log('Sidebar Debug:', { userRole, permissions, isLoading })

  // Get navigation items based on user role and permissions
  const navigationItems = getNavigationItems(userRole, permissions)
  
  console.log('Navigation Items:', navigationItems)

  if (isLoading) {
    return (
      <div className="fixed inset-y-0 left-0 z-40 w-64 bg-sidebar border-r border-sidebar-border">
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <div className="w-8 h-8 bg-primary rounded-lg mx-auto mb-4 animate-pulse"></div>
            <p className="text-muted-foreground">Loading...</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <>
      {/* Mobile menu button */}
      <Button
        variant="ghost"
        size="icon"
        className="md:hidden fixed top-4 left-4 z-50 bg-card textile-shadow"
        onClick={() => setIsMobileOpen(!isMobileOpen)}
      >
        {isMobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
      </Button>

      {/* Sidebar */}
      <div className={cn(
        "fixed inset-y-0 left-0 z-40 w-64 bg-sidebar border-r border-sidebar-border transform transition-transform duration-300 ease-in-out md:translate-x-0",
        isMobileOpen ? "translate-x-0" : "-translate-x-full",
        className
      )}>
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center px-6 py-4 border-b border-sidebar-border">
            <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center mr-3">
              <span className="text-primary-foreground font-bold text-lg">F</span>
            </div>
            <span className="text-xl font-bold text-sidebar-foreground">Frameio</span>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-2">
            {navigationItems.map((item) => {
              const isActive = pathname === item.href
              const Icon = item.icon
              
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  onClick={() => setIsMobileOpen(false)}
                  className={cn(
                    "flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 textile-hover",
                    isActive
                      ? "bg-sidebar-primary text-sidebar-primary-foreground textile-shadow"
                      : "text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
                  )}
                >
                  <Icon className="mr-3 h-5 w-5" />
                  {item.name}
                </Link>
              )
            })}
          </nav>

          {/* Settings */}
          <div className="px-4 py-4 border-t border-sidebar-border">
            <Link
              href="/dashboard/settings"
              className={cn(
                "flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 textile-hover",
                pathname === "/dashboard/settings"
                  ? "bg-sidebar-primary text-sidebar-primary-foreground textile-shadow"
                  : "text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
              )}
            >
              <Settings className="mr-3 h-5 w-5" />
              Settings
            </Link>
          </div>
        </div>
      </div>

      {/* Mobile overlay */}
      {isMobileOpen && (
        <div 
          className="fixed inset-0 z-30 bg-black/50 md:hidden"
          onClick={() => setIsMobileOpen(false)}
        />
      )}
    </>
  )
}

