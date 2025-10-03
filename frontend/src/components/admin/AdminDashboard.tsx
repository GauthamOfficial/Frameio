"use client"

import { useState } from 'react'
import { useOrganization } from '@/contexts/organization-context'
import { 
  Users, 
  Building2, 
  CreditCard, 
  BarChart3, 
  Settings, 
  Shield, 
  Activity,
  UserPlus,
  FileText,
  Database,
  Zap,
  AlertCircle
} from 'lucide-react'

interface AdminStats {
  totalUsers: number
  activeUsers: number
  totalOrganizations: number
  monthlyRevenue: number
  aiGenerations: number
  systemHealth: 'healthy' | 'warning' | 'critical'
}

export default function AdminDashboard() {
  const { userRole, organizationId } = useOrganization()
  const [activeTab, setActiveTab] = useState('overview')
  const [stats, setStats] = useState<AdminStats>({
    totalUsers: 1247,
    activeUsers: 892,
    totalOrganizations: 156,
    monthlyRevenue: 45600,
    aiGenerations: 12847,
    systemHealth: 'healthy'
  })

  const tabs = [
    { id: 'overview', label: 'Overview', icon: BarChart3 },
    { id: 'users', label: 'User Management', icon: Users },
    { id: 'organizations', label: 'Organizations', icon: Building2 },
    { id: 'billing', label: 'Billing & Plans', icon: CreditCard },
    { id: 'analytics', label: 'Analytics', icon: Activity },
    { id: 'ai-services', label: 'AI Services', icon: Zap },
    { id: 'system', label: 'System Settings', icon: Settings },
  ]

  const renderOverview = () => (
    <div className="space-y-6">
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Users className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Users</p>
              <p className="text-2xl font-bold text-gray-900">{stats.totalUsers.toLocaleString()}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <Activity className="h-6 w-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Active Users</p>
              <p className="text-2xl font-bold text-gray-900">{stats.activeUsers.toLocaleString()}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 rounded-lg">
              <Building2 className="h-6 w-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Organizations</p>
              <p className="text-2xl font-bold text-gray-900">{stats.totalOrganizations}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <div className="p-2 bg-yellow-100 rounded-lg">
              <CreditCard className="h-6 w-6 text-yellow-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Monthly Revenue</p>
              <p className="text-2xl font-bold text-gray-900">${stats.monthlyRevenue.toLocaleString()}</p>
            </div>
          </div>
        </div>
      </div>

      {/* System Health */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">System Health</h3>
          <div className={`flex items-center px-3 py-1 rounded-full text-sm font-medium ${
            stats.systemHealth === 'healthy' 
              ? 'bg-green-100 text-green-800' 
              : stats.systemHealth === 'warning'
              ? 'bg-yellow-100 text-yellow-800'
              : 'bg-red-100 text-red-800'
          }`}>
            <div className={`w-2 h-2 rounded-full mr-2 ${
              stats.systemHealth === 'healthy' 
                ? 'bg-green-500' 
                : stats.systemHealth === 'warning'
                ? 'bg-yellow-500'
                : 'bg-red-500'
            }`} />
            {stats.systemHealth.charAt(0).toUpperCase() + stats.systemHealth.slice(1)}
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center">
            <p className="text-2xl font-bold text-gray-900">{stats.aiGenerations.toLocaleString()}</p>
            <p className="text-sm text-gray-600">AI Generations This Month</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-gray-900">99.9%</p>
            <p className="text-sm text-gray-600">Uptime</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-gray-900">2.3s</p>
            <p className="text-sm text-gray-600">Avg Response Time</p>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
        <div className="space-y-3">
          <div className="flex items-center justify-between py-2">
            <div className="flex items-center">
              <UserPlus className="h-4 w-4 text-green-600 mr-3" />
              <span className="text-sm text-gray-900">New user registered: john.doe@company.com</span>
            </div>
            <span className="text-xs text-gray-500">2 minutes ago</span>
          </div>
          <div className="flex items-center justify-between py-2">
            <div className="flex items-center">
              <Building2 className="h-4 w-4 text-blue-600 mr-3" />
              <span className="text-sm text-gray-900">New organization created: TechCorp Inc.</span>
            </div>
            <span className="text-xs text-gray-500">15 minutes ago</span>
          </div>
          <div className="flex items-center justify-between py-2">
            <div className="flex items-center">
              <Zap className="h-4 w-4 text-purple-600 mr-3" />
              <span className="text-sm text-gray-900">AI generation spike detected (+45%)</span>
            </div>
            <span className="text-xs text-gray-500">1 hour ago</span>
          </div>
        </div>
      </div>
    </div>
  )

  const renderUsers = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">User Management</h2>
        <button className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 flex items-center">
          <UserPlus className="h-4 w-4 mr-2" />
          Invite User
        </button>
      </div>
      
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">All Users</h3>
            <div className="flex space-x-2">
              <input
                type="text"
                placeholder="Search users..."
                className="px-3 py-2 border border-gray-300 rounded-md text-sm"
              />
              <select className="px-3 py-2 border border-gray-300 rounded-md text-sm">
                <option>All Roles</option>
                <option>Admin</option>
                <option>Manager</option>
                <option>Designer</option>
              </select>
            </div>
          </div>
          
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">User</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Role</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Organization</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Last Active</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                <tr>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="h-10 w-10 rounded-full bg-blue-500 flex items-center justify-center text-white font-medium">
                        JD
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-gray-900">John Doe</div>
                        <div className="text-sm text-gray-500">john.doe@company.com</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">
                      Admin
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">TechCorp Inc.</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                      Active
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">2 minutes ago</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button className="text-blue-600 hover:text-blue-900 mr-3">Edit</button>
                    <button className="text-red-600 hover:text-red-900">Remove</button>
                  </td>
                </tr>
                {/* Add more rows as needed */}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )

  const renderOrganizations = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Organization Management</h2>
        <button className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 flex items-center">
          <Building2 className="h-4 w-4 mr-2" />
          Create Organization
        </button>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">TechCorp Inc.</h3>
            <span className="px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-full">Active</span>
          </div>
          <div className="space-y-2 text-sm text-gray-600">
            <p>Plan: Premium</p>
            <p>Users: 25</p>
            <p>Created: Jan 15, 2024</p>
          </div>
        </div>
        {/* Add more organization cards */}
      </div>
    </div>
  )

  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview':
        return renderOverview()
      case 'users':
        return renderUsers()
      case 'organizations':
        return renderOrganizations()
      case 'billing':
        return <div className="text-center py-12 text-gray-500">Billing management coming soon...</div>
      case 'analytics':
        return <div className="text-center py-12 text-gray-500">Advanced analytics coming soon...</div>
      case 'ai-services':
        return <div className="text-center py-12 text-gray-500">AI services management coming soon...</div>
      case 'system':
        return <div className="text-center py-12 text-gray-500">System settings coming soon...</div>
      default:
        return renderOverview()
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <Shield className="h-8 w-8 text-blue-600 mr-3" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Admin Dashboard</h1>
                <p className="text-sm text-gray-600">System administration and management</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">Current Organization: {organizationId}</span>
              <div className="h-8 w-px bg-gray-300" />
              <span className="text-sm font-medium text-gray-900">{userRole}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="flex">
        {/* Sidebar */}
        <div className="w-64 bg-white shadow-sm border-r min-h-screen">
          <nav className="mt-6">
            <div className="px-3 space-y-1">
              {tabs.map((tab) => {
                const Icon = tab.icon
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`w-full flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                      activeTab === tab.id
                        ? 'bg-blue-100 text-blue-700'
                        : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                    }`}
                  >
                    <Icon className="h-5 w-5 mr-3" />
                    {tab.label}
                  </button>
                )
              })}
            </div>
          </nav>
        </div>

        {/* Main Content */}
        <div className="flex-1 p-6">
          {renderTabContent()}
        </div>
      </div>
    </div>
  )
}
