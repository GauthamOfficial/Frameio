"use client"

import { useOrganization } from '@/contexts/organization-context'
import { useUser } from '@clerk/nextjs'
import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import { Loader2, Shield, AlertTriangle } from 'lucide-react'

interface AdminRouteProtectionProps {
  children: React.ReactNode
  fallback?: React.ReactNode
}

export default function AdminRouteProtection({ children, fallback }: AdminRouteProtectionProps) {
  const { userRole, isLoading, error } = useOrganization()
  const { user, isLoaded } = useUser()
  const router = useRouter()
  const [isChecking, setIsChecking] = useState(true)

  useEffect(() => {
    if (isLoaded && user && !isLoading) {
      // Check if user has admin role
      if (userRole !== 'Admin') {
        // Redirect non-admin users after a short delay
        const timer = setTimeout(() => {
          router.push('/dashboard')
        }, 2000)
        
        setIsChecking(false)
        return () => clearTimeout(timer)
      }
      setIsChecking(false)
    }
  }, [user, isLoaded, userRole, isLoading, router])

  // Show loading while checking authentication and role
  if (!isLoaded || isLoading || isChecking) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto text-blue-600" />
          <p className="mt-2 text-gray-600">Verifying admin access...</p>
        </div>
      </div>
    )
  }

  // Show error if there's an authentication error
  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center max-w-md mx-auto p-6">
          <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Access Error</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={() => router.push('/dashboard')}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Go to Dashboard
          </button>
        </div>
      </div>
    )
  }

  // Show access denied for non-admin users
  if (userRole !== 'Admin') {
    return fallback || (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center max-w-md mx-auto p-6">
          <Shield className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Access Denied</h2>
          <p className="text-gray-600 mb-4">
            You don't have permission to access the admin panel. This area is restricted to administrators only.
          </p>
          <div className="space-y-2">
            <p className="text-sm text-gray-500">Redirecting to dashboard...</p>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div className="bg-blue-600 h-2 rounded-full animate-pulse" style={{ width: '100%' }}></div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // Show admin content for admin users
  return <>{children}</>
}
