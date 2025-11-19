"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { 
  Image, 
  Calendar, 
  Download, 
  ExternalLink, 
  Loader2, 
  Facebook, 
  Instagram, 
  MessageCircle,
  Share2,
  Copy,
  CheckCircle
} from "lucide-react"
import { useAuth } from "@/hooks/useAuth"
import { useToastHelpers } from "@/components/common"

interface Poster {
  id: string
  image_url: string
  caption: string
  full_caption: string
  prompt: string
  aspect_ratio: string
  hashtags: string[]
  emoji: string
  created_at: string
  branding_applied: boolean
  logo_added: boolean
  contact_info_added: boolean
}

export default function SocialMediaPage() {
  const [posters, setPosters] = useState<Poster[]>([])
  const [loading, setLoading] = useState(true)
  const [copiedItem, setCopiedItem] = useState<string | null>(null)
  const { getToken } = useAuth()
  const { showError, showSuccess } = useToastHelpers()

  useEffect(() => {
    fetchPosters()
  }, [])

  const fetchPosters = async () => {
    try {
      setLoading(true)
      const token = await getToken()
      const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'
      const baseUrl = apiBase.replace(/\/$/, '')
      const url = `${baseUrl}/api/ai/ai-poster/posters/`
      
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      }
      
      if (token) {
        headers['Authorization'] = `Bearer ${token}`
      }
      
      const response = await fetch(url, {
        method: 'GET',
        headers,
        credentials: 'include'
      })

      if (!response.ok) {
        if (response.status === 404 || response.status === 204) {
          setPosters([])
          return
        }
        throw new Error(`Failed to fetch posters (${response.status})`)
      }

      const text = await response.text()
      if (!text) {
        setPosters([])
        return
      }

      const data = JSON.parse(text)
      
      let postersData: Poster[] = []
      if (data.success && data.results) {
        postersData = data.results
      } else if (Array.isArray(data)) {
        postersData = data
      } else if (data.results && Array.isArray(data.results)) {
        postersData = data.results
      }

      // Ensure image URLs are absolute
      const postersWithFixedUrls = postersData.map((poster: Poster) => {
        if (poster.image_url && !poster.image_url.startsWith('http')) {
          poster.image_url = poster.image_url.startsWith('/') 
            ? `${baseUrl}${poster.image_url}`
            : `${baseUrl}/${poster.image_url}`
        }
        return poster
      })

      setPosters(postersWithFixedUrls)
    } catch (error) {
      console.error('Error fetching posters:', error)
      const errorMessage = error instanceof Error ? error.message : 'Failed to load posts'
      if (!errorMessage.includes('Network') && !errorMessage.includes('Failed to fetch')) {
        showError(errorMessage)
      }
      setPosters([])
    } finally {
      setLoading(false)
    }
  }

  const copyToClipboard = async (text: string, type: string) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopiedItem(type)
      setTimeout(() => setCopiedItem(null), 2000)
      showSuccess('Copied to clipboard!')
    } catch (err) {
      console.error('Failed to copy text: ', err)
      showError('Failed to copy to clipboard')
    }
  }

  const shareToWhatsApp = (poster: Poster) => {
    const shareText = poster.full_caption || poster.caption || ''
    const shareUrl = typeof window !== 'undefined' ? window.location.origin + `/poster/${poster.id}` : ''
    const whatsappText = `${shareText}\n\n${shareUrl}`
    const whatsappLink = `https://wa.me/?text=${encodeURIComponent(whatsappText)}`
    window.open(whatsappLink, '_blank')
  }

  const shareToFacebook = async (poster: Poster) => {
    const shareText = poster.full_caption || poster.caption || ''
    const shareUrl = typeof window !== 'undefined' ? window.location.origin + `/poster/${poster.id}` : ''
    
    try {
      // Try to use Facebook sharer
      const shareLink = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(shareUrl)}&quote=${encodeURIComponent(shareText)}`
      window.open(
        shareLink,
        'facebook-share-dialog',
        'width=800,height=600,scrollbars=yes,resizable=yes'
      )
    } catch (error) {
      console.error('Facebook sharing error:', error)
      // Fallback: Copy to clipboard
      const imageUrl = poster.image_url.startsWith('http') 
        ? poster.image_url 
        : `${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'}${poster.image_url}`
      
      const facebookText = `${shareText}\n\n🖼️ View the full poster: ${imageUrl}`
      await copyToClipboard(facebookText, `facebook-${poster.id}`)
    }
  }

  const shareToInstagram = (poster: Poster) => {
    const shareText = poster.full_caption || poster.caption || ''
    const shareUrl = typeof window !== 'undefined' ? window.location.origin + `/poster/${poster.id}` : ''
    const instagramText = `${shareText}\n\n${shareUrl}`
    copyToClipboard(instagramText, `instagram-${poster.id}`)
  }

  const handleDownload = async (poster: Poster) => {
    try {
      const response = await fetch(poster.image_url)
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `poster-${poster.id}.png`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      showSuccess('Poster downloaded successfully!')
    } catch (error) {
      console.error('Error downloading poster:', error)
      showError('Failed to download poster')
    }
  }

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString)
      if (isNaN(date.getTime())) {
        return 'Invalid date'
      }
      const now = new Date()
      const diffTime = Math.abs(now.getTime() - date.getTime())
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
      
      if (diffDays === 0) {
        return 'Today'
      } else if (diffDays === 1) {
        return 'Yesterday'
      } else if (diffDays < 7) {
        return `${diffDays} days ago`
      } else if (diffDays < 30) {
        const weeks = Math.floor(diffDays / 7)
        return `${weeks} ${weeks === 1 ? 'week' : 'weeks'} ago`
      } else {
        return date.toLocaleDateString('en-US', {
          year: 'numeric',
          month: 'short',
          day: 'numeric'
        })
      }
    } catch (error) {
      return 'Invalid date'
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Social Media Posts</h1>
          <p className="text-muted-foreground">
            View and share your generated posts on social media platforms.
          </p>
        </div>
        <Card>
          <CardContent className="flex items-center justify-center h-64">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Social Media Posts</h1>
        <p className="text-muted-foreground">
          View and share your generated posts on social media platforms.
        </p>
      </div>

      {posters.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center h-64 text-center">
            <Image className="h-12 w-12 text-muted-foreground mb-4" />
            <p className="text-muted-foreground mb-2">No posts generated yet</p>
            <p className="text-sm text-muted-foreground">
              Create your first poster to see it here
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {posters.map((poster) => (
            <Card key={poster.id} className="overflow-hidden hover:shadow-lg transition-shadow">
              {/* Image */}
              <div className="aspect-square bg-muted overflow-hidden relative">
                {poster.image_url ? (
                  <img
                    src={poster.image_url}
                    alt={poster.caption || poster.prompt || 'Generated poster'}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      const target = e.target as HTMLImageElement
                      if (poster.image_url && !poster.image_url.startsWith('http')) {
                        const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'
                        const baseUrl = apiBase.replace(/\/$/, '')
                        const fixedUrl = poster.image_url.startsWith('/') 
                          ? `${baseUrl}${poster.image_url}`
                          : `${baseUrl}/${poster.image_url}`
                        target.src = fixedUrl
                      } else {
                        target.style.display = 'none'
                      }
                    }}
                    loading="lazy"
                  />
                ) : (
                  <div className="absolute inset-0 flex items-center justify-center bg-muted">
                    <Image className="h-12 w-12 text-muted-foreground opacity-50" />
                  </div>
                )}
              </div>

              {/* Content */}
              <CardContent className="p-4 space-y-4">
                {/* Caption */}
                <div>
                  <p className="text-sm font-medium text-foreground line-clamp-2 mb-1">
                    {poster.caption || poster.full_caption || poster.prompt || 'No caption'}
                  </p>
                  {poster.prompt && poster.prompt !== poster.caption && (
                    <p className="text-xs text-muted-foreground line-clamp-1">
                      {poster.prompt}
                    </p>
                  )}
                </div>

                {/* Date */}
                <div className="flex items-center text-xs text-muted-foreground">
                  <Calendar className="h-3 w-3 mr-1" />
                  {formatDate(poster.created_at)}
                </div>

                {/* Hashtags */}
                {poster.hashtags && poster.hashtags.length > 0 && (
                  <div className="flex flex-wrap gap-1">
                    {poster.hashtags.slice(0, 3).map((tag, idx) => (
                      <Badge key={idx} variant="outline" className="text-xs">
                        {tag.replace('#', '')}
                      </Badge>
                    ))}
                    {poster.hashtags.length > 3 && (
                      <Badge variant="outline" className="text-xs">
                        +{poster.hashtags.length - 3}
                      </Badge>
                    )}
                  </div>
                )}

                {/* Share Buttons */}
                <div className="space-y-2 pt-2 border-t">
                  <div className="grid grid-cols-3 gap-2">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => shareToWhatsApp(poster)}
                      className="w-full"
                    >
                      <MessageCircle className="h-4 w-4 mr-1 text-green-600" />
                      <span className="text-xs">WhatsApp</span>
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => shareToFacebook(poster)}
                      className="w-full"
                    >
                      <Facebook className="h-4 w-4 mr-1 text-blue-600" />
                      <span className="text-xs">Facebook</span>
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => shareToInstagram(poster)}
                      className="w-full"
                    >
                      {copiedItem === `instagram-${poster.id}` ? (
                        <>
                          <CheckCircle className="h-4 w-4 mr-1 text-green-600" />
                          <span className="text-xs">Copied!</span>
                        </>
                      ) : (
                        <>
                          <Instagram className="h-4 w-4 mr-1 text-pink-600" />
                          <span className="text-xs">Instagram</span>
                        </>
                      )}
                    </Button>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-2">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleDownload(poster)}
                      className="w-full"
                    >
                      <Download className="h-4 w-4 mr-1" />
                      <span className="text-xs">Download</span>
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => window.open(poster.image_url, '_blank')}
                      className="w-full"
                    >
                      <ExternalLink className="h-4 w-4 mr-1" />
                      <span className="text-xs">View</span>
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}

