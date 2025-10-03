"use client"

import { useState, useEffect } from 'react'
import { useUser, useAuth } from '@clerk/nextjs'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { useOrganization } from "@/contexts/organization-context"
import { 
  User, 
  Bell, 
  Shield, 
  Palette, 
  Globe,
  Save,
  Check
} from "lucide-react"

export default function SettingsPage() {
  const { user } = useUser()
  const { getToken } = useAuth()
  const { userRole, permissions, isLoading: orgLoading } = useOrganization()
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [success, setSuccess] = useState<string | null>(null)

  // Profile settings
  const [profileData, setProfileData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    phone: ''
  })

  // Notification settings
  const [notifications, setNotifications] = useState({
    emailNotifications: true,
    pushNotifications: true,
    marketingEmails: false,
    designUpdates: true,
    billingAlerts: true
  })

  // Appearance settings
  const [appearance, setAppearance] = useState({
    theme: 'light',
    language: 'en',
    timezone: 'UTC'
  })

  // Security settings
  const [security, setSecurity] = useState({
    twoFactorEnabled: false,
    sessionTimeout: 30,
    loginAlerts: true
  })

  useEffect(() => {
    if (user && !orgLoading) {
      // Load user data
      setProfileData({
        firstName: user.firstName || '',
        lastName: user.lastName || '',
        email: user.primaryEmailAddress?.emailAddress || '',
        phone: user.phoneNumbers?.[0]?.phoneNumber || ''
      })
      setLoading(false)
    }
  }, [user, orgLoading])

  const handleSave = async (section: string) => {
    setSaving(true)
    setSuccess(null)

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      setSuccess(`${section} settings saved successfully!`)
      setTimeout(() => setSuccess(null), 3000)
    } catch (error) {
      console.error('Failed to save settings:', error)
    } finally {
      setSaving(false)
    }
  }

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
        {success && (
          <div className="flex items-center text-green-600">
            <Check className="h-4 w-4 mr-2" />
            {success}
          </div>
        )}
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
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="firstName">First Name</Label>
                <Input
                  id="firstName"
                  value={profileData.firstName}
                  onChange={(e) => setProfileData(prev => ({ ...prev, firstName: e.target.value }))}
                />
              </div>
              <div>
                <Label htmlFor="lastName">Last Name</Label>
                <Input
                  id="lastName"
                  value={profileData.lastName}
                  onChange={(e) => setProfileData(prev => ({ ...prev, lastName: e.target.value }))}
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={profileData.email}
                  onChange={(e) => setProfileData(prev => ({ ...prev, email: e.target.value }))}
                />
              </div>
              <div>
                <Label htmlFor="phone">Phone</Label>
                <Input
                  id="phone"
                  value={profileData.phone}
                  onChange={(e) => setProfileData(prev => ({ ...prev, phone: e.target.value }))}
                />
              </div>
            </div>
            <Button 
              onClick={() => handleSave('Profile')}
              disabled={saving}
              className="w-full sm:w-auto"
            >
              <Save className="h-4 w-4 mr-2" />
              {saving ? 'Saving...' : 'Save Profile'}
            </Button>
          </CardContent>
        </Card>

        {/* Notification Settings */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Bell className="h-5 w-5 mr-2" />
              Notifications
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <Label htmlFor="emailNotifications">Email Notifications</Label>
                <p className="text-sm text-muted-foreground">Receive notifications via email</p>
              </div>
              <Switch
                id="emailNotifications"
                checked={notifications.emailNotifications}
                onCheckedChange={(checked) => setNotifications(prev => ({ ...prev, emailNotifications: checked }))}
              />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <Label htmlFor="pushNotifications">Push Notifications</Label>
                <p className="text-sm text-muted-foreground">Receive push notifications in browser</p>
              </div>
              <Switch
                id="pushNotifications"
                checked={notifications.pushNotifications}
                onCheckedChange={(checked) => setNotifications(prev => ({ ...prev, pushNotifications: checked }))}
              />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <Label htmlFor="marketingEmails">Marketing Emails</Label>
                <p className="text-sm text-muted-foreground">Receive promotional content and updates</p>
              </div>
              <Switch
                id="marketingEmails"
                checked={notifications.marketingEmails}
                onCheckedChange={(checked) => setNotifications(prev => ({ ...prev, marketingEmails: checked }))}
              />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <Label htmlFor="designUpdates">Design Updates</Label>
                <p className="text-sm text-muted-foreground">Get notified about new design features</p>
              </div>
              <Switch
                id="designUpdates"
                checked={notifications.designUpdates}
                onCheckedChange={(checked) => setNotifications(prev => ({ ...prev, designUpdates: checked }))}
              />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <Label htmlFor="billingAlerts">Billing Alerts</Label>
                <p className="text-sm text-muted-foreground">Receive billing and subscription alerts</p>
              </div>
              <Switch
                id="billingAlerts"
                checked={notifications.billingAlerts}
                onCheckedChange={(checked) => setNotifications(prev => ({ ...prev, billingAlerts: checked }))}
              />
            </div>
            <Button 
              onClick={() => handleSave('Notification')}
              disabled={saving}
              className="w-full sm:w-auto"
            >
              <Save className="h-4 w-4 mr-2" />
              {saving ? 'Saving...' : 'Save Notifications'}
            </Button>
          </CardContent>
        </Card>

        {/* Appearance Settings */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Palette className="h-5 w-5 mr-2" />
              Appearance
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-3 gap-4">
              <div>
                <Label htmlFor="theme">Theme</Label>
                <select
                  id="theme"
                  value={appearance.theme}
                  onChange={(e) => setAppearance(prev => ({ ...prev, theme: e.target.value }))}
                  className="w-full p-2 border rounded-md"
                >
                  <option value="light">Light</option>
                  <option value="dark">Dark</option>
                  <option value="system">System</option>
                </select>
              </div>
              <div>
                <Label htmlFor="language">Language</Label>
                <select
                  id="language"
                  value={appearance.language}
                  onChange={(e) => setAppearance(prev => ({ ...prev, language: e.target.value }))}
                  className="w-full p-2 border rounded-md"
                >
                  <option value="en">English</option>
                  <option value="es">Spanish</option>
                  <option value="fr">French</option>
                </select>
              </div>
              <div>
                <Label htmlFor="timezone">Timezone</Label>
                <select
                  id="timezone"
                  value={appearance.timezone}
                  onChange={(e) => setAppearance(prev => ({ ...prev, timezone: e.target.value }))}
                  className="w-full p-2 border rounded-md"
                >
                  <option value="UTC">UTC</option>
                  <option value="EST">Eastern Time</option>
                  <option value="PST">Pacific Time</option>
                </select>
              </div>
            </div>
            <Button 
              onClick={() => handleSave('Appearance')}
              disabled={saving}
              className="w-full sm:w-auto"
            >
              <Save className="h-4 w-4 mr-2" />
              {saving ? 'Saving...' : 'Save Appearance'}
            </Button>
          </CardContent>
        </Card>

        {/* Security Settings */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Shield className="h-5 w-5 mr-2" />
              Security
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <Label htmlFor="twoFactorEnabled">Two-Factor Authentication</Label>
                <p className="text-sm text-muted-foreground">Add an extra layer of security to your account</p>
              </div>
              <Switch
                id="twoFactorEnabled"
                checked={security.twoFactorEnabled}
                onCheckedChange={(checked) => setSecurity(prev => ({ ...prev, twoFactorEnabled: checked }))}
              />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <Label htmlFor="loginAlerts">Login Alerts</Label>
                <p className="text-sm text-muted-foreground">Get notified of new login attempts</p>
              </div>
              <Switch
                id="loginAlerts"
                checked={security.loginAlerts}
                onCheckedChange={(checked) => setSecurity(prev => ({ ...prev, loginAlerts: checked }))}
              />
            </div>
            <div>
              <Label htmlFor="sessionTimeout">Session Timeout (minutes)</Label>
              <Input
                id="sessionTimeout"
                type="number"
                value={security.sessionTimeout}
                onChange={(e) => setSecurity(prev => ({ ...prev, sessionTimeout: parseInt(e.target.value) || 30 }))}
                className="w-32"
              />
            </div>
            <Button 
              onClick={() => handleSave('Security')}
              disabled={saving}
              className="w-full sm:w-auto"
            >
              <Save className="h-4 w-4 mr-2" />
              {saving ? 'Saving...' : 'Save Security'}
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
