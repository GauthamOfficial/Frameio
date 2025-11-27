"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { 
  Wand2, 
  Download,
  AlertCircle,
  CheckCircle,
  Loader2,
  Upload,
  Copy,
  MessageSquare,
  Sparkles,
  Share2,
  ExternalLink,
  Facebook,
  Twitter,
  Instagram,
  Mail
} from "lucide-react"
import React, { useState, useRef, useEffect } from "react"
import { useUser, useAuth } from '@clerk/nextjs'
import { useRouter, useSearchParams } from 'next/navigation'
import { useCompanyProfile } from '@/hooks/use-company-profile'

interface GenerationResult {
  success: boolean
  message?: string
  image_path?: string
  image_url?: string
  public_url?: string  // Cloudinary URL for sharing
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
  const searchParams = useSearchParams()
  
  // Error handling
  const [componentError, setComponentError] = useState<string | null>(null)
  
  // Company profile data
  const {
    hasBrandingData,
    brandingData
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
  
  // Textarea auto-resize functionality
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  
  // Auto-resize textarea based on content
  const adjustTextareaHeight = React.useCallback(() => {
    const textarea = textareaRef.current
    if (textarea) {
      // Reset height to auto to get the correct scrollHeight
      textarea.style.height = 'auto'
      // Set height based on scrollHeight, with min and max constraints
      const newHeight = Math.min(Math.max(textarea.scrollHeight, 100), 500)
      textarea.style.height = `${newHeight}px`
    }
  }, [])

  // Read prompt from URL query parameters
  useEffect(() => {
    const promptParam = searchParams.get('prompt')
    if (promptParam) {
      try {
        // searchParams.get() already does basic decoding, but may still have encoded characters
        // Try to decode any remaining encoded characters
        let decodedPrompt = promptParam
        
        // Check if the string contains encoded characters that need decoding
        if (promptParam.includes('%')) {
          try {
            decodedPrompt = decodeURIComponent(promptParam)
          } catch {
            // If decodeURIComponent fails, try a safer approach
            // Decode character by character for problematic sequences
            decodedPrompt = promptParam.replace(/%[0-9A-F]{2}/gi, (match) => {
              try {
                return decodeURIComponent(match)
              } catch {
                return match // Keep the original if decoding fails
              }
            })
          }
        }
        
        setPrompt(decodedPrompt)
        // Clear the URL parameter after reading it
        router.replace('/dashboard/poster-generator', { scroll: false })
        // Adjust textarea height after setting prompt from URL
        setTimeout(() => adjustTextareaHeight(), 100)
      } catch {
        // If all else fails, use the parameter as-is
        console.error('Error processing prompt parameter:', error)
        setPrompt(promptParam)
        // Clear the URL parameter even if there was an error
        router.replace('/dashboard/poster-generator', { scroll: false })
        // Adjust textarea height even if there was an error
        setTimeout(() => adjustTextareaHeight(), 100)
      }
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams, router, adjustTextareaHeight])
  
  // Adjust textarea height when prompt changes
  useEffect(() => {
    // Use setTimeout to ensure DOM is updated
    const timer = setTimeout(() => {
      adjustTextareaHeight()
    }, 0)
    return () => clearTimeout(timer)
  }, [prompt, adjustTextareaHeight])
  
  // Caption and hashtag functionality
  const [copiedItem, setCopiedItem] = useState<string | null>(null)

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

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const copyHashtags = async () => {
    if (result?.hashtags) {
      const hashtagText = result.hashtags.join(' ')
      await copyToClipboard(hashtagText, 'hashtags')
    }
  }

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const copyFullCaption = async () => {
    if (result?.full_caption) {
      await copyToClipboard(result.full_caption, 'caption')
    }
  }

  const shareToSocialMedia = async (platform: string) => {
    if (!result?.image_url || !result?.full_caption) return

    // Generate a unique poster ID (in a real app, this would come from the backend)
    const posterId = `poster_${Date.now()}`
    
    const shareText = result.full_caption
    let shareLink = ''
    
    switch (platform) {
      case 'facebook': {
        // Use cloudinary_url (direct image URL) or public_url for sharing
        // Priority: cloudinary_url > public_url > image_url (if Cloudinary)
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        let shareableUrl = (result as any).cloudinary_url
        if (!shareableUrl || !shareableUrl.startsWith('http')) {
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          shareableUrl = (result as any).public_url
        }
        if (!shareableUrl || !shareableUrl.startsWith('http')) {
          // Last resort: check if image_url is a Cloudinary URL
          const imageUrl = result.image_url
          if (imageUrl && imageUrl.startsWith('http') && imageUrl.includes('cloudinary')) {
            shareableUrl = imageUrl
          }
        }
        
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const captionText = shareText || (result as any).caption || ''
        
        // Format hashtags as string
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const hashtagsArray = (result as any).hashtags || []
        const hashtagsStr = Array.isArray(hashtagsArray) 
          ? hashtagsArray.join(' ') 
          : (typeof hashtagsArray === 'string' ? hashtagsArray : '')
        
        // Combine caption and hashtags for the quote parameter
        const fullShareText = captionText 
          ? (hashtagsStr ? `${captionText}\n\n${hashtagsStr}` : captionText)
          : hashtagsStr
        
        // CRITICAL: shareableUrl must be a Cloudinary URL (starts with http)
        // Local URLs won't work for Facebook sharing
        if (!shareableUrl) {
          console.error('❌ ERROR: Cannot share to Facebook - no Cloudinary URL available!')
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          console.error('cloudinary_url:', (result as any).cloudinary_url)
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          console.error('public_url:', (result as any).public_url)
          console.error('image_url:', result.image_url)
          console.error('Please check backend logs for Cloudinary upload errors.')
          alert('Unable to share to Facebook: Poster was not uploaded to Cloudinary. Please check backend logs.')
          return
        }
        
        if (!shareableUrl.startsWith('http')) {
          console.error('❌ ERROR: Cannot share to Facebook - URL is not a Cloudinary URL!')
          console.error('shareableUrl:', shareableUrl)
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          console.error('cloudinary_url:', (result as any).cloudinary_url)
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          console.error('public_url:', (result as any).public_url)
          console.error('Please check backend logs for Cloudinary upload errors.')
          alert('Unable to share to Facebook: Poster URL is not publicly accessible. Please check backend logs.')
          return
        }
        
        // Ensure the URL is absolute and publicly accessible (should already be from Cloudinary)
        const sharePageUrl = shareableUrl
        
        // Facebook sharer with Cloudinary image URL AND quote parameter containing caption + hashtags
        // The quote parameter will pre-fill the text field with caption and hashtags
        if (fullShareText) {
          shareLink = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(sharePageUrl)}&quote=${encodeURIComponent(fullShareText)}`
        } else {
          shareLink = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(sharePageUrl)}`
        }
        
        // Open Facebook share dialog in a new tab
        window.open(shareLink, '_blank')
        return
      }
      case 'twitter': {
        const twitterUrl = await getPosterShareUrl(posterId)
        shareLink = `https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}&url=${encodeURIComponent(twitterUrl)}`
        break
      }
      case 'instagram': {
        // Instagram doesn't support direct sharing, copy to clipboard
        const instagramUrl = await getPosterShareUrl(posterId)
        copyToClipboard(`${shareText}\n\n${instagramUrl}`, 'instagram')
        return
      }
      case 'whatsapp': {
        const whatsappUrl = await getPosterShareUrl(posterId)
        shareLink = `https://wa.me/?text=${encodeURIComponent(shareText + ' ' + whatsappUrl)}`
        break
      }
      case 'email': {
        const emailUrl = await getPosterShareUrl(posterId)
        shareLink = `mailto:?subject=Check out this poster&body=${encodeURIComponent(shareText + '\n\n' + emailUrl)}`
        break
      }
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
    } catch {
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

        // Ensure path ends with trailing slash for Django compatibility
        // Remove any existing trailing slash first, then add one to ensure consistency
        const cleanPath = path.replace(/\/+$/, '')
        const normalizedPath = `${cleanPath}/`

        const attemptFetch = async (url: string) => {
          const controller = new AbortController()
          const localTimeout = setTimeout(() => controller.abort(), 180000)
          try {
            console.log('Fetching URL:', url) // Debug log
            const res = await fetch(url, { ...init, signal: controller.signal })
            return res
          } finally {
            clearTimeout(localTimeout)
          }
        }

        // For Django endpoints that require trailing slashes, use absolute URLs directly
        // to bypass Next.js rewrites which may strip trailing slashes
        // 1) Try absolute bases first (bypasses Next.js rewrites)
        for (const base of fallbackBases) {
          try {
            const cleanBase = base.replace(/\/+$/, '')
            // Ensure path starts with / for proper URL construction
            const pathWithSlash = normalizedPath.startsWith('/') ? normalizedPath : `/${normalizedPath}`
            const absoluteUrl = `${cleanBase}${pathWithSlash}`
            console.log('Attempting absolute URL:', absoluteUrl) // Debug log
            return await attemptFetch(absoluteUrl)
          } catch (e) {
            lastErr = e
            console.error('Absolute URL fetch failed:', e) // Debug log
          }
        }

        // 2) Fallback to same-origin relative path (leverages Next.js rewrites)
        // This is less reliable for trailing slashes but kept as fallback
        try {
          console.log('Attempting relative path:', normalizedPath) // Debug log
          return await attemptFetch(normalizedPath)
        } catch (e) {
          lastErr = e
          console.error('Relative path fetch failed:', e) // Debug log
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
        
        // Clone the response so we can read it multiple times
        const clonedResponse = response.clone()
        
        try {
          // First try to parse as JSON
          const errorData = await response.json()
          console.error('Error response data:', errorData)
          message = errorData?.error || errorData?.message || errorData?.detail || message
          // Include more details if available
          if (errorData?.detail && errorData.detail !== message) {
            message += `: ${errorData.detail}`
          }
        } catch {
          // If JSON parsing fails, try as text
          try {
            const responseText = await clonedResponse.text()
            console.error('Error response text (raw):', responseText)
            
            if (responseText && responseText.trim()) {
              // Try to parse as JSON one more time from text
              try {
                const errorData = JSON.parse(responseText)
                message = errorData?.error || errorData?.message || errorData?.detail || message
              } catch {
                // Not JSON, use text as message
                message = responseText.length > 200 ? responseText.substring(0, 200) + '...' : responseText
              }
            } else {
              // Empty response - provide helpful message
              message = `HTTP ${response.status}: Server returned empty response. Check backend logs for details.`
              console.error('Empty error response received')
            }
          } catch {
            console.error('Failed to read error response')
            message = `HTTP ${response.status}: Unable to read error response. Check backend logs.`
          }
        }
        
        console.error('Full error message:', message)
        throw new Error(message)
      }

      const data = await response.json()
      console.log('Generation result:', data)
      console.log('Response keys:', Object.keys(data))
      console.log('public_url value:', data.public_url)
      console.log('image_url value:', data.image_url)

      if (data.success) {
        // Validate public_url - it should always be present in the response
        // but may be empty if Cloudinary upload failed
        // Check for missing key, undefined, or null
        if (!data.hasOwnProperty('public_url') || data.public_url === undefined || data.public_url === null) {
          console.error('❌ CRITICAL ERROR: public_url key is missing or invalid from API response!')
          console.error('Response keys:', Object.keys(data))
          console.error('public_url value:', data.public_url)
          console.error('public_url type:', typeof data.public_url)
          // Set it to empty string so the rest of the code doesn't break
          data.public_url = ''
        }
        
        // Ensure public_url is a string (convert if needed)
        if (typeof data.public_url !== 'string') {
          console.warn('⚠️ WARNING: public_url is not a string, converting...')
          data.public_url = String(data.public_url || '')
        }
        
        // Validate cloudinary_url - it should always be present in the response
        if (!data.hasOwnProperty('cloudinary_url') || data.cloudinary_url === undefined || data.cloudinary_url === null) {
          console.warn('⚠️ WARNING: cloudinary_url key is missing or invalid from API response!')
          console.warn('Response keys:', Object.keys(data))
          console.warn('cloudinary_url value:', data.cloudinary_url)
          // Set it to empty string so the rest of the code doesn't break
          data.cloudinary_url = ''
        }
        
        // Ensure cloudinary_url is a string (convert if needed)
        if (typeof data.cloudinary_url !== 'string') {
          console.warn('⚠️ WARNING: cloudinary_url is not a string, converting...')
          data.cloudinary_url = String(data.cloudinary_url || '')
        }
        
        // Check if public_url is a valid Cloudinary URL (starts with http)
        if (!data.public_url || !data.public_url.startsWith('http')) {
          console.error('❌ CRITICAL ERROR: public_url is missing or is not a Cloudinary URL!')
          console.error('public_url value:', data.public_url)
          console.error('public_url type:', typeof data.public_url)
          console.error('This means Facebook sharing will NOT work!')
          console.error('Please check backend logs for Cloudinary upload errors.')
          console.error('The poster was generated successfully, but cannot be shared on Facebook.')
          // Don't set to local URL - this will break Facebook sharing
          // The backend should have handled this, but if it didn't, we'll show an error
          // Still set the result so the user can see the poster, but sharing will be disabled
        } else {
          console.log('✅ Poster generated successfully!')
          console.log('✅ Public URL (Cloudinary):', data.public_url)
        }
        
        // Check if cloudinary_url is valid (preferred for direct image sharing)
        if (data.cloudinary_url && data.cloudinary_url.startsWith('http')) {
          console.log('✅ Cloudinary URL (direct image):', data.cloudinary_url)
        } else if (data.public_url && data.public_url.startsWith('http')) {
          // Fallback: use public_url if cloudinary_url is not available
          console.warn('⚠️ cloudinary_url is not available, using public_url as fallback')
          data.cloudinary_url = data.public_url
        } else {
          console.warn('⚠️ WARNING: cloudinary_url is not a valid Cloudinary URL!')
          console.warn('cloudinary_url value:', data.cloudinary_url)
        }
        
        setResult(data)
        setError(null)
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


  // eslint-disable-next-line @typescript-eslint/no-unused-vars
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
                ref={textareaRef}
                id="prompt"
                placeholder="Describe your Post"
                value={prompt}
                onChange={(e) => {
                  setPrompt(e.target.value)
                  // Auto-resize on input
                  setTimeout(() => adjustTextareaHeight(), 0)
                }}
                disabled={isGenerating}
                className="min-h-[100px] max-h-[500px] resize-none overflow-y-auto placeholder:opacity-50"
                style={{ height: 'auto' }}
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
                    {/* eslint-disable-next-line @next/next/no-img-element */}
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
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img 
                      src="/Men Shirt.png" 
                      alt="Men's Shirt" 
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <div className="font-medium text-gray-700">Men&apos;s Denim Shirt</div>
                  <div className="text-gray-500 text-xs mt-1">Urban Casual Style</div>
                </button>
                
                <button
                  type="button"
                  onClick={() => setPrompt("Create a stylish product post featuring a dummy model wearing the uploaded saree. Set the background in a premium, elegant environment with cinematic lighting for a luxurious look. Add the text 'AVAILABLE NOW' and 'Contact Us' in a nice cinematic font, positioned around two-thirds from the top edge of the image. Do not include any other text or contact details.")}
                  className="flex-1 p-3 text-center border border-gray-200 rounded-md hover:border-gray-300 hover:bg-gray-50 transition-colors text-sm"
                  disabled={isGenerating}
                >
                  <div className="w-full aspect-[4/5] rounded-md mb-2 overflow-hidden">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
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
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img 
                      src="/T_shirt.png" 
                      alt="Men's Casual T-shirt" 
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <div className="font-medium text-gray-700">Men&apos;s Casual T-shirt</div>
                  <div className="text-gray-500 text-xs mt-1">Premium dress shop style</div>
                </button>
              </div>
              <Button
                type="button"
                variant="outline"
                onClick={() => router.push('/dashboard/templates')}
                className="w-full mt-2"
                disabled={isGenerating}
              >
                More Templates
                <ExternalLink className="ml-2 h-4 w-4" />
              </Button>
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
                    {/* eslint-disable-next-line @next/next/no-img-element */}
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
                  {/* eslint-disable-next-line @next/next/no-img-element */}
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
    </div>
    )
  } catch (error) {
    console.error('Component error:', error)
    setComponentError(error instanceof Error ? error.message : 'Unknown error occurred')
    return null
  }
}
