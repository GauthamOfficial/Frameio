"use client"

import { Bell } from "lucide-react"
import { Button } from "@/components/ui/button"
import { AuthUserButton } from "@/components/auth/user-button"
import { useOrganization } from "@/contexts/organization-context"
import { useUser } from "@/hooks/useAuth"
import { cn } from "@/lib/utils"
import Link from "next/link"

interface TopNavProps {
  className?: string
}

export function TopNav({ className }: TopNavProps) {
  const { user } = useUser()
  const { userRole, isLoading } = useOrganization()

  return (
    <header className={cn(
      "bg-card border-b border-border textile-shadow",
      className
    )}>
      <div className="flex items-center px-6 py-4">
        {/* Left spacer to help center nav */}
        <div className="flex-1" />

        {/* Navigation Links */}
        <div className="flex-1 flex justify-center">
          <nav className="hidden md:flex items-center space-x-6 mx-6">
            <Link
              href="/"
              className="text-sm font-medium text-[#8B2635] hover:text-[#8B2635]/80 transition-colors duration-200 px-3 py-2 rounded-md hover:bg-[#8B2635]/10"
            >
              Home
            </Link>
            <Link
              href="/about"
              className="text-sm font-medium text-[#8B2635] hover:text-[#8B2635]/80 transition-colors duration-200 px-3 py-2 rounded-md hover:bg-[#8B2635]/10"
            >
              About
            </Link>
            <Link
              href="/contact"
              className="text-sm font-medium text-[#8B2635] hover:text-[#8B2635]/80 transition-colors duration-200 px-3 py-2 rounded-md hover:bg-[#8B2635]/10"
            >
              Contact Us
            </Link>
          </nav>
        </div>

        {/* Right side */}
        <div className="flex items-center space-x-4 flex-1 justify-end">
          {/* Notifications */}
          <Button variant="ghost" size="icon" className="relative">
            <Bell className="h-5 w-5" />
            <span className="absolute -top-1 -right-1 h-3 w-3 bg-accent rounded-full"></span>
          </Button>

          {/* User Menu */}
          <div className="flex items-center space-x-3">
            <div className="text-right">
              <p className="text-sm font-medium text-foreground">
                {user?.first_name || user?.username || user?.email || 'User'}
              </p>
              {userRole && !isLoading && (
                <p className="text-xs text-muted-foreground">
                  {userRole}
                </p>
              )}
            </div>
            <AuthUserButton />
          </div>
        </div>
      </div>
    </header>
  )
}

