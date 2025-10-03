"use client"

import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Switch } from "@/components/ui/switch"
import { 
  Settings, 
  Save,
  Shield,
  Bell,
  Database,
  Key,
  Globe,
  Mail
} from "lucide-react"

export default function AdminSettings() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Admin Settings</h1>
        <p className="text-gray-600 mt-2">Configure system-wide settings and preferences</p>
      </div>

      {/* General Settings */}
      <Card className="p-6">
        <div className="flex items-center space-x-3 mb-6">
          <Settings className="w-6 h-6 text-blue-600" />
          <h2 className="text-xl font-semibold text-gray-900">General Settings</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-2">
            <Label htmlFor="site-name">Site Name</Label>
            <Input
              id="site-name"
              defaultValue="Frameio"
              placeholder="Enter site name"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="site-url">Site URL</Label>
            <Input
              id="site-url"
              defaultValue="https://frameio.com"
              placeholder="Enter site URL"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="admin-email">Admin Email</Label>
            <Input
              id="admin-email"
              type="email"
              defaultValue="admin@frameio.com"
              placeholder="Enter admin email"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="timezone">Timezone</Label>
            <Input
              id="timezone"
              defaultValue="UTC"
              placeholder="Enter timezone"
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

      {/* Security Settings */}
      <Card className="p-6">
        <div className="flex items-center space-x-3 mb-6">
          <Shield className="w-6 h-6 text-blue-600" />
          <h2 className="text-xl font-semibold text-gray-900">Security Settings</h2>
        </div>

        <div className="space-y-6">
          <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
            <div>
              <h3 className="font-medium text-gray-900">Two-Factor Authentication</h3>
              <p className="text-sm text-gray-600">Require 2FA for all users</p>
            </div>
            <Switch />
          </div>

          <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
            <div>
              <h3 className="font-medium text-gray-900">Session Timeout</h3>
              <p className="text-sm text-gray-600">Auto-logout after 30 minutes of inactivity</p>
            </div>
            <Switch defaultChecked />
          </div>

          <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
            <div>
              <h3 className="font-medium text-gray-900">IP Restrictions</h3>
              <p className="text-sm text-gray-600">Limit access to specific IP ranges</p>
            </div>
            <Switch />
          </div>

          <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
            <div>
              <h3 className="font-medium text-gray-900">Password Policy</h3>
              <p className="text-sm text-gray-600">Enforce strong password requirements</p>
            </div>
            <Switch defaultChecked />
          </div>
        </div>
      </Card>

      {/* Notification Settings */}
      <Card className="p-6">
        <div className="flex items-center space-x-3 mb-6">
          <Bell className="w-6 h-6 text-blue-600" />
          <h2 className="text-xl font-semibold text-gray-900">Notification Settings</h2>
        </div>

        <div className="space-y-6">
          <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
            <div>
              <h3 className="font-medium text-gray-900">Email Notifications</h3>
              <p className="text-sm text-gray-600">Send email notifications for system events</p>
            </div>
            <Switch defaultChecked />
          </div>

          <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
            <div>
              <h3 className="font-medium text-gray-900">User Registration Alerts</h3>
              <p className="text-sm text-gray-600">Notify admins when new users register</p>
            </div>
            <Switch defaultChecked />
          </div>

          <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
            <div>
              <h3 className="font-medium text-gray-900">System Alerts</h3>
              <p className="text-sm text-gray-600">Send alerts for system issues</p>
            </div>
            <Switch defaultChecked />
          </div>
        </div>
      </Card>

      {/* API Settings */}
      <Card className="p-6">
        <div className="flex items-center space-x-3 mb-6">
          <Key className="w-6 h-6 text-blue-600" />
          <h2 className="text-xl font-semibold text-gray-900">API Settings</h2>
        </div>

        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="api-key">API Key</Label>
            <Input
              id="api-key"
              type="password"
              defaultValue="sk-1234567890abcdef"
              placeholder="Enter API key"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="rate-limit">Rate Limit (requests per minute)</Label>
            <Input
              id="rate-limit"
              type="number"
              defaultValue="1000"
              placeholder="Enter rate limit"
            />
          </div>

          <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
            <div>
              <h3 className="font-medium text-gray-900">API Access Logging</h3>
              <p className="text-sm text-gray-600">Log all API requests for debugging</p>
            </div>
            <Switch defaultChecked />
          </div>
        </div>
      </Card>

      {/* Database Settings */}
      <Card className="p-6">
        <div className="flex items-center space-x-3 mb-6">
          <Database className="w-6 h-6 text-blue-600" />
          <h2 className="text-xl font-semibold text-gray-900">Database Settings</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-2">
            <Label htmlFor="db-host">Database Host</Label>
            <Input
              id="db-host"
              defaultValue="localhost"
              placeholder="Enter database host"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="db-port">Database Port</Label>
            <Input
              id="db-port"
              defaultValue="5432"
              placeholder="Enter database port"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="db-name">Database Name</Label>
            <Input
              id="db-name"
              defaultValue="frameio_db"
              placeholder="Enter database name"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="db-user">Database User</Label>
            <Input
              id="db-user"
              defaultValue="frameio_user"
              placeholder="Enter database user"
            />
          </div>
        </div>

        <div className="flex justify-end mt-6">
          <Button variant="outline" className="mr-2">Test Connection</Button>
          <Button className="flex items-center space-x-2">
            <Save className="w-4 h-4" />
            <span>Save Changes</span>
          </Button>
        </div>
      </Card>
    </div>
  )
}