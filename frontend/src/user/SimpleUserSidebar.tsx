"use client"

import { useState } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Logo } from "@/components/common/logo"
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
  X
} from "lucide-react"

const userNavigationItems = [
  { name: "Dashboard", href: "/user", icon: LayoutDashboard },
  { name: "AI Poster Generator", href: "/user/poster-generator", icon: Image },
  { name: "Branding Kit", href: "/user/branding-kit", icon: Palette },
  { name: "Social Media Posts", href: "/user/social-media", icon: Share2 },
  { name: "Scheduler", href: "/user/scheduler", icon: Calendar },
  { name: "Templates Library", href: "/user/templates", icon: Library },
  { name: "Analytics", href: "/user/analytics", icon: BarChart3 },
]

interface SimpleUserSidebarProps {
  className?: string
}

export function SimpleUserSidebar({ className }: SimpleUserSidebarProps) {
  const [isMobileOpen, setIsMobileOpen] = useState(false)
  const pathname = usePathname()

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
          <div className="px-6 py-4 border-b border-sidebar-border">
            <Link href="/">
              <Logo className="mr-3" />
            </Link>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-2">
            {userNavigationItems.map((item) => {
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
              href="/user/settings"
              className={cn(
                "flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 textile-hover",
                pathname === "/user/settings"
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
