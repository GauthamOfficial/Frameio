"use client"

import { useState, useEffect } from 'react'
import { useUser, useAuth } from '@clerk/nextjs'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useOrganization } from "@/contexts/organization-context"
import { organizationApi, Organization } from "@/lib/api"
import { 
  Building, 
  Save, 
  Users, 
  Globe,
  Calendar,
  Shield
} from "lucide-react"

export default function OrganizationPage() {
  const { user } = useUser()
  const { getToken } = useAuth()
  const { userRole, permissions, isLoading: orgLoading } = useOrganization()
  const [organization, setOrganization] = useState<Organization | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  
  const [formData, setFormData] = useState({
    name: '',
    domain: ''
  })

  // Check if user has permission to access this page
  if (!orgLoading && !permissions.includes('manage_organization')) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <Shield className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-foreground mb-2">Access Denied</h2>
          <p className="text-muted-foreground">
            You don't have permission to manage organization settings
          </p>
        </div>
      </div>
    )
  }

  const fetchOrganization = async () => {
    if (!user) return

    try {
      setLoading(true)
      setError(null)
      const token = await getToken()
      const orgData = await organizationApi.getOrganization(token)
      setOrganization(orgData)
      setFormData({
        name: orgData.name,
        domain: orgData.domain
      })
    } catch (err) {
      console.error('Failed to fetch organization:', err)
      setError('Failed to load')
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    if (!user || !organization) return

    try {
      setSaving(true)
      setError(null)
      setSuccess(null)
      
      const token = await getToken()
      const updatedOrg = await organizationApi.updateOrganization(formData, token)
      setOrganization(updatedOrg)
      setSuccess('Organization settings updated successfully!')
    } catch (err) {
      console.error('Failed to update organization:', err)
      setError('Failed to update organization settings')
    } finally {
      setSaving(false)
    }
  }

  useEffect(() => {
    if (user && permissions.includes('manage_organization')) {
      fetchOrganization()
    }
  }, [user, permissions])

  if (loading || orgLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="w-8 h-8 bg-primary rounded-lg mx-auto mb-4 animate-pulse"></div>
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Organization Settings</h1>
            <p className="text-muted-foreground mt-1">
              Manage your organization's settings and information.
            </p>
          </div>
        </div>

        {/* Organization Info Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card className="textile-hover textile-shadow">
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <Building className="h-5 w-5 text-chart-1" />
                <div>
                  <p className="text-2xl font-bold">{organization?.name || 'N/A'}</p>
                  <p className="text-xs text-muted-foreground">Organization Name</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card className="textile-hover textile-shadow">
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <Globe className="h-5 w-5 text-chart-2" />
                <div>
                  <p className="text-2xl font-bold">{organization?.domain || 'N/A'}</p>
                  <p className="text-xs text-muted-foreground">Domain</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card className="textile-hover textile-shadow">
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <Calendar className="h-5 w-5 text-chart-3" />
                <div>
                  <p className="text-2xl font-bold">
                    {organization?.created_at ? 
                      new Date(organization.created_at).toLocaleDateString() : 
                      'N/A'
                    }
                  </p>
                  <p className="text-xs text-muted-foreground">Created</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Organization Settings Form */}
        <Card className="textile-hover textile-shadow">
          <CardHeader>
            <CardTitle>Organization Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {error && (
              <div className="p-3 bg-destructive/10 border border-destructive/20 rounded-lg">
                <p className="text-destructive text-sm">{error}</p>
              </div>
            )}
            
            {success && (
              <div className="p-3 bg-green-500/10 border border-green-500/20 rounded-lg">
                <p className="text-green-600 text-sm">{success}</p>
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="name">Organization Name</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="Enter organization name"
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="domain">Domain</Label>
                <Input
                  id="domain"
                  value={formData.domain}
                  onChange={(e) => setFormData({ ...formData, domain: e.target.value })}
                  placeholder="Enter organization domain"
                />
              </div>
            </div>

            <div className="flex justify-end">
              <Button 
                onClick={handleSave}
                disabled={saving}
                className="bg-textile-accent"
              >
                {saving ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                    Saving...
                  </>
                ) : (
                  <>
                    <Save className="mr-2 h-4 w-4" />
                    Save Changes
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Organization Members */}
        <Card className="textile-hover textile-shadow">
          <CardHeader>
            <CardTitle className="flex items-center">
              <Users className="mr-2 h-5 w-5" />
              Organization Members
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-center py-8">
              <Users className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <p className="text-muted-foreground">
                View and manage organization members in the User Management section.
              </p>
              <Button 
                variant="outline" 
                className="mt-4"
                onClick={() => window.location.href = '/dashboard/users'}
              >
                Go to User Management
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
  )
}
