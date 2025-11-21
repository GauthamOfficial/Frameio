"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter, DialogClose } from "@/components/ui/dialog"
import { Calendar, Plus, Clock, Image as ImageIcon, Loader2 } from "lucide-react"
import { useAuth } from "@/hooks/useAuth"
import { useToastHelpers } from "@/components/common"

interface GeneratedPoster {
  id: string
  image_url: string
  public_url?: string
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

interface ScheduledPost {
  id: string
  platform: string
  platform_display: string
  asset_url: string
  caption: string
  scheduled_time: string
  status: string
  status_display: string
  created_at: string
  posted_at?: string
  error_message?: string
}

export default function SchedulerPage() {
  const [generatedPosters, setGeneratedPosters] = useState<GeneratedPoster[]>([])
  const [scheduledPosts, setScheduledPosts] = useState<ScheduledPost[]>([])
  const [loading, setLoading] = useState(true)
  const [scheduling, setScheduling] = useState(false)
  const [showScheduleModal, setShowScheduleModal] = useState(false)
  const [selectedPoster, setSelectedPoster] = useState<GeneratedPoster | null>(null)
  const [scheduleData, setScheduleData] = useState({
    platform: 'instagram',
    scheduledTime: '',
    caption: ''
  })
  
  const { getToken } = useAuth()
  const { showError, showSuccess } = useToastHelpers()

  // Helper to get organization context from user profile if not in localStorage
  const getOrganizationContext = async () => {
    try {
      // First check localStorage
      const orgSlug = typeof window !== 'undefined' ? window.localStorage.getItem('organizationSlug') : null
      const devOrgId = typeof window !== 'undefined' ? window.localStorage.getItem('devOrgId') : null
      
      if (orgSlug || devOrgId) {
        return { orgSlug, devOrgId }
      }

      // Try to get from user profile
      const token = await getToken()
      if (token) {
        const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'
        const baseUrl = apiBase.replace(/\/$/, '')
        const response = await fetch(`${baseUrl}/api/users/`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        })
        
        if (response.ok) {
          const data = await response.json()
          const user = Array.isArray(data) ? data[0] : data
          if (user?.current_organization) {
            // Store for future use
            if (typeof window !== 'undefined') {
              window.localStorage.setItem('devOrgId', user.current_organization)
            }
            return { devOrgId: user.current_organization }
          }
        }
      }
    } catch (e) {
      console.warn('Failed to get organization context from user profile:', e)
    }
    return { orgSlug: null, devOrgId: null }
  }

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    await Promise.all([fetchPosters(), fetchScheduledPosts()])
  }

  const fetchPosters = async () => {
    try {
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

      // Add organization context headers
      try {
        const orgSlug = typeof window !== 'undefined' ? window.localStorage.getItem('organizationSlug') : null
          || process.env.NEXT_PUBLIC_ORGANIZATION_SLUG
        if (orgSlug) {
          headers['X-Organization'] = orgSlug
        }
        const devOrgId = typeof window !== 'undefined' ? window.localStorage.getItem('devOrgId') : null
          || process.env.NEXT_PUBLIC_DEV_ORG_ID
        if (devOrgId) {
          headers['X-Dev-Org-Id'] = devOrgId
        }
      } catch {}
      
      let response: Response
      try {
        response = await fetch(url, {
          method: 'GET',
          headers,
          credentials: 'include'
        })
      } catch (networkError) {
        // Handle network errors gracefully
        console.error('Network error fetching posters:', networkError)
        setGeneratedPosters([])
        return
      }

      if (!response.ok) {
        if (response.status === 404 || response.status === 204) {
          setGeneratedPosters([])
          return
        }
        throw new Error(`Failed to fetch posters (${response.status})`)
      }

      const text = await response.text()
      if (!text) {
        setGeneratedPosters([])
        return
      }

      const data = JSON.parse(text)
      
      let postersData: GeneratedPoster[] = []
      if (data.success && data.results) {
        postersData = data.results
      } else if (Array.isArray(data)) {
        postersData = data
      } else if (data.results && Array.isArray(data.results)) {
        postersData = data.results
      }

      // Ensure image URLs are absolute
      const postersWithFixedUrls = postersData.map((poster: GeneratedPoster) => {
        if (poster.image_url && !poster.image_url.startsWith('http')) {
          poster.image_url = poster.image_url.startsWith('/') 
            ? `${baseUrl}${poster.image_url}`
            : `${baseUrl}/${poster.image_url}`
        }
        return poster
      })

      setGeneratedPosters(postersWithFixedUrls)
    } catch (error) {
      console.error('Error fetching posters:', error)
      setGeneratedPosters([])
    } finally {
      setLoading(false)
    }
  }

  const fetchScheduledPosts = async () => {
    try {
      const token = await getToken()
      const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'
      const baseUrl = apiBase.replace(/\/$/, '')
      const url = `${baseUrl}/api/ai/schedule/`
      
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      }
      
      if (token) {
        headers['Authorization'] = `Bearer ${token}`
      }

      // Add organization context headers
      try {
        const orgSlug = typeof window !== 'undefined' ? window.localStorage.getItem('organizationSlug') : null
          || process.env.NEXT_PUBLIC_ORGANIZATION_SLUG
        if (orgSlug) {
          headers['X-Organization'] = orgSlug
        }
        const devOrgId = typeof window !== 'undefined' ? window.localStorage.getItem('devOrgId') : null
          || process.env.NEXT_PUBLIC_DEV_ORG_ID
        if (devOrgId) {
          headers['X-Dev-Org-Id'] = devOrgId
        }
      } catch {}
      
      let response: Response
      try {
        response = await fetch(url, {
          method: 'GET',
          headers,
          credentials: 'include'
        })
      } catch (networkError) {
        // Handle network errors gracefully
        console.error('Network error fetching scheduled posts:', networkError)
        setScheduledPosts([])
        return
      }

      if (!response.ok) {
        if (response.status === 404 || response.status === 204) {
          setScheduledPosts([])
          return
        }
        throw new Error(`Failed to fetch scheduled posts (${response.status})`)
      }

      const text = await response.text()
      if (!text) {
        setScheduledPosts([])
        return
      }

      const data = JSON.parse(text)
      
      let scheduledData: ScheduledPost[] = []
      if (Array.isArray(data)) {
        scheduledData = data
      } else if (data.results && Array.isArray(data.results)) {
        scheduledData = data.results
      }

      setScheduledPosts(scheduledData)
    } catch (error) {
      console.error('Error fetching scheduled posts:', error)
      setScheduledPosts([])
    }
  }

  const handleSchedulePoster = (poster: GeneratedPoster) => {
    setSelectedPoster(poster)
    setScheduleData({
      platform: 'instagram',
      scheduledTime: '',
      caption: poster.full_caption || poster.caption || ''
    })
    setShowScheduleModal(true)
  }

  const handleScheduleSubmit = async () => {
    if (!selectedPoster) return
    
    if (!scheduleData.scheduledTime || !scheduleData.caption.trim()) {
      showError("Please fill in all required fields")
      return
    }

    // Validate scheduled time is in the future
    const scheduledDate = new Date(scheduleData.scheduledTime)
    if (scheduledDate <= new Date()) {
      showError("Scheduled time must be in the future")
      return
    }

    setScheduling(true)
    try {
      const token = await getToken()
      const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'
      const baseUrl = apiBase.replace(/\/$/, '')
      const url = `${baseUrl}/api/ai/schedule/`
      
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      }
      
      if (token) {
        headers['Authorization'] = `Bearer ${token}`
      }

      // Add organization context headers
      try {
        const orgContext = await getOrganizationContext()
        const orgSlug = orgContext.orgSlug || process.env.NEXT_PUBLIC_ORGANIZATION_SLUG
        const devOrgId = orgContext.devOrgId || process.env.NEXT_PUBLIC_DEV_ORG_ID
        
        if (orgSlug) {
          headers['X-Organization'] = orgSlug
        }
        if (devOrgId) {
          headers['X-Dev-Org-Id'] = devOrgId
        }
        // Backend will automatically handle organization resolution from user membership if headers not provided
      } catch (e) {
        console.error('Error setting organization headers:', e)
      }

      // Ensure asset_url is an absolute URL
      let assetUrl = selectedPoster.public_url || selectedPoster.image_url
      if (assetUrl && !assetUrl.startsWith('http')) {
        assetUrl = assetUrl.startsWith('/') 
          ? `${baseUrl}${assetUrl}`
          : `${baseUrl}/${assetUrl}`
      }
      
      if (!assetUrl) {
        showError("Poster image URL is missing")
        return
      }
      
      const requestBody = {
        platform: scheduleData.platform,
        asset_url: assetUrl,
        caption: scheduleData.caption,
        scheduled_time: scheduledDate.toISOString(),
        metadata: {
          poster_id: selectedPoster.id,
          hashtags: selectedPoster.hashtags || [],
          prompt: selectedPoster.prompt,
          aspect_ratio: selectedPoster.aspect_ratio
        }
      }
      
      console.log('Scheduling post with data:', {
        url,
        headers: Object.keys(headers),
        body: requestBody
      })
      
      let response: Response
      try {
        response = await fetch(url, {
          method: 'POST',
          headers,
          credentials: 'include',
          body: JSON.stringify(requestBody)
        })
      } catch (networkError) {
        // Handle network errors (CORS, connection refused, etc.)
        console.error('Network error scheduling post:', networkError)
        const errorObj = networkError instanceof Error ? networkError : new Error(String(networkError))
        
        let errorMessage = 'Failed to schedule post'
        if (errorObj.message === 'Failed to fetch' || errorObj.name === 'TypeError') {
          errorMessage = 'Cannot connect to server. Please ensure the backend is running and accessible.'
        } else if (errorObj.message.includes('CORS')) {
          errorMessage = 'CORS error. Please check backend CORS configuration.'
        } else {
          errorMessage = `Network error: ${errorObj.message}`
        }
        
        showError(errorMessage)
        return
      }

      if (!response.ok) {
        let errorData: any = {}
        try {
          const text = await response.text()
          console.error('Backend error response:', text)
          if (text) {
            errorData = JSON.parse(text)
            console.error('Parsed error data:', errorData)
          }
        } catch (e) {
          console.error('Failed to parse error response:', e)
        }
        
        // Handle validation errors with field details
        let errorMessage = errorData.detail || errorData.error || errorData.message || `Failed to schedule post (${response.status})`
        
        // If detail is an object (field validation errors), format it nicely
        if (typeof errorData.detail === 'object' && errorData.detail !== null && !Array.isArray(errorData.detail)) {
          const fieldErrors = Object.entries(errorData.detail)
            .map(([field, error]: [string, any]) => {
              const errorText = Array.isArray(error) ? error[0] : error
              return `${field}: ${errorText}`
            })
            .join(', ')
          errorMessage = fieldErrors || errorMessage
        }
        
        // Log full error for debugging
        console.error('Scheduling error:', {
          status: response.status,
          errorData,
          errorMessage
        })
        
        // Show error without throwing to prevent console errors
        showError(errorMessage)
        return
      }

      showSuccess("Post scheduled successfully!")
      setShowScheduleModal(false)
      setSelectedPoster(null)
      setScheduleData({
        platform: 'instagram',
        scheduledTime: '',
        caption: ''
      })
      
      // Refresh scheduled posts
      await fetchScheduledPosts()
    } catch (error) {
      // Only log to console, don't throw - error is already shown to user
      console.error('Error scheduling post:', error)
      const errorMessage = error instanceof Error ? error.message : 'Failed to schedule post'
      showError(errorMessage)
    } finally {
      setScheduling(false)
    }
  }

  const formatDateTime = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    })
  }

  const formatTime = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    })
  }

  const getStatusBadgeVariant = (status: string) => {
    switch (status.toLowerCase()) {
      case 'posted':
        return 'default'
      case 'scheduled':
        return 'secondary'
      case 'pending':
        return 'outline'
      case 'failed':
        return 'destructive'
      default:
        return 'outline'
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-chart-1" />
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Social Media Scheduler</h1>
          <p className="text-muted-foreground mt-1">
            Plan and schedule your textile marketing posts across platforms.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-8">
        {/* Calendar View - Scheduled Posts */}
        <Card className="textile-hover textile-shadow">
          <CardHeader>
            <CardTitle className="flex items-center">
              <Calendar className="mr-2 h-5 w-5 text-chart-1" />
              Scheduled Posts
            </CardTitle>
          </CardHeader>
          <CardContent>
            {scheduledPosts.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <Calendar className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>No scheduled posts yet</p>
                <p className="text-sm mt-2">Schedule a post from your generated posters below</p>
              </div>
            ) : (
              <div className="space-y-4">
                {scheduledPosts.map((post) => (
                  <div key={post.id} className="flex items-center justify-between p-4 border border-border rounded-lg">
                    <div className="flex items-center space-x-4 flex-1">
                      <div className="w-10 h-10 bg-chart-1 rounded-lg flex items-center justify-center flex-shrink-0">
                        <Calendar className="h-5 w-5 text-white" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-foreground truncate">{post.caption.substring(0, 50)}...</p>
                        <p className="text-sm text-muted-foreground">
                          {formatTime(post.scheduled_time)} • {post.platform_display || post.platform}
                        </p>
                        <p className="text-xs text-muted-foreground mt-1">
                          {formatDateTime(post.scheduled_time)}
                        </p>
                      </div>
                    </div>
                    <Badge variant={getStatusBadgeVariant(post.status)}>
                      {post.status_display || post.status}
                    </Badge>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Generated Posters */}
      <Card className="textile-hover textile-shadow">
        <CardHeader>
          <CardTitle className="flex items-center">
            <ImageIcon className="mr-2 h-5 w-5 text-chart-1" />
            Generated Posters - Ready to Schedule
          </CardTitle>
        </CardHeader>
        <CardContent>
          {generatedPosters.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <ImageIcon className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No generated posters yet</p>
              <p className="text-sm mt-2">Generate posters first to schedule them</p>
            </div>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
              {generatedPosters.map((poster) => (
                <div key={poster.id} className="border border-border rounded-lg overflow-hidden hover:shadow-md transition-shadow">
                  <div className="aspect-square bg-muted relative">
                    <img
                      src={poster.image_url}
                      alt={poster.caption}
                      className="w-full h-full object-cover"
                      onError={(e) => {
                        const target = e.target as HTMLImageElement
                        target.src = '/placeholder-image.png'
                      }}
                    />
                  </div>
                  <div className="p-4">
                    <p className="text-sm font-medium text-foreground line-clamp-2 mb-2">
                      {poster.caption || poster.prompt.substring(0, 50)}
                    </p>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-muted-foreground">
                        {new Date(poster.created_at).toLocaleDateString()}
                      </span>
                      <Button
                        size="sm"
                        onClick={() => handleSchedulePoster(poster)}
                        className="bg-textile-accent hover:bg-textile-accent/90 text-xs px-2 py-1 h-7"
                      >
                        <Clock className="mr-1 h-3 w-3" />
                        Schedule
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Schedule Modal */}
      <Dialog open={showScheduleModal} onOpenChange={setShowScheduleModal}>
        <DialogContent className="max-w-2xl">
          <DialogClose onClose={() => setShowScheduleModal(false)} />
          <DialogHeader>
            <DialogTitle>Schedule Post</DialogTitle>
            <DialogDescription>
              Choose when and where to publish this post
            </DialogDescription>
          </DialogHeader>
          
          {selectedPoster && (
            <div className="space-y-4">
              {/* Poster Preview */}
              <div className="border border-border rounded-lg p-4">
                <div className="aspect-square w-32 mx-auto bg-muted rounded-lg overflow-hidden">
                  <img
                    src={selectedPoster.image_url}
                    alt={selectedPoster.caption}
                    className="w-full h-full object-cover"
                  />
                </div>
              </div>

              {/* Platform Selection */}
              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Platform
                </label>
                <select
                  value={scheduleData.platform}
                  onChange={(e) => setScheduleData({ ...scheduleData, platform: e.target.value })}
                  className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground"
                >
                  <option value="instagram">Instagram</option>
                  <option value="facebook">Facebook</option>
                  <option value="twitter">Twitter</option>
                  <option value="linkedin">LinkedIn</option>
                  <option value="tiktok">TikTok</option>
                  <option value="whatsapp">WhatsApp</option>
                </select>
              </div>

              {/* Scheduled Time */}
              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Scheduled Time *
                </label>
                <input
                  type="datetime-local"
                  value={scheduleData.scheduledTime}
                  onChange={(e) => setScheduleData({ ...scheduleData, scheduledTime: e.target.value })}
                  className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground"
                  min={new Date().toISOString().slice(0, 16)}
                  required
                />
              </div>

              {/* Caption */}
              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Caption *
                </label>
                <textarea
                  value={scheduleData.caption}
                  onChange={(e) => setScheduleData({ ...scheduleData, caption: e.target.value })}
                  className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground min-h-[100px]"
                  placeholder="Enter post caption..."
                  required
                />
                {selectedPoster.hashtags && selectedPoster.hashtags.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-2">
                    {selectedPoster.hashtags.slice(0, 5).map((tag, idx) => (
                      <Badge key={idx} variant="outline" className="text-xs">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setShowScheduleModal(false)}
              disabled={scheduling}
            >
              Cancel
            </Button>
            <Button
              onClick={handleScheduleSubmit}
              disabled={scheduling || !scheduleData.scheduledTime || !scheduleData.caption.trim()}
              className="bg-textile-accent hover:bg-textile-accent/90"
            >
              {scheduling ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Scheduling...
                </>
              ) : (
                <>
                  <Clock className="mr-2 h-4 w-4" />
                  Schedule Post
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
