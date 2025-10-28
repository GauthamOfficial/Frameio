"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { FacebookSharingModal } from "@/components/FacebookSharingModal"
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
  Settings,
  Share2,
  ExternalLink,
  Facebook,
  Twitter,
  Instagram,
  Mail
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
  
  // Facebook sharing modal
  const [showFacebookModal, setShowFacebookModal] = useState(false)
  const [facebookContent, setFacebookContent] = useState('')
  const [facebookImageUrl, setFacebookImageUrl] = useState('')

  // Copy and share functions
  const copyToClipboard = async (text: string, type: string) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopiedItem(type)
      setTimeout(() => setCopiedItem(null), 2000)
    } catch (err) {
      console.error('Failed to copy text: ', err)
    }
  }

  const copyHashtags = async () => {
    if (result?.hashtags) {
      const hashtagText = result.hashtags.join(' ')
      await copyToClipboard(hashtagText, 'hashtags')
    }
  }

  const copyFullCaption = async () => {
    if (result?.full_caption) {
      await copyToClipboard(result.full_caption, 'caption')
    }
  }

  const shareToSocialMedia = async (platform: string) => {
    if (!result?.image_url || !result?.full_caption) return

    // Generate a unique poster ID (in a real app, this would come from the backend)
    const posterId = `poster_${Date.now()}`
    
    // Import ngrok utility dynamically to avoid SSR issues
    const { getPosterShareUrl, isAnyTunnelRunning } = await import('@/utils/ngrok')
    
    const shareText = result.full_caption
    let shareLink = ''
    
    switch (platform) {
      case 'facebook':
        try {
          // Check if any tunnel is running for Facebook sharing
          const tunnelRunning = await isAnyTunnelRunning()
          
          if (tunnelRunning) {
            // Use ngrok URL for Facebook sharing
            const posterPageUrl = await getPosterShareUrl(posterId)
            shareLink = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(posterPageUrl)}&quote=${encodeURIComponent(shareText)}`
          } else {
            // Fallback: Show modal for better user experience
            const imageUrl = result.image_url.startsWith('http') 
              ? result.image_url 
              : `http://localhost:8000${result.image_url}`
            
            // Create a better formatted Facebook post
            const facebookText = `${shareText}\n\n🖼️ View the full poster: ${imageUrl}\n\n#AIPoster #Design #Innovation`
            
            // Set modal content and show modal
            setFacebookContent(facebookText)
            setFacebookImageUrl(imageUrl)
            setShowFacebookModal(true)
            return
          }
          
          // Open Facebook share dialog in a popup window
          window.open(
            shareLink,
            'facebook-share-dialog',
            'width=800,height=600,scrollbars=yes,resizable=yes'
          )
          return
        } catch (error) {
          console.error('Facebook sharing error:', error)
          // Fallback to modal
          const imageUrl = result.image_url.startsWith('http') 
            ? result.image_url 
            : `http://localhost:8000${result.image_url}`
          
          // Create a better formatted Facebook post
          const facebookText = `${shareText}\n\n🖼️ View the full poster: ${imageUrl}\n\n#AIPoster #Design #Innovation`
          
          // Set modal content and show modal
          setFacebookContent(facebookText)
          setFacebookImageUrl(imageUrl)
          setShowFacebookModal(true)
          return
        }
      case 'twitter':
        const posterPageUrl = await getPosterShareUrl(posterId)
        shareLink = `https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}&url=${encodeURIComponent(posterPageUrl)}`
        break
      case 'instagram':
        // Instagram doesn't support direct sharing, copy to clipboard
        const instagramUrl = await getPosterShareUrl(posterId)
        copyToClipboard(`${shareText}\n\n${instagramUrl}`, 'instagram')
        return
      case 'whatsapp':
        const whatsappUrl = await getPosterShareUrl(posterId)
        shareLink = `https://wa.me/?text=${encodeURIComponent(shareText + ' ' + whatsappUrl)}`
        break
      case 'email':
        const emailUrl = await getPosterShareUrl(posterId)
        shareLink = `mailto:?subject=Check out this poster&body=${encodeURIComponent(shareText + '\n\n' + emailUrl)}`
        break
    }
    
    if (shareLink) {
      window.open(shareLink, '_blank')
    }
  }

  const shareToClipboard = async () => {
    if (!result?.image_url || !result?.full_caption) return

    // Generate a unique poster ID (in a real app, this would come from the backend)
    const posterId = `poster_${Date.now()}`
    
    // Import ngrok utility dynamically to avoid SSR issues
    const { getPosterShareUrl } = await import('@/utils/ngrok')
    
    const posterPageUrl = await getPosterShareUrl(posterId)
    const shareText = `${result.full_caption}\n\n${posterPageUrl}`
    await copyToClipboard(shareText, 'share')
  }

  // Parse JSON caption if it's in JSON format
  const parseCaption = (caption: string) => {
    try {
      // Check if the caption starts with JSON-like structure
      if (caption.trim().startsWith('{') && caption.trim().endsWith('}')) {
        const parsed = JSON.parse(caption)
        return {
          main_text: parsed.main_text || parsed.caption || caption,
          full_caption: parsed.full_caption || parsed.main_text || caption,
          hashtags: parsed.hashtags || [],
          call_to_action: parsed.call_to_action || '',
          emoji: parsed.emoji || ''
        }
      }
      return {
        main_text: caption,
        full_caption: caption,
        hashtags: [],
        call_to_action: '',
        emoji: ''
      }
    } catch (e) {
      // If parsing fails, return the original caption
      return {
        main_text: caption,
        full_caption: caption,
        hashtags: [],
        call_to_action: '',
        emoji: ''
      }
    }
  }

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
      
      // Multitenancy: pass organization context if available
      try {
        // Prefer a user-selected slug in localStorage, else env var
        const orgSlug = (typeof window !== 'undefined' ? window.localStorage.getItem('organizationSlug') : null)
          || process.env.NEXT_PUBLIC_ORGANIZATION_SLUG
        if (orgSlug) {
          authHeaders['X-Organization'] = orgSlug
        }
        // Dev convenience: support org id header
        const devOrgId = (typeof window !== 'undefined' ? window.localStorage.getItem('devOrgId') : null)
          || process.env.NEXT_PUBLIC_DEV_ORG_ID
        if (devOrgId) {
          authHeaders['X-Dev-Org-Id'] = devOrgId
        }
      } catch {}
      
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

      // Helper to try same-origin first (so Next.js rewrites apply), then fall back
      const fetchWithFallback = async (path: string, init: RequestInit) => {
        let lastErr: unknown = null

        // 1) Try same-origin relative path (leverages Next.js rewrites)
        try {
          const controller = new AbortController()
          const localTimeout = setTimeout(() => controller.abort(), 180000)
          const res = await fetch(path, { ...init, signal: controller.signal })
          clearTimeout(localTimeout)
          if (res.ok) return res
        } catch (e) {
          lastErr = e
        }

        // 2) Try absolute bases as fallbacks
        for (const base of fallbackBases) {
          try {
            const controller = new AbortController()
            const localTimeout = setTimeout(() => controller.abort(), 180000)
            const res = await fetch(`${base}${path}`, { ...init, signal: controller.signal })
            clearTimeout(localTimeout)
            if (res.ok) return res
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
                placeholder="Describe your Post"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                disabled={isGenerating}
                rows={4}
                className="min-h-[100px] resize-y placeholder:opacity-50"
              />
            </div>

            {/* Template Section */}
            <div className="space-y-2">
              <Label>Templates</Label>
              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={() => setPrompt("Create a stylish product post featuring a dummy model wearing the uploaded white party frock. Set the background in a moody, misty outdoor atmosphere with soft cinematic lighting. Add the text 'AVAILABLE NOW' and 'Contact Us' in a nice cinematic font, positioned around two-thirds from the top edge of the image. Do not include any other text or contact details.")}
                  className="flex-1 p-3 text-center border border-gray-200 rounded-md hover:border-gray-300 hover:bg-gray-50 transition-colors text-sm"
                  disabled={isGenerating}
                >
                  <div className="w-full aspect-[4/5] rounded-md mb-2 overflow-hidden">
                    <img 
                      src="/Wedding Frock.jpg" 
                      alt="Wedding Frock" 
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <div className="font-medium text-gray-700">Wedding Frock</div>
                  <div className="text-gray-500 text-xs mt-1">Moody outdoor style</div>
                </button>
                
                <button
                  type="button"
                  onClick={() => setPrompt("Create a stylish product post featuring a real man wearing the uploaded shirt. Set the background with cinematic buildings and dramatic lighting for a modern, urban look. Add the text 'AVAILABLE NOW' and 'Contact Us' in a nice cinematic font, positioned around two-thirds from the top edge of the image. Do not include any other text or contact details.")}
                  className="flex-1 p-3 text-center border border-gray-200 rounded-md hover:border-gray-300 hover:bg-gray-50 transition-colors text-sm"
                  disabled={isGenerating}
                >
                  <div className="w-full aspect-[4/5] rounded-md mb-2 overflow-hidden">
                    <img 
                      src="/Men Shirt.png" 
                      alt="Men's Shirt" 
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <div className="font-medium text-gray-700">Men's Denim Shirt</div>
                  <div className="text-gray-500 text-xs mt-1">Urban Casual Style</div>
                </button>
                
                <button
                  type="button"
                  onClick={() => setPrompt("Create a stylish product post featuring a dummy model wearing the uploaded saree. Set the background in a premium, elegant environment with cinematic lighting for a luxurious look. Add the text 'AVAILABLE NOW' and 'Contact Us' in a nice cinematic font, positioned around two-thirds from the top edge of the image. Do not include any other text or contact details.")}
                  className="flex-1 p-3 text-center border border-gray-200 rounded-md hover:border-gray-300 hover:bg-gray-50 transition-colors text-sm"
                  disabled={isGenerating}
                >
                  <div className="w-full aspect-[4/5] rounded-md mb-2 overflow-hidden">
                    <img 
                      src="/Saaree.jpg" 
                      alt="Elegant Silk Saree" 
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <div className="font-medium text-gray-700">Elegant Silk Saree</div>
                  <div className="text-gray-500 text-xs mt-1">Premium Luxurious Style</div>
                </button>
                
                <button
                  type="button"
                  onClick={() => setPrompt("Create a stylish product post featuring a dummy wearing the uploaded men's T-shirt. Set the background at a cinematic premium dress shop. Add the text 'AVAILABLE NOW' and 'Contact Us' in a nice cinematic font, positioned around two-thirds from the top edge of the image. Do not include any other text or contact details.")}
                  className="flex-1 p-3 text-center border border-gray-200 rounded-md hover:border-gray-300 hover:bg-gray-50 transition-colors text-sm"
                  disabled={isGenerating}
                >
                  <div className="w-full aspect-[4/5] rounded-md mb-2 overflow-hidden">
                    <img 
                      src="/T_shirt.png" 
                      alt="Men's Casual T-shirt" 
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <div className="font-medium text-gray-700">Men's Casual T-shirt</div>
                  <div className="text-gray-500 text-xs mt-1">Premium dress shop style</div>
                </button>
              </div>
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


                {/* AI Generated Caption and Hashtags Section */}
                {result && (
                  <div className="mt-6 space-y-4">
                    <div className="flex items-center justify-between">
                      <h3 className="text-lg font-semibold flex items-center gap-2">
                        <Sparkles className="h-5 w-5 text-purple-500" />
                        AI Generated Content
                      </h3>
                      <div className="flex gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => {
                            const content = `${result.caption || result.full_caption || ''}\n\n${result.hashtags ? result.hashtags.join(' ') : ''}`
                            copyToClipboard(content, 'all')
                          }}
                          className="text-xs"
                        >
                          <Copy className="mr-1 h-3 w-3" />
                          {copiedItem === 'all' ? 'Copied!' : 'Copy All'}
                        </Button>
                      </div>
                    </div>

                    <div className="space-y-4">
                        {/* AI Generated Caption and Hashtags as Single Text */}
                        {(result.caption || result.full_caption || result.hashtags) ? (() => {
                          const parsedCaption = parseCaption(result.caption || result.full_caption || '')
                          const allHashtags = [...(result.hashtags || []), ...(parsedCaption.hashtags || [])]
                          const uniqueHashtags = [...new Set(allHashtags)]
                          
                          // Combine caption and hashtags into a single text
                          const fullText = `${parsedCaption.full_caption || parsedCaption.main_text}${uniqueHashtags.length > 0 ? '\n\n' + uniqueHashtags.join(' ') : ''}`
                          
                          return (
                            <Card className="border-l-4 border-l-blue-500">
                              <CardHeader className="pb-3">
                                <CardTitle className="text-sm flex items-center justify-between">
                                  <div className="flex items-center gap-2">
                                    <MessageSquare className="h-4 w-4 text-blue-500" />
                                    AI Generated Content
                                  </div>
                                  <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={() => copyToClipboard(fullText, 'all')}
                                    className="h-6 px-2"
                                  >
                                    <Copy className="h-3 w-3" />
                                  </Button>
                                </CardTitle>
                              </CardHeader>
                              <CardContent className="pt-0">
                                <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-4 rounded-lg border">
                                  <div className="whitespace-pre-wrap text-sm text-gray-800 leading-relaxed">
                                    {fullText}
                                  </div>
                                </div>
                              </CardContent>
                            </Card>
                          )
                        })() : (
                          <Card className="bg-gray-50 border-gray-200">
                            <CardHeader className="pb-3">
                              <CardTitle className="text-sm flex items-center gap-2">
                                <MessageSquare className="h-4 w-4" />
                                AI Generated Content
                              </CardTitle>
                            </CardHeader>
                            <CardContent className="pt-0">
                              <p className="text-sm text-gray-600">
                                No caption or hashtags generated. This might be due to caption service issues.
                              </p>
                            </CardContent>
                          </Card>
                        )}


                        {/* Social Media Sharing */}
                        <Card className="border-l-4 border-l-purple-500">
                          <CardHeader className="pb-3">
                            <CardTitle className="text-sm flex items-center gap-2">
                              <Share2 className="h-4 w-4 text-purple-500" />
                              Share to Social Media
                            </CardTitle>
                          </CardHeader>
                          <CardContent className="pt-0">
                            <div className="bg-gradient-to-r from-purple-50 to-pink-50 p-4 rounded-lg border mb-4">
                              <p className="text-xs text-gray-600 mb-3">Share your poster and AI-generated content:</p>
                              <div className="grid grid-cols-2 gap-2">
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => shareToSocialMedia('facebook')}
                                  className="flex items-center gap-2 hover:bg-blue-50 hover:border-blue-300"
                                >
                                  <Facebook className="h-4 w-4 text-blue-600" />
                                  Facebook
                                </Button>
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => shareToSocialMedia('twitter')}
                                  className="flex items-center gap-2 hover:bg-blue-50 hover:border-blue-300"
                                >
                                  <Twitter className="h-4 w-4 text-blue-400" />
                                  Twitter
                                </Button>
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => shareToSocialMedia('instagram')}
                                  className="flex items-center gap-2 hover:bg-pink-50 hover:border-pink-300"
                                >
                                  <Instagram className="h-4 w-4 text-pink-600" />
                                  {copiedItem === 'instagram' ? 'Copied!' : 'Instagram'}
                                </Button>
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => shareToSocialMedia('whatsapp')}
                                  className="flex items-center gap-2 hover:bg-green-50 hover:border-green-300"
                                >
                                  <ExternalLink className="h-4 w-4 text-green-600" />
                                  WhatsApp
                                </Button>
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => shareToSocialMedia('email')}
                                  className="flex items-center gap-2 col-span-2 hover:bg-gray-50 hover:border-gray-300"
                                >
                                  <Mail className="h-4 w-4 text-gray-600" />
                                  Email
                                </Button>
                              </div>
                            </div>
                            <div className="text-center">
                              <Button
                                variant="default"
                                size="sm"
                                onClick={shareToClipboard}
                                className="w-full"
                              >
                                <Share2 className="mr-2 h-4 w-4" />
                                {copiedItem === 'share' ? 'Copied to Clipboard!' : 'Copy All Content to Clipboard'}
                              </Button>
                            </div>
                          </CardContent>
                        </Card>
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
      
      {/* Facebook Sharing Modal */}
      <FacebookSharingModal
        isOpen={showFacebookModal}
        onClose={() => setShowFacebookModal(false)}
        content={facebookContent}
        imageUrl={facebookImageUrl}
      />
    </div>
    )
  } catch (error) {
    console.error('Component error:', error)
    setComponentError(error instanceof Error ? error.message : 'Unknown error occurred')
    return null
  }
}
