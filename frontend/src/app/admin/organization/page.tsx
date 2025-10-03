"use client"

import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { 
  Building2, 
  Users, 
  Settings, 
  Save,
  Upload,
  Globe,
  Mail,
  Phone
} from "lucide-react"

export default function OrganizationSettings() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Organization Settings</h1>
        <p className="text-gray-600 mt-2">Manage your organization's information and preferences</p>
      </div>

      {/* Organization Info */}
      <Card className="p-6">
        <div className="flex items-center space-x-3 mb-6">
          <Building2 className="w-6 h-6 text-blue-600" />
          <h2 className="text-xl font-semibold text-gray-900">Organization Information</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-2">
            <Label htmlFor="org-name">Organization Name</Label>
            <Input
              id="org-name"
              defaultValue="Acme Textile Company"
              placeholder="Enter organization name"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="org-domain">Domain</Label>
            <Input
              id="org-domain"
              defaultValue="acmetextile.com"
              placeholder="Enter domain"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="org-email">Contact Email</Label>
            <Input
              id="org-email"
              type="email"
              defaultValue="contact@acmetextile.com"
              placeholder="Enter contact email"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="org-phone">Phone Number</Label>
            <Input
              id="org-phone"
              defaultValue="+1 (555) 123-4567"
              placeholder="Enter phone number"
            />
          </div>

          <div className="md:col-span-2 space-y-2">
            <Label htmlFor="org-description">Description</Label>
            <Textarea
              id="org-description"
              defaultValue="Leading textile manufacturer specializing in sustainable fabrics and innovative design solutions."
              placeholder="Enter organization description"
              rows={3}
            />
          </div>
        </div>

        <div className="flex justify-end mt-6">
          <Button className="flex items-center space-x-2">
            <Save className="w-4 h-4" />
            <span>Save Changes</span>
          </Button>
        </div>
      </Card>

      {/* Organization Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Users</p>
              <p className="text-2xl font-bold text-gray-900">24</p>
            </div>
            <Users className="w-8 h-8 text-blue-600" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Projects</p>
              <p className="text-2xl font-bold text-gray-900">12</p>
            </div>
            <Building2 className="w-8 h-8 text-green-600" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Storage Used</p>
              <p className="text-2xl font-bold text-gray-900">2.4 GB</p>
            </div>
            <Settings className="w-8 h-8 text-purple-600" />
          </div>
        </Card>
      </div>

      {/* Logo Upload */}
      <Card className="p-6">
        <div className="flex items-center space-x-3 mb-6">
          <Upload className="w-6 h-6 text-blue-600" />
          <h2 className="text-xl font-semibold text-gray-900">Organization Logo</h2>
        </div>

        <div className="flex items-center space-x-6">
          <div className="w-20 h-20 bg-gray-100 rounded-lg flex items-center justify-center">
            <Building2 className="w-8 h-8 text-gray-400" />
          </div>
          <div>
            <Button variant="outline" className="mb-2">
              <Upload className="w-4 h-4 mr-2" />
              Upload Logo
            </Button>
            <p className="text-sm text-gray-600">PNG, JPG up to 2MB</p>
          </div>
        </div>
      </Card>

      {/* Security Settings */}
      <Card className="p-6">
        <div className="flex items-center space-x-3 mb-6">
          <Settings className="w-6 h-6 text-blue-600" />
          <h2 className="text-xl font-semibold text-gray-900">Security Settings</h2>
        </div>

        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
            <div>
              <h3 className="font-medium text-gray-900">Two-Factor Authentication</h3>
              <p className="text-sm text-gray-600">Require 2FA for all users</p>
            </div>
            <Button variant="outline" size="sm">Enable</Button>
          </div>

          <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
            <div>
              <h3 className="font-medium text-gray-900">Session Timeout</h3>
              <p className="text-sm text-gray-600">Auto-logout after inactivity</p>
            </div>
            <Button variant="outline" size="sm">Configure</Button>
          </div>

          <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
            <div>
              <h3 className="font-medium text-gray-900">IP Restrictions</h3>
              <p className="text-sm text-gray-600">Limit access to specific IP ranges</p>
            </div>
            <Button variant="outline" size="sm">Configure</Button>
          </div>
        </div>
      </Card>
    </div>
  )
}
