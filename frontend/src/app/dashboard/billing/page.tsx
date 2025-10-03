"use client"

import { useState, useEffect } from 'react'
import { useUser } from '@clerk/nextjs'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { useOrganization } from "@/contexts/organization-context"
import { 
  CreditCard, 
  DollarSign, 
  Calendar,
  Shield,
  CheckCircle,
  AlertCircle,
  TrendingUp,
  Users
} from "lucide-react"

export default function BillingPage() {
  const { user } = useUser()
  const { userRole, permissions, isLoading: orgLoading } = useOrganization()
  const [loading, setLoading] = useState(true)

  // Check if user has permission to access this page
  if (!orgLoading && !permissions.includes('view_billing')) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <Shield className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-foreground mb-2">Access Denied</h2>
          <p className="text-muted-foreground">
            You don't have permission to view billing information
          </p>
        </div>
      </div>
    )
  }

  // Mock billing data - in a real app, this would come from your billing provider
  const billingData = {
    plan: 'Pro Plan',
    status: 'active',
    nextBilling: '2024-02-15',
    amount: 99.00,
    currency: 'USD',
    usage: {
      users: 5,
      maxUsers: 10,
      storage: 2.5,
      maxStorage: 10
    },
    features: [
      'Unlimited AI Poster Generation',
      'Advanced Analytics',
      'Team Collaboration',
      'Priority Support',
      'Custom Branding'
    ]
  }

  useEffect(() => {
    // Simulate loading
    const timer = setTimeout(() => setLoading(false), 1000)
    return () => clearTimeout(timer)
  }, [])

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
            <h1 className="text-3xl font-bold text-foreground">Billing & Subscription</h1>
            <p className="text-muted-foreground mt-1">
              Manage your subscription and billing information.
            </p>
          </div>
          <Button className="bg-textile-accent">
            <CreditCard className="mr-2 h-4 w-4" />
            Update Payment Method
          </Button>
        </div>

        {/* Billing Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="textile-hover textile-shadow">
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <DollarSign className="h-5 w-5 text-chart-1" />
                <div>
                  <p className="text-2xl font-bold">${billingData.amount}</p>
                  <p className="text-xs text-muted-foreground">Monthly</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card className="textile-hover textile-shadow">
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <Calendar className="h-5 w-5 text-chart-2" />
                <div>
                  <p className="text-2xl font-bold">
                    {new Date(billingData.nextBilling).toLocaleDateString('en-US', { 
                      month: 'short', 
                      day: 'numeric' 
                    })}
                  </p>
                  <p className="text-xs text-muted-foreground">Next Billing</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card className="textile-hover textile-shadow">
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <Users className="h-5 w-5 text-chart-3" />
                <div>
                  <p className="text-2xl font-bold">
                    {billingData.usage.users}/{billingData.usage.maxUsers}
                  </p>
                  <p className="text-xs text-muted-foreground">Users</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card className="textile-hover textile-shadow">
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <TrendingUp className="h-5 w-5 text-chart-4" />
                <div>
                  <p className="text-2xl font-bold">{billingData.usage.storage}GB</p>
                  <p className="text-xs text-muted-foreground">Storage Used</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Current Plan */}
        <Card className="textile-hover textile-shadow">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center">
                <CreditCard className="mr-2 h-5 w-5" />
                Current Plan
              </CardTitle>
              <Badge 
                variant={billingData.status === 'active' ? 'default' : 'destructive'}
                className="flex items-center space-x-1"
              >
                {billingData.status === 'active' ? (
                  <CheckCircle className="h-3 w-3" />
                ) : (
                  <AlertCircle className="h-3 w-3" />
                )}
                <span className="capitalize">{billingData.status}</span>
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-xl font-semibold text-foreground mb-2">
                  {billingData.plan}
                </h3>
                <p className="text-3xl font-bold text-foreground mb-1">
                  ${billingData.amount}
                  <span className="text-lg text-muted-foreground">/month</span>
                </p>
                <p className="text-sm text-muted-foreground">
                  Billed monthly • Next billing: {new Date(billingData.nextBilling).toLocaleDateString()}
                </p>
              </div>
              
              <div className="space-y-2">
                <h4 className="font-medium text-foreground">Plan Features</h4>
                <ul className="space-y-1">
                  {billingData.features.map((feature, index) => (
                    <li key={index} className="flex items-center text-sm text-muted-foreground">
                      <CheckCircle className="h-4 w-4 text-green-500 mr-2 flex-shrink-0" />
                      {feature}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Usage Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card className="textile-hover textile-shadow">
            <CardHeader>
              <CardTitle>User Usage</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span>Active Users</span>
                    <span>{billingData.usage.users}/{billingData.usage.maxUsers}</span>
                  </div>
                  <div className="w-full bg-muted rounded-full h-2">
                    <div 
                      className="bg-chart-1 h-2 rounded-full" 
                      style={{ width: `${(billingData.usage.users / billingData.usage.maxUsers) * 100}%` }}
                    ></div>
                  </div>
                </div>
                
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span>Storage Used</span>
                    <span>{billingData.usage.storage}GB/{billingData.usage.maxStorage}GB</span>
                  </div>
                  <div className="w-full bg-muted rounded-full h-2">
                    <div 
                      className="bg-chart-2 h-2 rounded-full" 
                      style={{ width: `${(billingData.usage.storage / billingData.usage.maxStorage) * 100}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="textile-hover textile-shadow">
            <CardHeader>
              <CardTitle>Billing Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button variant="outline" className="w-full justify-start">
                <CreditCard className="mr-2 h-4 w-4" />
                Update Payment Method
              </Button>
              <Button variant="outline" className="w-full justify-start">
                <Calendar className="mr-2 h-4 w-4" />
                Download Invoice
              </Button>
              <Button variant="outline" className="w-full justify-start">
                <TrendingUp className="mr-2 h-4 w-4" />
                Upgrade Plan
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Billing History */}
        <Card className="textile-hover textile-shadow">
          <CardHeader>
            <CardTitle>Recent Billing History</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[
                { date: '2024-01-15', amount: 99.00, status: 'paid' },
                { date: '2023-12-15', amount: 99.00, status: 'paid' },
                { date: '2023-11-15', amount: 99.00, status: 'paid' },
              ].map((invoice, index) => (
                <div key={index} className="flex items-center justify-between p-3 border border-border rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-chart-1 rounded-lg flex items-center justify-center">
                      <CreditCard className="h-4 w-4 text-white" />
                    </div>
                    <div>
                      <p className="font-medium text-foreground">
                        {new Date(invoice.date).toLocaleDateString('en-US', { 
                          month: 'long', 
                          year: 'numeric' 
                        })}
                      </p>
                      <p className="text-sm text-muted-foreground">Invoice #{invoice.date}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <Badge variant="default" className="text-xs">
                      {invoice.status}
                    </Badge>
                    <p className="font-semibold text-foreground">${invoice.amount}</p>
                    <Button variant="ghost" size="sm">
                      Download
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
  )
}
