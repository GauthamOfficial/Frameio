"use client"

import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { 
  CreditCard, 
  Download, 
  Calendar,
  DollarSign,
  TrendingUp,
  AlertCircle,
  CheckCircle
} from "lucide-react"

export default function BillingManagement() {
  const billingHistory = [
    {
      id: 1,
      date: "2024-01-15",
      amount: "$299.00",
      status: "Paid",
      description: "Monthly subscription - Pro Plan"
    },
    {
      id: 2,
      date: "2023-12-15",
      amount: "$299.00",
      status: "Paid",
      description: "Monthly subscription - Pro Plan"
    },
    {
      id: 3,
      date: "2023-11-15",
      amount: "$299.00",
      status: "Paid",
      description: "Monthly subscription - Pro Plan"
    }
  ]

  const getStatusIcon = (status: string) => {
    return status === "Paid" ? (
      <CheckCircle className="w-4 h-4 text-green-600" />
    ) : (
      <AlertCircle className="w-4 h-4 text-red-600" />
    )
  }

  const getStatusColor = (status: string) => {
    return status === "Paid" 
      ? "bg-green-100 text-green-800" 
      : "bg-red-100 text-red-800"
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Billing Management</h1>
        <p className="text-gray-600 mt-2">Manage subscriptions, payments, and billing information</p>
      </div>

      {/* Current Plan */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <CreditCard className="w-6 h-6 text-blue-600" />
            <h2 className="text-xl font-semibold text-gray-900">Current Plan</h2>
          </div>
          <Button variant="outline">Change Plan</Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="p-4 border border-gray-200 rounded-lg">
            <h3 className="font-semibold text-gray-900">Pro Plan</h3>
            <p className="text-2xl font-bold text-gray-900 mt-2">$299<span className="text-sm font-normal text-gray-600">/month</span></p>
            <p className="text-sm text-gray-600 mt-1">Next billing: Feb 15, 2024</p>
          </div>

          <div className="p-4 border border-gray-200 rounded-lg">
            <h3 className="font-semibold text-gray-900">Users</h3>
            <p className="text-2xl font-bold text-gray-900 mt-2">24<span className="text-sm font-normal text-gray-600">/50</span></p>
            <p className="text-sm text-gray-600 mt-1">Active users</p>
          </div>

          <div className="p-4 border border-gray-200 rounded-lg">
            <h3 className="font-semibold text-gray-900">Storage</h3>
            <p className="text-2xl font-bold text-gray-900 mt-2">2.4<span className="text-sm font-normal text-gray-600">/10 GB</span></p>
            <p className="text-sm text-gray-600 mt-1">Used storage</p>
          </div>
        </div>
      </Card>

      {/* Payment Method */}
      <Card className="p-6">
        <div className="flex items-center space-x-3 mb-6">
          <CreditCard className="w-6 h-6 text-blue-600" />
          <h2 className="text-xl font-semibold text-gray-900">Payment Method</h2>
        </div>

        <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-8 bg-blue-600 rounded flex items-center justify-center">
              <span className="text-white text-xs font-bold">VISA</span>
            </div>
            <div>
              <p className="font-medium text-gray-900">•••• •••• •••• 4242</p>
              <p className="text-sm text-gray-600">Expires 12/25</p>
            </div>
          </div>
          <Button variant="outline" size="sm">Update</Button>
        </div>
      </Card>

      {/* Billing History */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <Calendar className="w-6 h-6 text-blue-600" />
            <h2 className="text-xl font-semibold text-gray-900">Billing History</h2>
          </div>
          <Button variant="outline" className="flex items-center space-x-2">
            <Download className="w-4 h-4" />
            <span>Export</span>
          </Button>
        </div>

        <div className="space-y-4">
          {billingHistory.map((item) => (
            <div key={item.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
              <div className="flex items-center space-x-4">
                {getStatusIcon(item.status)}
                <div>
                  <p className="font-medium text-gray-900">{item.description}</p>
                  <p className="text-sm text-gray-600">{item.date}</p>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <span className="font-semibold text-gray-900">{item.amount}</span>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(item.status)}`}>
                  {item.status}
                </span>
                <Button variant="ghost" size="sm">
                  <Download className="w-4 h-4" />
                </Button>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Usage Analytics */}
      <Card className="p-6">
        <div className="flex items-center space-x-3 mb-6">
          <TrendingUp className="w-6 h-6 text-blue-600" />
          <h2 className="text-xl font-semibold text-gray-900">Usage Analytics</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="p-4 bg-gray-50 rounded-lg">
            <h3 className="font-semibold text-gray-900 mb-2">API Calls</h3>
            <p className="text-2xl font-bold text-gray-900">45,678</p>
            <p className="text-sm text-gray-600">This month</p>
          </div>

          <div className="p-4 bg-gray-50 rounded-lg">
            <h3 className="font-semibold text-gray-900 mb-2">Designs Generated</h3>
            <p className="text-2xl font-bold text-gray-900">1,234</p>
            <p className="text-sm text-gray-600">This month</p>
          </div>
        </div>
      </Card>
    </div>
  )
}
