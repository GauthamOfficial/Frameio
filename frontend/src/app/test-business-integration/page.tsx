"use client"

import { useState, useEffect } from 'react'
import { useAuth } from '@clerk/nextjs'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { 
  Building2, 
  CheckCircle, 
  AlertCircle, 
  Loader2,
  ExternalLink,
  RefreshCw
} from 'lucide-react'
import { useCompanyProfile } from '@/hooks/use-company-profile'

export default function TestBusinessIntegrationPage() {
  const { getToken } = useAuth()
  const [testResults, setTestResults] = useState<any>(null)
  const [isTesting, setIsTesting] = useState(false)

  const {
    profile,
    status,
    loading: profileLoading,
    error: profileError,
    hasBrandingData,
    brandingData,
    contactInfoText,
    refreshProfile
  } = useCompanyProfile()

  const runIntegrationTest = async () => {
    setIsTesting(true)
    setTestResults(null)

    try {
      console.log('🧪 Running business integration test...')
      
      const results = {
        timestamp: new Date().toISOString(),
        profile_loaded: !!profile,
        has_branding_data: hasBrandingData,
        profile_complete: status?.completion_percentage || 0,
        branding_data: brandingData,
        contact_info: contactInfoText,
        api_endpoints: {
          company_profiles: '/api/company-profiles/',
          company_profiles_status: '/api/company-profiles/status/',
          ai_poster_generate: '/api/ai/ai-poster/generate_poster/',
          ai_poster_edit: '/api/ai/ai-poster/edit_poster/'
        },
        test_status: 'completed'
      }

      setTestResults(results)
      console.log('✅ Integration test completed:', results)
    } catch (error) {
      console.error('❌ Integration test failed:', error)
      setTestResults({
        timestamp: new Date().toISOString(),
        test_status: 'failed',
        error: error instanceof Error ? error.message : 'Unknown error'
      })
    } finally {
      setIsTesting(false)
    }
  }

  const goToSettings = () => {
    window.open('/dashboard/settings', '_blank')
  }

  const goToPosterGenerator = () => {
    window.open('/dashboard/poster-generator', '_blank')
  }

  return (
    <div className="container mx-auto p-6 max-w-6xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-center mb-2">Business Integration Test</h1>
        <p className="text-center text-gray-600">Test the integration between settings and poster generator</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Test Controls */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5" />
              Integration Test
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button 
              onClick={runIntegrationTest}
              disabled={isTesting}
              className="w-full"
            >
              {isTesting ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                  Running Test...
                </>
              ) : (
                <>
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Run Integration Test
                </>
              )}
            </Button>

            <div className="space-y-2">
              <Button 
                variant="outline" 
                onClick={goToSettings}
                className="w-full"
              >
                <ExternalLink className="h-4 w-4 mr-2" />
                Go to Settings
              </Button>
              
              <Button 
                variant="outline" 
                onClick={goToPosterGenerator}
                className="w-full"
              >
                <ExternalLink className="h-4 w-4 mr-2" />
                Go to Poster Generator
              </Button>
            </div>
          </CardContent>
        </Card>

      </div>

      {/* Test Results */}
      {testResults && (
        <Card className="mt-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5" />
              Test Results
              <Badge 
                variant={testResults.test_status === 'completed' ? 'default' : 'destructive'}
                className="ml-auto"
              >
                {testResults.test_status}
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <h4 className="font-medium">Profile Status</h4>
                  <div className="space-y-1 text-sm">
                    <div className="flex justify-between">
                      <span>Profile Loaded:</span>
                      <Badge variant={testResults.profile_loaded ? 'default' : 'secondary'}>
                        {testResults.profile_loaded ? 'Yes' : 'No'}
                      </Badge>
                    </div>
                    <div className="flex justify-between">
                      <span>Has Branding:</span>
                      <Badge variant={testResults.has_branding_data ? 'default' : 'secondary'}>
                        {testResults.has_branding_data ? 'Yes' : 'No'}
                      </Badge>
                    </div>
                    <div className="flex justify-between">
                      <span>Completion:</span>
                      <span>{testResults.profile_complete}%</span>
                    </div>
                  </div>
                </div>

                <div className="space-y-2">
                  <h4 className="font-medium">API Endpoints</h4>
                  <div className="space-y-1 text-sm">
                    {Object.entries(testResults.api_endpoints).map(([key, value]) => (
                      <div key={key} className="flex justify-between">
                        <span className="capitalize">{key.replace('_', ' ')}:</span>
                        <code className="text-xs bg-gray-100 px-1 rounded">{value}</code>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {testResults.branding_data && (
                <div className="space-y-2">
                  <h4 className="font-medium">Branding Data</h4>
                  <pre className="text-xs bg-gray-100 p-3 rounded overflow-auto">
                    {JSON.stringify(testResults.branding_data, null, 2)}
                  </pre>
                </div>
              )}

              {testResults.contact_info && (
                <div className="space-y-2">
                  <h4 className="font-medium">Contact Information</h4>
                  <div className="bg-gray-100 p-3 rounded text-sm">
                    <pre className="whitespace-pre-wrap">{testResults.contact_info}</pre>
                  </div>
                </div>
              )}

              {testResults.error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                  <div className="flex items-center gap-2">
                    <AlertCircle className="h-4 w-4 text-red-600" />
                    <span className="text-red-800 text-sm font-medium">Test Error</span>
                  </div>
                  <p className="text-red-700 text-sm mt-1">{testResults.error}</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

