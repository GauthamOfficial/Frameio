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
      <div className="flex items-center px-3 sm:px-4 md:px-6 py-3 sm:py-4">
        {/* Left spacer to help center nav */}
        <div className="hidden md:flex flex-1" />

        {/* Navigation Links */}
        <div className="hidden md:flex flex-1 justify-center">
          <nav className="flex items-center space-x-4 lg:space-x-6 mx-6">
            <Link
              href="/"
              className="text-sm font-medium text-[#8B2635] hover:text-[#8B2635]/80 transition-colors duration-200 px-2 lg:px-3 py-2 rounded-md hover:bg-[#8B2635]/10"
            >
              Home
            </Link>
            <Link
              href="/about"
              className="text-sm font-medium text-[#8B2635] hover:text-[#8B2635]/80 transition-colors duration-200 px-2 lg:px-3 py-2 rounded-md hover:bg-[#8B2635]/10"
            >
              About
            </Link>
            <Link
              href="/contact"
              className="text-sm font-medium text-[#8B2635] hover:text-[#8B2635]/80 transition-colors duration-200 px-2 lg:px-3 py-2 rounded-md hover:bg-[#8B2635]/10"
            >
              Contact Us
            </Link>
          </nav>
        </div>

        {/* Right side */}
        <div className="flex items-center gap-2 sm:gap-3 md:gap-4 flex-1 md:flex-1 justify-end">
          {/* Notifications */}
          <Button variant="ghost" size="icon" className="relative h-8 w-8 sm:h-10 sm:w-10">
            <Bell className="h-4 w-4 sm:h-5 sm:w-5" />
            <span className="absolute -top-1 -right-1 h-2.5 w-2.5 sm:h-3 sm:w-3 bg-accent rounded-full"></span>
          </Button>

          {/* User Menu */}
          <div className="flex items-center gap-2 sm:gap-3">
            <div className="hidden sm:block text-right">
              <p className="text-xs sm:text-sm font-medium text-foreground truncate max-w-[100px] sm:max-w-none">
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

