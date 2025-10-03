"use client"

import { Button } from "@/components/ui/button"
import { useOrganization } from "@/contexts/organization-context"
import { useRouter } from "next/navigation"

export function AdminSetup() {
  const { userRole, refreshUserData } = useOrganization()
  const router = useRouter()

  const setupAdminRole = () => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('user-role', 'Admin')
      localStorage.setItem('user-permissions', JSON.stringify([
        'manage_users',
        'manage_organization',
        'view_billing',
        'manage_designs',
        'view_analytics',
        'manage_templates'
      ]))
      
      refreshUserData()
      router.push('/admin')
    }
  }

  // Only show in development and if not already admin
  if (process.env.NODE_ENV !== 'development' || userRole === 'Admin') {
    return null
  }

  return (
    <div className="fixed bottom-4 left-4 bg-blue-50 border border-blue-200 rounded-lg p-4 shadow-lg z-50 max-w-sm">
      <div className="text-sm font-medium text-blue-900 mb-2">Development Helper</div>
      <div className="text-xs text-blue-700 mb-3">
        Click to test admin panel access
      </div>
      <Button 
        size="sm" 
        onClick={setupAdminRole}
        className="w-full"
      >
        Switch to Admin Role
      </Button>
    </div>
  )
}
