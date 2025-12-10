"use client"

import { useState, useEffect } from 'react'
import { useUser } from '@/hooks/useAuth'
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
  // Profile settings (kept for future use)
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [profileData, setProfileData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    phone: ''
  })


  useEffect(() => {
    if (user && !orgLoading) {
      // Load user data
      setProfileData({
        firstName: user.first_name || '',
        lastName: user.last_name || '',
        email: user.email || '',
        phone: user.phone_number || ''
      })
      setLoading(false)
    } else if (!user && !orgLoading) {
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
