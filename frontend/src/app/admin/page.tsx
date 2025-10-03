"use client"

import { Card } from "@/components/ui/card"
import { 
  Users, 
  Building2, 
  CreditCard, 
  BarChart3,
  TrendingUp,
  DollarSign,
  UserPlus,
  Activity
} from "lucide-react"

export default function AdminOverview() {
  const stats = [
    {
      title: "Total Users",
      value: "1,234",
      change: "+12%",
      icon: Users,
      color: "text-blue-600"
    },
    {
      title: "Active Organizations",
      value: "89",
      change: "+5%",
      icon: Building2,
      color: "text-green-600"
    },
    {
      title: "Monthly Revenue",
      value: "$45,678",
      change: "+8%",
      icon: DollarSign,
      color: "text-purple-600"
    },
    {
      title: "System Health",
      value: "99.9%",
      change: "+0.1%",
      icon: Activity,
      color: "text-green-600"
    }
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Admin Overview</h1>
        <p className="text-gray-600 mt-2">Manage your organization and monitor system performance</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <Card key={index} className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">{stat.title}</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">{stat.value}</p>
                <p className="text-sm text-green-600 mt-1 flex items-center">
                  <TrendingUp className="w-4 h-4 mr-1" />
                  {stat.change}
                </p>
              </div>
              <div className={`p-3 rounded-lg bg-gray-50 ${stat.color}`}>
                <stat.icon className="w-6 h-6" />
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Quick Actions */}
      <Card className="p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
            <UserPlus className="w-5 h-5 text-blue-600 mr-3" />
            <div className="text-left">
              <p className="font-medium text-gray-900">Add New User</p>
              <p className="text-sm text-gray-600">Invite team members</p>
            </div>
          </button>
          
          <button className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
            <Building2 className="w-5 h-5 text-green-600 mr-3" />
            <div className="text-left">
              <p className="font-medium text-gray-900">Organization Settings</p>
              <p className="text-sm text-gray-600">Manage organization</p>
            </div>
          </button>
          
          <button className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
            <BarChart3 className="w-5 h-5 text-purple-600 mr-3" />
            <div className="text-left">
              <p className="font-medium text-gray-900">View Analytics</p>
              <p className="text-sm text-gray-600">System insights</p>
            </div>
          </button>
        </div>
      </Card>

      {/* Recent Activity */}
      <Card className="p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Activity</h2>
        <div className="space-y-4">
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center">
              <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
              <span className="text-sm text-gray-900">New user registered: john.doe@company.com</span>
            </div>
            <span className="text-xs text-gray-500">2 minutes ago</span>
          </div>
          
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center">
              <div className="w-2 h-2 bg-blue-500 rounded-full mr-3"></div>
              <span className="text-sm text-gray-900">Organization settings updated</span>
            </div>
            <span className="text-xs text-gray-500">1 hour ago</span>
          </div>
          
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center">
              <div className="w-2 h-2 bg-yellow-500 rounded-full mr-3"></div>
              <span className="text-sm text-gray-900">Billing information updated</span>
            </div>
            <span className="text-xs text-gray-500">3 hours ago</span>
          </div>
        </div>
      </Card>
    </div>
  )
}