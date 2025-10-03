"use client"

import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { 
  BarChart3, 
  TrendingUp, 
  Users, 
  Activity,
  Download,
  Calendar,
  Eye,
  MousePointer,
  Clock
} from "lucide-react"

export default function AdminAnalytics() {
  const metrics = [
    {
      title: "Total Users",
      value: "1,234",
      change: "+12%",
      icon: Users,
      color: "text-blue-600"
    },
    {
      title: "Active Sessions",
      value: "89",
      change: "+5%",
      icon: Activity,
      color: "text-green-600"
    },
    {
      title: "Page Views",
      value: "45,678",
      change: "+8%",
      icon: Eye,
      color: "text-purple-600"
    },
    {
      title: "Avg. Session Time",
      value: "4m 32s",
      change: "+2%",
      icon: Clock,
      color: "text-orange-600"
    }
  ]

  const topPages = [
    { page: "/dashboard", views: 1234, unique: 890 },
    { page: "/poster-generator", views: 987, unique: 654 },
    { page: "/catalog-builder", views: 765, unique: 543 },
    { page: "/admin", views: 432, unique: 321 },
    { page: "/settings", views: 321, unique: 234 }
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>
          <p className="text-gray-600 mt-2">Comprehensive insights into your organization's usage</p>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="outline" className="flex items-center space-x-2">
            <Calendar className="w-4 h-4" />
            <span>Last 30 days</span>
          </Button>
          <Button variant="outline" className="flex items-center space-x-2">
            <Download className="w-4 h-4" />
            <span>Export</span>
          </Button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {metrics.map((metric, index) => (
          <Card key={index} className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">{metric.title}</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">{metric.value}</p>
                <p className="text-sm text-green-600 mt-1 flex items-center">
                  <TrendingUp className="w-4 h-4 mr-1" />
                  {metric.change}
                </p>
              </div>
              <div className={`p-3 rounded-lg bg-gray-50 ${metric.color}`}>
                <metric.icon className="w-6 h-6" />
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Usage Chart */}
        <Card className="p-6">
          <div className="flex items-center space-x-3 mb-6">
            <BarChart3 className="w-6 h-6 text-blue-600" />
            <h2 className="text-xl font-semibold text-gray-900">Usage Over Time</h2>
          </div>
          
          <div className="h-64 bg-gray-50 rounded-lg flex items-center justify-center">
            <div className="text-center">
              <BarChart3 className="w-12 h-12 text-gray-400 mx-auto mb-2" />
              <p className="text-gray-600">Chart visualization would go here</p>
              <p className="text-sm text-gray-500">Integration with charting library needed</p>
            </div>
          </div>
        </Card>

        {/* User Activity */}
        <Card className="p-6">
          <div className="flex items-center space-x-3 mb-6">
            <Activity className="w-6 h-6 text-blue-600" />
            <h2 className="text-xl font-semibold text-gray-900">User Activity</h2>
          </div>
          
          <div className="h-64 bg-gray-50 rounded-lg flex items-center justify-center">
            <div className="text-center">
              <Activity className="w-12 h-12 text-gray-400 mx-auto mb-2" />
              <p className="text-gray-600">Activity chart would go here</p>
              <p className="text-sm text-gray-500">Real-time user activity tracking</p>
            </div>
          </div>
        </Card>
      </div>

      {/* Top Pages */}
      <Card className="p-6">
        <div className="flex items-center space-x-3 mb-6">
          <MousePointer className="w-6 h-6 text-blue-600" />
          <h2 className="text-xl font-semibold text-gray-900">Top Pages</h2>
        </div>

        <div className="space-y-4">
          {topPages.map((page, index) => (
            <div key={index} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
              <div>
                <p className="font-medium text-gray-900">{page.page}</p>
                <p className="text-sm text-gray-600">{page.unique} unique visitors</p>
              </div>
              <div className="text-right">
                <p className="font-semibold text-gray-900">{page.views.toLocaleString()}</p>
                <p className="text-sm text-gray-600">total views</p>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* System Performance */}
      <Card className="p-6">
        <div className="flex items-center space-x-3 mb-6">
          <TrendingUp className="w-6 h-6 text-blue-600" />
          <h2 className="text-xl font-semibold text-gray-900">System Performance</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="p-4 bg-green-50 rounded-lg">
            <h3 className="font-semibold text-gray-900 mb-2">Uptime</h3>
            <p className="text-2xl font-bold text-green-600">99.9%</p>
            <p className="text-sm text-gray-600">Last 30 days</p>
          </div>

          <div className="p-4 bg-blue-50 rounded-lg">
            <h3 className="font-semibold text-gray-900 mb-2">Response Time</h3>
            <p className="text-2xl font-bold text-blue-600">245ms</p>
            <p className="text-sm text-gray-600">Average</p>
          </div>

          <div className="p-4 bg-purple-50 rounded-lg">
            <h3 className="font-semibold text-gray-900 mb-2">Error Rate</h3>
            <p className="text-2xl font-bold text-purple-600">0.1%</p>
            <p className="text-sm text-gray-600">Last 24 hours</p>
          </div>
        </div>
      </Card>
    </div>
  )
}
