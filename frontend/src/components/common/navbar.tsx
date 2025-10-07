"use client"

import { UserButton } from "@clerk/nextjs"
import { useOrganization } from "@/contexts/organization-context"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { 
  Bell, 
  Search, 
  Settings, 
  LogOut,
  User,
  Building2
} from "lucide-react"

interface NavbarProps {
  title?: string
  showSearch?: boolean
  showNotifications?: boolean
  className?: string
}

export function Navbar({ 
  title = "Frameio", 
  showSearch = true, 
  showNotifications = true,
  className = ""
}: NavbarProps) {
  const { userRole, organizationId } = useOrganization()

  return (
    <header className={`bg-white border-b border-gray-200 px-6 py-4 w-full ${className}`}>
      <div className="flex items-center justify-between w-full">
        <div className="flex items-center space-x-4">
          <h1 className="text-xl font-semibold text-gray-900">{title}</h1>
          {organizationId && (
            <div className="flex items-center text-sm text-gray-500">
              <Building2 className="w-4 h-4 mr-1" />
              Organization ID: {organizationId.slice(0, 8)}...
            </div>
          )}
        </div>

        <div className="flex items-center space-x-4">
          {showSearch && (
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Search..."
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          )}

          {showNotifications && (
            <Button variant="ghost" size="sm" className="relative">
              <Bell className="w-5 h-5" />
              <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                3
              </span>
            </Button>
          )}

          <div className="flex items-center space-x-3">
            <Badge 
              variant="secondary"
              className="flex items-center space-x-1"
            >
              <User className="w-3 h-3" />
              <span>{userRole}</span>
            </Badge>
            <UserButton 
              afterSignOutUrl="/"
              appearance={{
                elements: {
                  avatarBox: "w-8 h-8"
                }
              }}
            />
          </div>
        </div>
      </div>
    </header>
  )
}
