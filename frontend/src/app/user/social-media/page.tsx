"use client"

import { useState, useEffect } from "react"
import { Card, CardContent } from "@/components/ui/card"
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
  Copy,
  CheckCircle
} from "lucide-react"
import { useAuth } from "@/hooks/useAuth"
import { useToastHelpers } from "@/components/common"
import { apiGet, getFullUrl } from "@/utils/api"

interface Poster {
  id: string
  image_url: string
  public_url?: string  // Cloudinary URL for sharing
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
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const fetchPosters = async () => {
    try {
      setLoading(true)
      const token = await getToken()
      
      const data = await apiGet<{ success?: boolean; results?: Poster[] } | Poster[]>(
        '/api/ai/ai-poster/posters/',
        undefined,
        token
      )
      
      let postersData: Poster[] = []
      if (Array.isArray(data)) {
        postersData = data
      } else if (data && typeof data === 'object' && 'success' in data && data.success && 'results' in data && Array.isArray(data.results)) {
        postersData = data.results
      } else if (data && typeof data === 'object' && 'results' in data && Array.isArray(data.results)) {
        postersData = data.results
      }

      // Ensure image URLs are absolute
      const postersWithFixedUrls = postersData.map((poster: Poster) => {
        if (poster.image_url && !poster.image_url.startsWith('http')) {
          poster.image_url = getFullUrl(poster.image_url)
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
    // Use cloudinary_url (direct image URL) or public_url for sharing
    const posterWithUrls = poster as Poster & { cloudinary_url?: string; public_url?: string };
    const shareableUrl = posterWithUrls.cloudinary_url || posterWithUrls.public_url || poster.image_url
    const captionText = poster.full_caption || poster.caption || ''
    
    // Format hashtags as string
    const posterWithHashtags = poster as Poster & { hashtags?: string[] | string };
    const hashtagsArray = posterWithHashtags.hashtags || []
    const hashtagsStr = Array.isArray(hashtagsArray) 
      ? hashtagsArray.join(' ') 
      : (typeof hashtagsArray === 'string' ? hashtagsArray : '')
    
    // Combine caption and hashtags for the quote parameter
    const fullShareText = captionText 
      ? (hashtagsStr ? `${captionText}\n\n${hashtagsStr}` : captionText)
      : hashtagsStr
    
    // Ensure the URL is absolute and publicly accessible (must be Cloudinary URL)
    if (!shareableUrl || !shareableUrl.startsWith('http')) {
      console.error('❌ ERROR: Cannot share to Facebook - cloudinary_url is missing or not a public URL!')
      alert('Unable to share to Facebook: Poster was not uploaded to Cloudinary. Please check backend logs.')
      return
    }
    
    const sharePageUrl = shareableUrl
    
    // Facebook sharer with Cloudinary image URL AND quote parameter containing caption + hashtags
    // The quote parameter will pre-fill the text field with caption and hashtags
    const shareLink = fullShareText
      ? `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(sharePageUrl)}&quote=${encodeURIComponent(fullShareText)}`
      : `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(sharePageUrl)}`
    
    window.open(shareLink, '_blank')
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
    } catch {
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
            <Image className="h-12 w-12 text-muted-foreground mb-4" aria-label="No posts icon" />
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
                  /* eslint-disable-next-line @next/next/no-img-element */
                  <img
                    src={poster.image_url}
                    alt={poster.caption || poster.prompt || 'Generated poster'}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      const target = e.target as HTMLImageElement
                      if (poster.image_url && !poster.image_url.startsWith('http')) {
                        target.src = getFullUrl(poster.image_url)
                      } else {
                        target.style.display = 'none'
                      }
                    }}
                    loading="lazy"
                  />
                ) : (
                  <div className="absolute inset-0 flex items-center justify-center bg-muted">
                    <Image className="h-12 w-12 text-muted-foreground opacity-50" aria-label="No image available" />
                  </div>
                )}
              </div>

              {/* Content */}
              <CardContent className="p-4 space-y-4">
                {/* Caption */}
                <div className="relative group">
                  <div className="flex items-start justify-between gap-2">
                    <p className="text-sm font-medium text-foreground line-clamp-2 mb-1 flex-1">
                      {poster.caption || poster.full_caption || poster.prompt || 'No caption'}
                    </p>
                    <Button
                      size="sm"
                      variant="ghost"
                      className="h-6 w-6 p-0 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0"
                      onClick={() => {
                        const captionText = poster.full_caption || poster.caption || poster.prompt || ''
                        if (captionText) {
                          copyToClipboard(captionText, `caption-${poster.id}`)
                        }
                      }}
                      title="Copy caption"
                    >
                      {copiedItem === `caption-${poster.id}` ? (
                        <CheckCircle className="h-4 w-4 text-green-600" />
                      ) : (
                        <Copy className="h-4 w-4" />
                      )}
                    </Button>
                  </div>
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

