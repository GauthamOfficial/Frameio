"use client"

import { useState, useEffect } from 'react'
import { useUser } from '@clerk/nextjs'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { useOrganization } from "@/contexts/organization-context"
import { 
  User, 
  Lock
} from "lucide-react"
import CompanyProfileSettings from "@/components/settings/CompanyProfileSettings"

export default function SettingsPage() {
  const { user } = useUser()
  const { isLoading: orgLoading } = useOrganization()
  const [loading, setLoading] = useState(true)
  const [clerkConfigured, setClerkConfigured] = useState(false)

  // Profile settings
  const [profileData, setProfileData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    phone: ''
  })


  useEffect(() => {
    // Check if Clerk is configured
    const isClerkConfigured = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY && 
                             process.env.NEXT_PUBLIC_CLERK_FRONTEND_API
    setClerkConfigured(!!isClerkConfigured)
    
    if (user && !orgLoading) {
      // Load user data
      setProfileData({
        firstName: user.firstName || '',
        lastName: user.lastName || '',
        email: user.primaryEmailAddress?.emailAddress || '',
        phone: user.phoneNumbers?.[0]?.phoneNumber || ''
      })
      setLoading(false)
    } else if (!isClerkConfigured) {
      // In development mode without Clerk, just set loading to false
      console.log('⚠️ Clerk not configured, running in development mode')
      setLoading(false)
    }
  }, [user, orgLoading])


  if (loading || orgLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="w-8 h-8 bg-primary rounded-lg mx-auto mb-4 animate-pulse"></div>
          <p className="text-muted-foreground">Loading settings...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Settings</h1>
          <p className="text-muted-foreground mt-1">
            Manage your account settings and preferences.
          </p>
        </div>
      </div>

      {/* Clerk Configuration Warning */}
      {!clerkConfigured && (
        <Card className="border-yellow-200 bg-yellow-50">
          <CardHeader>
            <CardTitle className="flex items-center text-yellow-800">
              <Lock className="h-5 w-5 mr-2" />
              Development Mode
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-yellow-700">
              Clerk authentication is not configured. You're running in development mode. 
              To enable full authentication features, run: <code className="bg-yellow-100 px-2 py-1 rounded">node setup-clerk-env.js</code>
            </p>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-6">
        {/* Profile Settings */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <User className="h-5 w-5 mr-2" />
              Profile Information
            </CardTitle>
          </CardHeader>
          <CardContent>
            <CompanyProfileSettings />
          </CardContent>
        </Card>

      </div>
    </div>
  )
}
