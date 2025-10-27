import React, { useState, useEffect } from 'react'
import { useUser, useAuth } from '@clerk/nextjs'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { Button } from '../ui/button'
import { Input } from '../ui/input'
import { Label } from '../ui/label'
import { Textarea } from '../ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select'
import { Badge } from '../ui/badge'
import { Separator } from '../ui/separator'
import { Upload, Image as ImageIcon, Save, Palette } from 'lucide-react'
import { useToastHelpers } from '@/components/common'
import { API_ENDPOINTS, API_BASE_URL } from '@/lib/config'

interface CompanyProfile {
  id?: string
  company_name?: string
  logo?: string
  logo_url?: string
  whatsapp_number?: string
  email?: string
  facebook_username?: string
  website?: string
  address?: string
  description?: string
  brand_colors?: string[]
  preferred_logo_position?: string
  has_complete_profile?: boolean
  contact_info?: {
    whatsapp?: string
    email?: string
  }
  created_at?: string
  updated_at?: string
}

interface ProfileStatus {
  has_profile: boolean
  has_logo: boolean
  has_contact_info: boolean
  is_complete: boolean
  completion_percentage: number
}

const CompanyProfileSettings: React.FC = () => {
  const { user } = useUser()
  const { getToken } = useAuth()
  const { showSuccess, showError } = useToastHelpers()
  const router = useRouter()
  const [profile, setProfile] = useState<CompanyProfile | null>(null)
  const [status, setStatus] = useState<ProfileStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [logoFile, setLogoFile] = useState<File | null>(null)
  const [logoPreview, setLogoPreview] = useState<string | null>(null)

  // Form state
  const [formData, setFormData] = useState({
    company_name: '',
    whatsapp_number: '',
    email: '',
    facebook_username: '',
    website: '',
    address: '',
    description: '',
    preferred_logo_position: 'top_right'
  })

  useEffect(() => {
    console.log('🔍 useEffect triggered')
    console.log('User:', user ? 'Present' : 'Missing')
    console.log('getToken:', getToken ? 'Present' : 'Missing')
    
    // Check if Clerk is properly configured
    const clerkConfigured = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY && 
                           process.env.NEXT_PUBLIC_CLERK_FRONTEND_API
    console.log('Clerk configured:', clerkConfigured)
    
    if (user && getToken) {
      console.log('✅ Loading profile...')
      loadProfile()
    } else if (!clerkConfigured) {
      console.log('⚠️ Clerk not configured, using development mode')
      // In development mode without Clerk, still try to load profile
      loadProfile()
    } else {
      console.log('❌ Missing user or getToken')
      setLoading(false)
    }
  }, [user, getToken])

  const loadProfile = async () => {
    // Allow loading profile even without user in development mode
    if (!user && process.env.NODE_ENV === 'production') {
      console.log('❌ No user available in production mode')
      setLoading(false)
      return
    }
    
    try {
      setLoading(true)
      const token = await getToken()
      
      // Debug logging
      console.log('🔍 Loading profile...')
      console.log('API Endpoint:', API_ENDPOINTS.COMPANY_PROFILES)
      console.log('Token:', token ? 'Present' : 'Missing')
      console.log('User:', user?.emailAddresses?.[0]?.emailAddress)
      
      // Fallback to development token if Clerk token is not available
      const authToken = token || 'test_clerk_token'
      console.log('Using token:', authToken ? 'Present' : 'Missing')
      
      // Test backend connectivity first
      try {
        console.log('🔍 Testing backend connectivity...')
        const healthResponse = await fetch(`${API_BASE_URL}/health/`, { 
          method: 'GET',
          headers: {
            'Content-Type': 'application/json'
          }
        })
        console.log('Health check status:', healthResponse.status)
      } catch (healthError) {
        console.warn('⚠️ Health check failed:', healthError.message)
      }
      
      const response = await fetch(API_ENDPOINTS.COMPANY_PROFILES, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        },
        // Add timeout to prevent hanging requests
        signal: AbortSignal.timeout(10000) // 10 second timeout
      })
      
      console.log('Response status:', response.status)
      console.log('Response headers:', Object.fromEntries(response.headers.entries()))

      if (response.ok) {
        const data = await response.json()
        
        // Check if response is empty
        if (!data || Object.keys(data).length === 0) {
          console.warn('⚠️ Empty response received from server (status OK)')
          // Don't show error, just proceed with empty form
        } else {
          console.log('✅ Profile loaded successfully:', data)
          setProfile(data)
          setFormData({
            company_name: data.company_name || '',
            whatsapp_number: data.whatsapp_number || '',
            email: data.email || '',
            facebook_username: data.facebook_username || '',
            website: data.website || '',
            address: data.address || '',
            description: data.description || '',
            preferred_logo_position: data.preferred_logo_position || 'top_right'
          })
          if (data.logo_url) {
            setLogoPreview(data.logo_url)
          }
          // Load status after successful profile load
          loadStatus()
        }
      } else {
        // Handle different error responses
        let errorMessage = 'Failed to load profile information'
        try {
          const errorData = await response.json()
          
          // Check if response is empty or contains no useful error information
          if (!errorData || Object.keys(errorData).length === 0) {
            console.warn('⚠️ Empty response received from server')
            errorMessage = response.statusText || `HTTP ${response.status}`
          } else {
            // Only log debug info if we have valid error data
            if (errorData && typeof errorData === 'object') {
              // Check if the object has meaningful content
              const hasContent = Object.keys(errorData).length > 0 && 
                                Object.values(errorData).some(value => 
                                  value !== null && 
                                  value !== undefined && 
                                  value !== '' && 
                                  value !== '{}' &&
                                  (typeof value !== 'object' || Object.keys(value).length > 0)
                                )
              
              // Additional check: if it's just an empty object or has no meaningful error fields
              const hasErrorFields = errorData.error || errorData.message || errorData.detail || errorData.errors
              
              if (hasContent && hasErrorFields) {
                console.error('❌ Load error response:', errorData)
                errorMessage = errorData.error || errorData.message || errorData.detail || errorMessage
              } else {
                console.warn('⚠️ Load error response: Empty or meaningless error object')
                console.warn('  Object keys:', Object.keys(errorData))
                console.warn('  Object values:', Object.values(errorData))
                console.warn('  Has content:', hasContent)
                console.warn('  Has error fields:', hasErrorFields)
                errorMessage = response.statusText || `HTTP ${response.status}`
              }
            } else {
              console.warn('⚠️ Load error response: Invalid error data type')
              console.warn('  Error data:', errorData)
              errorMessage = response.statusText || `HTTP ${response.status}`
            }
          }
        } catch (parseError) {
          errorMessage = response.statusText || `HTTP ${response.status}`
          console.error('❌ Load error (non-JSON):', errorMessage)
        }
        
        if (response.status === 401) {
          showError('Please log in again to access your profile')
        } else if (response.status === 404) {
          console.log('ℹ️ No profile found, will create new one')
          // Don't show error for 404, just proceed with empty form
        } else {
          showError(errorMessage)
        }
      }
    } catch (error) {
      console.error('❌ Error loading profile:', error)
      console.error('Error type:', error.constructor.name)
      console.error('Error message:', error.message)
      console.error('Error stack:', error.stack)
      
      // Check if it's a network error
      if (error.name === 'AbortError') {
        console.error('⏰ Request timeout')
        showError('Request timed out. Please check your connection and try again.')
      } else if (error.message === 'Failed to fetch') {
        console.error('🌐 Network error - Backend server may not be running')
        showError('Cannot connect to server. Please ensure the backend is running on http://localhost:8000')
      } else if (error.message.includes('CORS')) {
        console.error('🚫 CORS error')
        showError('CORS error. Please check backend CORS configuration.')
      } else {
        showError('Failed to load company profile: ' + error.message)
      }
    } finally {
      setLoading(false)
    }
  }

  const loadStatus = async () => {
    if (!user) return
    
    try {
      const token = await getToken()
      const authToken = token || 'test_clerk_token'
      
      console.log('🔍 Loading profile status...')
      console.log('Status endpoint:', API_ENDPOINTS.COMPANY_PROFILES_STATUS)
      
      const response = await fetch(API_ENDPOINTS.COMPANY_PROFILES_STATUS, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        },
        // Add timeout to prevent hanging requests
        signal: AbortSignal.timeout(5000) // 5 second timeout
      })

      console.log('Status response:', response.status)

      if (response.ok) {
        const data = await response.json()
        console.log('✅ Status loaded successfully:', data)
        setStatus(data)
      } else {
        // Handle authentication errors silently for status
        console.warn('Failed to load profile status:', response.status, response.statusText)
        // Don't show error to user for status, just log it
      }
    } catch (error) {
      console.error('Error loading status:', error)
      // Don't show error to user for status, just log it
    }
  }

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const formatUrl = (url: string): string => {
    if (!url) return url
    
    // If URL doesn't start with http:// or https://, add https://
    if (!url.match(/^https?:\/\//)) {
      return `https://${url}`
    }
    return url
  }

  const validateUrl = (url: string): boolean => {
    if (!url) return true // Empty URL is valid (optional field)
    
    try {
      const urlObj = new URL(url)
      return urlObj.protocol === 'http:' || urlObj.protocol === 'https:'
    } catch {
      return false
    }
  }

  const handleLogoChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      setLogoFile(file)
      const reader = new FileReader()
      reader.onload = (e) => {
        setLogoPreview(e.target?.result as string)
      }
      reader.readAsDataURL(file)
    }
  }

  const handleSave = async () => {
    // Allow saving even without user in development mode
    if (!user && process.env.NODE_ENV === 'production') {
      console.log('❌ No user available in production mode')
      return
    }
    
    try {
      setSaving(true)
      
      const token = await getToken()
      const authToken = token || 'test_clerk_token'
      
      console.log('💾 Saving profile...')
      console.log('Using token:', authToken ? 'Present' : 'Missing')
      console.log('API Endpoint:', API_ENDPOINTS.COMPANY_PROFILES)
      
      // Test connectivity first
      try {
        console.log('🔍 Testing connectivity...')
        const testResponse = await fetch(`${API_BASE_URL}/health/`, { 
          method: 'GET',
          headers: {
            'Content-Type': 'application/json'
          }
        })
        console.log('✅ Backend connectivity test:', testResponse.status)
      } catch (testError) {
        console.error('❌ Backend connectivity test failed:', testError)
        showError('Cannot connect to backend server. Please ensure it\'s running on http://localhost:8000')
        return
      }
      
      let response
      
      // Format URLs before sending
      const formattedData = {
        ...formData,
        website: formData.website ? formatUrl(formData.website) : formData.website
      }

      // Validate URLs before sending
      if (formattedData.website && !validateUrl(formattedData.website)) {
        showError('Please enter a valid website URL (e.g., https://example.com)')
        return
      }

      // If there's a logo file, use FormData (multipart)
      if (logoFile) {
        const formDataToSend = new FormData()
        
        // Add text fields
        Object.entries(formattedData).forEach(([key, value]) => {
          if (value) {
            formDataToSend.append(key, value)
          }
        })
        
        // Add logo file
        formDataToSend.append('logo', logoFile)
        
        console.log('📁 Using FormData for file upload')
        console.log('Form data keys:', Array.from(formDataToSend.keys()))
        
        response = await fetch(API_ENDPOINTS.COMPANY_PROFILES, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${authToken}`
          },
          body: formDataToSend,
          // Add timeout to prevent hanging requests
          signal: AbortSignal.timeout(15000) // 15 second timeout for file uploads
        })
      } else {
        // No file upload, use JSON
        const jsonData = {
          ...formattedData
        }
        
        console.log('📄 Using JSON for data-only request')
        console.log('JSON data:', jsonData)
        
        response = await fetch(API_ENDPOINTS.COMPANY_PROFILES, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${authToken}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(jsonData),
          // Add timeout to prevent hanging requests
          signal: AbortSignal.timeout(10000) // 10 second timeout for JSON requests
        })
      }

      console.log('Save response status:', response.status)
      console.log('Save response headers:', Object.fromEntries(response.headers.entries()))

      if (response.ok) {
        const updatedProfile = await response.json()
        
        // Check if response is empty
        if (!updatedProfile || Object.keys(updatedProfile).length === 0) {
          console.warn('⚠️ Empty response received from server during save (status OK)')
          showSuccess('Company profile updated successfully!')
          // Reload profile to get updated data
          loadProfile()
        } else {
          console.log('✅ Profile saved successfully:', updatedProfile)
          setProfile(updatedProfile)
          showSuccess('Company profile updated successfully!')
          loadStatus()
        }
      } else {
        // Handle different response types
        let errorMessage = 'Failed to update profile'
        try {
          const errorData = await response.json()
          
          // Check if response is empty or contains no useful error information
          if (!errorData || Object.keys(errorData).length === 0) {
            console.warn('⚠️ Empty response received from server during save')
            errorMessage = response.statusText || `HTTP ${response.status}`
          } else {
            // Only log debug info if we have valid error data
            if (errorData && typeof errorData === 'object') {
              // Check if the object has meaningful content
              const hasContent = Object.keys(errorData).length > 0 && 
                                Object.values(errorData).some(value => 
                                  value !== null && 
                                  value !== undefined && 
                                  value !== '' && 
                                  value !== '{}' &&
                                  (typeof value !== 'object' || Object.keys(value).length > 0)
                                )
              
              // Additional check: if it's just an empty object or has no meaningful error fields
              const hasErrorFields = errorData.error || errorData.message || errorData.detail || errorData.errors
              
              if (hasContent && hasErrorFields) {
                console.log('Raw error response:', errorData)
                console.log('Error data type:', typeof errorData)
                console.log('Error data keys:', Object.keys(errorData))
                console.log('Error data values:', Object.values(errorData))
                
                errorMessage = errorData.error || errorData.message || errorData.detail || errorMessage
                
                console.error('❌ Save error response:')
                console.error('  Status:', response.status)
                console.error('  Error object:', JSON.stringify(errorData, null, 2))
                console.error('  Error message:', errorMessage)
              } else {
                console.warn('⚠️ Save error response: Empty or meaningless error object')
                console.warn('  Status:', response.status)
                console.warn('  Object keys:', Object.keys(errorData))
                console.warn('  Object values:', Object.values(errorData))
                console.warn('  Has content:', hasContent)
                console.warn('  Has error fields:', hasErrorFields)
                errorMessage = response.statusText || `HTTP ${response.status}`
              }
            } else {
              console.warn('⚠️ Save error response: Invalid error data type')
              console.warn('  Status:', response.status)
              console.warn('  Error data:', errorData)
              errorMessage = response.statusText || `HTTP ${response.status}`
            }
          }
        } catch (parseError) {
          // If response is not JSON (like "Unauthorized"), use status text
          errorMessage = response.statusText || `HTTP ${response.status}`
          console.error('❌ Save error (non-JSON):', errorMessage)
          console.error('Parse error:', parseError)
        }
        
        if (response.status === 401) {
          showError('Please log in again to save your profile')
        } else if (response.status === 413) {
          showError('File too large. Please choose a smaller logo image.')
        } else if (response.status === 400) {
          // For 400 errors, show more specific error message
          if (errorMessage.includes('company_name') || errorMessage.includes('name')) {
            showError('Please enter a valid company name.')
          } else if (errorMessage.includes('website') && errorMessage.includes('URL')) {
            showError('Please enter a valid website URL (e.g., https://example.com)')
          } else if (errorMessage.includes('facebook') && errorMessage.includes('URL')) {
            showError('Please enter a valid Facebook URL (e.g., https://facebook.com/yourpage)')
          } else if (errorMessage.includes('logo') || errorMessage.includes('image')) {
            showError('Please select a valid logo image.')
          } else {
            showError(`Invalid data: ${errorMessage}`)
          }
        } else {
          showError(errorMessage)
        }
      }
    } catch (error) {
      console.error('❌ Error saving profile:', error)
      console.error('Error type:', error.constructor.name)
      console.error('Error message:', error.message)
      console.error('Error stack:', error.stack)
      
      // Check if it's a network error
      if (error.name === 'AbortError') {
        console.error('⏰ Request timeout')
        showError('Request timed out. Please check your connection and try again.')
      } else if (error.message === 'Failed to fetch') {
        console.error('🌐 Network error - Backend server may not be running or CORS issue')
        showError('Cannot connect to server. Please ensure the backend is running on http://localhost:8000')
      } else if (typeof error.message === 'string' && error.message.includes('CORS')) {
        console.error('🚫 CORS error')
        showError('CORS error. Please check backend CORS configuration.')
      } else {
        showError('Failed to save company profile: ' + error.message)
      }
    } finally {
      setSaving(false)
    }
  }

  const getCompletionColor = (percentage: number) => {
    if (percentage >= 80) return 'bg-green-500'
    if (percentage >= 60) return 'bg-yellow-500'
    return 'bg-red-500'
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Profile Status */}
      {status && (
        <Card>
          <CardHeader>
            <CardTitle>Profile Completion</CardTitle>
            <CardDescription>
              Complete your company profile to enable brand personalization in AI-generated posters
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Completion</span>
                <span className="text-sm text-gray-600">{status.completion_percentage}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className={`h-2 rounded-full ${getCompletionColor(status.completion_percentage)}`}
                  style={{ width: `${status.completion_percentage}%` }}
                ></div>
              </div>
              <div className="flex flex-wrap gap-2">
                <Badge variant={status.has_profile ? "default" : "secondary"}>
                  {status.has_profile ? "✓" : "✗"} Company Name
                </Badge>
                <Badge variant={status.has_logo ? "default" : "secondary"}>
                  {status.has_logo ? "✓" : "✗"} Logo
                </Badge>
                <Badge variant={status.has_contact_info ? "default" : "secondary"}>
                  {status.has_contact_info ? "✓" : "✗"} Contact Info
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Three Column Layout */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Personal Information */}
        <Card>
          <CardHeader>
            <CardTitle>Personal Information</CardTitle>
            <CardDescription>
              Your personal details and contact information
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="company_name">Business Name *</Label>
              <Input
                id="company_name"
                value={formData.company_name}
                onChange={(e) => handleInputChange('company_name', e.target.value)}
                placeholder="Enter your business name"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="website">Website</Label>
              <Input
                id="website"
                type="url"
                value={formData.website}
                onChange={(e) => handleInputChange('website', e.target.value)}
                placeholder="https://yourcompany.com"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="description">Business Description</Label>
              <Textarea
                id="description"
                value={formData.description}
                onChange={(e) => handleInputChange('description', e.target.value)}
                placeholder="Describe your business..."
                rows={3}
              />
            </div>
          </CardContent>
        </Card>

        {/* Business Logo */}
        <Card>
          <CardHeader>
            <CardTitle>Business Logo</CardTitle>
            <CardDescription>
              Upload your business logo to be included in AI-generated posters
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="logo">Logo Image</Label>
              <div className="flex gap-2 mb-2">
                <div className="relative flex-1">
                  <Input
                    id="logo"
                    type="file"
                    accept="image/*"
                    onChange={handleLogoChange}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                  />
                  <div className="flex items-center justify-center w-full h-24 border-2 border-dashed border-gray-300 rounded-lg bg-gray-50 hover:bg-gray-100 transition-colors cursor-pointer">
                    <div className="flex flex-col items-center space-y-1">
                      <div className="p-2 bg-blue-100 rounded-full">
                        <Upload className="h-4 w-4 text-blue-600" />
                      </div>
                      <div className="text-center">
                        <p className="text-xs font-medium text-gray-700">Choose Logo</p>
                      </div>
                    </div>
                  </div>
                </div>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => router.push('/dashboard/branding-kit')}
                  className="h-24 px-4 flex flex-col items-center justify-center space-y-1"
                >
                  <Palette className="h-4 w-4 text-purple-600" />
                  <span className="text-xs font-medium">Create Logo</span>
                </Button>
              </div>
              <p className="text-xs text-gray-600">
                Recommended: 300x300px, PNG, JPG, or SVG. Or create a new logo with AI.
              </p>
            </div>
            
            {logoPreview ? (
              <div className="space-y-2">
                <Label>Preview</Label>
                <div className="border rounded-lg p-2 bg-gray-50 flex justify-center">
                  <img 
                    src={logoPreview} 
                    alt="Logo preview" 
                    className="max-w-20 max-h-20 object-contain"
                  />
                </div>
              </div>
            ) : (
              <div className="space-y-2">
                <Label>Preview</Label>
                <div className="border rounded-lg p-2 bg-gray-50 flex items-center justify-center h-20">
                  <div className="flex flex-col items-center space-y-1 text-gray-400">
                    <ImageIcon className="h-6 w-6" />
                    <p className="text-xs">No logo selected</p>
                  </div>
                </div>
              </div>
            )}
            
            <div className="space-y-2">
              <Label htmlFor="logo_position">Logo Position in Posters</Label>
              <Select 
                value={formData.preferred_logo_position}
                onValueChange={(value) => handleInputChange('preferred_logo_position', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select logo position" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="top_right">Top Right</SelectItem>
                  <SelectItem value="top_left">Top Left</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Contact Information */}
        <Card>
          <CardHeader>
            <CardTitle>Contact Information</CardTitle>
            <CardDescription>
              Add your contact details to be included in AI-generated posters
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="whatsapp_number">WhatsApp Number</Label>
              <Input
                id="whatsapp_number"
                value={formData.whatsapp_number}
                onChange={(e) => handleInputChange('whatsapp_number', e.target.value)}
                placeholder="+1234567890"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="facebook_username">Facebook Username</Label>
              <Input
                id="facebook_username"
                value={formData.facebook_username}
                onChange={(e) => handleInputChange('facebook_username', e.target.value)}
                placeholder="yourcompany"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">Email Address</Label>
              <Input
                id="email"
                type="email"
                value={formData.email}
                onChange={(e) => handleInputChange('email', e.target.value)}
                placeholder="contact@yourcompany.com"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="address">Address</Label>
              <Textarea
                id="address"
                value={formData.address}
                onChange={(e) => handleInputChange('address', e.target.value)}
                placeholder="Your business address..."
                rows={2}
              />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Save Button */}
      <div className="flex justify-start">
        <Button 
          onClick={handleSave} 
          disabled={saving}
          className="w-full sm:w-auto"
        >
          <Save className="h-4 w-4 mr-2" />
          {saving ? 'Saving...' : 'Save Profile'}
        </Button>
      </div>
    </div>
  )
}

export default CompanyProfileSettings
