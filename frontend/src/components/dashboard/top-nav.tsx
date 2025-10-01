"use client"

import { Bell, Search, User } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { AuthUserButton } from "@/components/auth/user-button"
import { cn } from "@/lib/utils"

interface TopNavProps {
  className?: string
}

export function TopNav({ className }: TopNavProps) {
  return (
    <header className={cn(
      "bg-card border-b border-border textile-shadow",
      className
    )}>
      <div className="flex items-center justify-between px-6 py-4">
        {/* Search */}
        <div className="flex-1 max-w-md">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search posts, templates, analytics..."
              className="pl-10 bg-input border-border focus:ring-2 focus:ring-ring"
            />
          </div>
        </div>

        {/* Right side */}
        <div className="flex items-center space-x-4">
          {/* Notifications */}
          <Button variant="ghost" size="icon" className="relative">
            <Bell className="h-5 w-5" />
            <span className="absolute -top-1 -right-1 h-3 w-3 bg-accent rounded-full"></span>
          </Button>

          {/* User Menu */}
          <div className="flex items-center space-x-3">
            <div className="text-right">
              <p className="text-sm font-medium text-foreground">Sarah Chen</p>
              <p className="text-xs text-muted-foreground">Textile Designer</p>
            </div>
            <AuthUserButton />
          </div>
        </div>
      </div>
    </header>
  )
}

