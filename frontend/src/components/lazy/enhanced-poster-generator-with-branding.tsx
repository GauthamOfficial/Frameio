"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { 
  Wand2, 
  Download, 
  RefreshCw,
  AlertCircle,
  CheckCircle,
  Loader2,
  Upload,
  Copy,
  Hash,
  MessageSquare,
  Sparkles,
  Building2,
  Settings
} from "lucide-react"
import React, { useState, useRef } from "react"
import { useUser, useAuth } from '@clerk/nextjs'
import { useRouter } from 'next/navigation'
import { useCompanyProfile } from '@/hooks/use-company-profile'

interface GenerationResult {
  success: boolean
  message?: string
  image_path?: string
  image_url?: string
  filename?: string
  error?: string
  text_added?: string
  style?: string
  caption?: string
  full_caption?: string
  hashtags?: string[]
  emoji?: string
  call_to_action?: string
  branding_applied?: boolean
  logo_added?: boolean
  contact_info_added?: boolean
}

export default function EnhancedPosterGeneratorWithBranding() {
  // Authentication
  const { user } = useUser()
  const { getToken } = useAuth()
  const router = useRouter()
  
  // Error handling
  const [componentError, setComponentError] = useState<string | null>(null)
  
  // Company profile data
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
  
  // State management
  const [isGenerating, setIsGenerating] = useState(false)
  const [prompt, setPrompt] = useState("")
  const [aspectRatio, setAspectRatio] = useState("4:5")
  const [result, setResult] = useState<GenerationResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  
  // Image upload functionality
  const [uploadedImage, setUploadedImage] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  
  // Caption and hashtag functionality
  const [showCaption, setShowCaption] = useState(false)
  const [copiedItem, setCopiedItem] = useState<string | null>(null)

  const generatePoster = async () => {
    if (!prompt.trim()) {
      setError('Please enter a prompt')
      return
    }

    setIsGenerating(true)
    setError(null)
    setResult(null)

    // Prepare abort/timeout handles in outer scope so finally can always clear them
    let timeoutId: ReturnType<typeof setTimeout> | undefined
    try {
      console.log('🚀 Starting poster generation with branding...')
      console.log('Prompt:', prompt)
      console.log('Aspect Ratio:', aspectRatio)
      console.log('Has uploaded image:', !!uploadedImage)
      console.log('User authenticated:', !!user)
      console.log('Has branding data:', hasBrandingData)
      console.log('Branding data:', brandingData)

      // Get authentication token
      const token = await getToken()
      const authHeaders = token ? { 'Authorization': `Bearer ${token}` } : {}
      
      // Add user context for branding (development)
      if (user?.id) {
        authHeaders['X-Dev-User-ID'] = user.id
      }

      let response;

      // Resolve API base robustly and add fallbacks
      const primaryBase = (process.env.NEXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')
      const fallbackBases = [primaryBase, 'http://127.0.0.1:8000', 'http://localhost:8000']
        .map(b => b.replace(/\/$/, ''))
        // de-duplicate while preserving order
        .filter((v, i, a) => a.indexOf(v) === i)

      // Helper to try multiple bases until one succeeds (per-attempt timeout)
      const fetchWithFallback = async (path: string, init: RequestInit) => {
        let lastErr: unknown = null
        for (const base of fallbackBases) {
          try {
            const controller = new AbortController()
            const localTimeout = setTimeout(() => controller.abort(), 180000)
            const res = await fetch(`${base}${path}`, { ...init, signal: controller.signal })
            clearTimeout(localTimeout)
            if (res.ok || res.status) return res
          } catch (e) {
            lastErr = e
          }
        }
        if (lastErr) throw lastErr
        throw new Error('Network request failed')
      }

      if (uploadedImage) {
        // Generate poster with uploaded image
        const formData = new FormData()
        formData.append('image', uploadedImage)
        formData.append('prompt', prompt)
        formData.append('aspect_ratio', aspectRatio)

        response = await fetchWithFallback(`/api/ai/ai-poster/edit_poster/`, {
          method: 'POST',
          // Do NOT set Content-Type with FormData; browser sets correct boundary
          headers: {
            Accept: 'application/json',
            ...authHeaders,
          },
          body: formData,
          mode: 'cors',
        })
      } else {
        // Generate poster from text only
        response = await fetchWithFallback(`/api/ai/ai-poster/generate_poster/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Accept: 'application/json',
            ...authHeaders,
          },
          body: JSON.stringify({
            prompt: prompt,
            aspect_ratio: aspectRatio,
          }),
          mode: 'cors',
        })
      }

      console.log('Response status:', response.status)
      
      if (!response.ok) {
        let message = `HTTP ${response.status}`
        try {
          const errorData = await response.json()
          message = errorData?.error || message
        } catch (e) {
          // fallback: response may not be JSON
          const text = await response.text().catch(() => '')
          if (text) message = text
        }
        throw new Error(message)
      }

      const data = await response.json()
      console.log('Generation result:', data)

      if (data.success) {
        setResult(data)
        setError(null)
        console.log('✅ Poster generated successfully!')
        console.log('Image URL:', data.image_url)
        console.log('Image Path:', data.image_path)
        console.log('Branding applied:', data.branding_applied)
        console.log('Logo added:', data.logo_added)
        console.log('Contact info added:', data.contact_info_added)
      } else {
        throw new Error(data.error || 'Generation failed')
      }
    } catch (err) {
      console.error('❌ Generation failed:', err)
      // Map common network errors to helpful messages
      const networkMsg =
        (err instanceof DOMException && err.name === 'AbortError') || (typeof err === 'string' && err.toLowerCase() === 'timeout')
          ? 'Request timed out. Please try again.'
          : err instanceof TypeError && /Failed to fetch/i.test(String(err.message))
          ? 'Cannot reach the backend. Ensure it is running on 127.0.0.1:8000 and CORS allows this origin.'
          : err instanceof Error
          ? err.message
          : 'Generation failed'
      setError(networkMsg)
      setResult(null)
    } finally {
      if (timeoutId) clearTimeout(timeoutId)
      setIsGenerating(false)
    }
  }

  const downloadImage = async () => {
    if (result?.image_url) {
      try {
        // The backend now provides full URLs, but keep fallback for safety
        const downloadUrl = result.image_url.startsWith('http') 
          ? result.image_url 
          : `http://localhost:8000${result.image_url}`
        
        // Fetch the image as a blob to force download
        const response = await fetch(downloadUrl)
        const blob = await response.blob()
        
        // Create a blob URL and download
        const blobUrl = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = blobUrl
        link.download = result.filename || 'generated-poster.png'
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        
        // Clean up the blob URL
        window.URL.revokeObjectURL(blobUrl)
      } catch (error) {
        console.error('Download failed:', error)
        // Fallback to direct link
        const link = document.createElement('a')
        link.href = result.image_url.startsWith('http') 
          ? result.image_url 
          : `http://localhost:8000${result.image_url}`
        link.download = result.filename || 'generated-poster.png'
        link.target = '_blank'
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
      }
    }
  }

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      setUploadedImage(file)
      const url = URL.createObjectURL(file)
      setPreviewUrl(url)
      setError(null)
    }
  }

  const clearUploadedImage = () => {
    setUploadedImage(null)
    setPreviewUrl(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const copyToClipboard = async (text: string, type: string) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopiedItem(type)
      setTimeout(() => setCopiedItem(null), 2000)
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }

  const goToSettings = () => {
    router.push('/dashboard/settings')
  }

  // Error boundary
  if (componentError) {
    return (
      <div className="container mx-auto p-6 max-w-7xl">
        <div className="text-center py-8">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold mb-2">Component Error</h2>
          <p className="text-gray-600 mb-4">{componentError}</p>
          <Button onClick={() => setComponentError(null)}>
            Try Again
          </Button>
        </div>
      </div>
    )
  }

  try {
    return (
      <div className="container mx-auto p-6 max-w-8xl">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-center mb-2">AI Poster Generator</h1>
        </div>

      <div className="flex justify-center">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full max-w-6xl" style={{ minHeight: '500px' }}>
        {/* Input Section */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <span>Generate Poster</span>
              {isGenerating && <Loader2 className="h-4 w-4 animate-spin" />}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="prompt">Describe your poster</Label>
              <Textarea
                id="prompt"
                placeholder="e.g., Modern silk saree collection with elegant patterns and vibrant colors, perfect for showcasing premium textile designs"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                disabled={isGenerating}
                rows={4}
                className="min-h-[100px] resize-y"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="aspect-ratio">Aspect Ratio</Label>
              <select
                id="aspect-ratio"
                value={aspectRatio}
                onChange={(e) => setAspectRatio(e.target.value)}
                disabled={isGenerating}
                className="w-full p-2 border rounded-md"
              >
                <option value="1:1">Square (1:1)</option>
                <option value="4:5">Portrait (4:5)</option>
                <option value="5:4">Portrait Wide (5:4)</option>
                <option value="3:2">Classic (3:2)</option>
                <option value="2:3">Classic Tall (2:3)</option>
                <option value="16:9">Landscape (16:9)</option>
                <option value="9:16">Vertical (9:16)</option>
              </select>
            </div>

            {/* Image Upload */}
            <div className="space-y-2">
              <Label>Upload Image (Optional)</Label>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center">
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleImageUpload}
                  disabled={isGenerating}
                  className="hidden"
                />
                {previewUrl ? (
                  <div className="space-y-2">
                    <img 
                      src={previewUrl} 
                      alt="Preview" 
                      className="w-full h-32 object-cover rounded"
                    />
                    <Button 
                      variant="outline" 
                      size="sm" 
                      onClick={clearUploadedImage}
                      disabled={isGenerating}
                    >
                      Remove Image
                    </Button>
                  </div>
                ) : (
                  <div>
                    <Upload className="h-8 w-8 mx-auto text-gray-400 mb-2" />
                    <Button 
                      variant="outline" 
                      onClick={() => fileInputRef.current?.click()}
                      disabled={isGenerating}
                    >
                      Choose Image
                    </Button>
                  </div>
                )}
              </div>
            </div>

            <Button 
              onClick={generatePoster} 
              disabled={isGenerating || !prompt.trim()}
              className="w-full"
            >
              {isGenerating ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                  Generating...
                </>
              ) : (
                <>
                  <Wand2 className="h-4 w-4 mr-2" />
                  Generate Poster
                </>
              )}
            </Button>

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                <div className="flex items-center gap-2">
                  <AlertCircle className="h-4 w-4 text-red-600" />
                  <span className="text-red-800 text-sm">{error}</span>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Generated Poster Section */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <span>Generated Poster</span>
              {result && (
                <div className="ml-auto">
                  <Badge variant="secondary">
                    <CheckCircle className="h-3 w-3 mr-1" />
                    Ready
                  </Badge>
                </div>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent>
              {result ? (
              <div className="space-y-4">
                <div className="border rounded-lg overflow-hidden relative w-full" style={{ aspectRatio: aspectRatio.replace(':', ' / ') }}>
                  <img 
                    src={result.image_url.startsWith('http') 
                      ? result.image_url 
                      : `${(process.env.NEXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')}${result.image_url}`} 
                    alt="Generated Poster" 
                    className="absolute inset-0 w-full h-full object-contain"
                  />
                </div>
                
                <div className="space-y-2">
                  <Button 
                    onClick={downloadImage}
                    className="w-full"
                    variant="outline"
                  >
                    <Download className="h-4 w-4 mr-2" />
                    Download Image
                  </Button>
                </div>

                {/* Branding Status */}
                {result.branding_applied && (
                  <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                    <div className="flex items-center gap-2">
                      <CheckCircle className="h-4 w-4 text-green-600" />
                      <span className="text-green-800 text-sm font-medium">Business branding applied</span>
                    </div>
                    <div className="text-green-700 text-xs mt-1">
                      {result.logo_added && "✓ Logo added "}
                      {result.contact_info_added && "✓ Contact info added"}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex items-center justify-center h-64 bg-gray-50 rounded-lg">
                <div className="text-center">
                  <Sparkles className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                  <p className="text-gray-500">Your generated poster will appear here</p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        </div>
      </div>
    </div>
    )
  } catch (error) {
    console.error('Component error:', error)
    setComponentError(error instanceof Error ? error.message : 'Unknown error occurred')
    return null
  }
}
