import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { Button } from '../ui/button'
import { Separator } from '../ui/separator'
import { Badge } from '../ui/badge'
import CompanyProfileSettings from './CompanyProfileSettings'

interface SettingsTab {
  id: string
  label: string
  description: string
  component: React.ComponentType
  badge?: string
}

const SettingsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState('company-profile')

  const tabs: SettingsTab[] = [
    {
      id: 'company-profile',
      label: 'Company Profile',
      description: 'Manage your company branding and contact information',
      component: CompanyProfileSettings,
      badge: 'New'
    }
  ]

  const ActiveComponent = tabs.find(tab => tab.id === activeTab)?.component

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-600 mt-2">
          Manage your account settings and company profile
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Settings Navigation */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Settings</CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <nav className="space-y-1">
                {tabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`w-full text-left px-4 py-3 text-sm font-medium rounded-none border-l-4 transition-colors ${
                      activeTab === tab.id
                        ? 'border-blue-500 bg-blue-50 text-blue-700'
                        : 'border-transparent text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span>{tab.label}</span>
                      {tab.badge && (
                        <Badge variant="secondary" className="text-xs">
                          {tab.badge}
                        </Badge>
                      )}
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                      {tab.description}
                    </p>
                  </button>
                ))}
              </nav>
            </CardContent>
          </Card>
        </div>

        {/* Settings Content */}
        <div className="lg:col-span-3">
          {ActiveComponent && <ActiveComponent />}
        </div>
      </div>
    </div>
  )
}

export default SettingsPage





