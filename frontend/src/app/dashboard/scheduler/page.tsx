"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter, DialogClose } from "@/components/ui/dialog"
import { Calendar, Clock, Image as ImageIcon, Loader2, Edit, Trash2 } from "lucide-react"
import { useAuth } from "@/hooks/useAuth"
import { useToastHelpers, ConfirmationModal } from "@/components/common"
import { apiGet, apiPost, apiPatch, apiDelete, getFullUrl } from "@/utils/api"

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
  metadata?: {
    poster_id?: string
    hashtags?: string[]
    prompt?: string
    aspect_ratio?: string
  }
}

export default function SchedulerPage() {
  const [generatedPosters, setGeneratedPosters] = useState<GeneratedPoster[]>([])
  const [scheduledPosts, setScheduledPosts] = useState<ScheduledPost[]>([])
  const [loading, setLoading] = useState(true)
  const [scheduling, setScheduling] = useState(false)
  const [showScheduleModal, setShowScheduleModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [selectedPoster, setSelectedPoster] = useState<GeneratedPoster | null>(null)
  const [selectedScheduledPost, setSelectedScheduledPost] = useState<ScheduledPost | null>(null)
  const [editing, setEditing] = useState(false)
  const [deleting, setDeleting] = useState<string | null>(null)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [postToDelete, setPostToDelete] = useState<ScheduledPost | null>(null)
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
        try {
          const data = await apiGet('/api/users/', {}, token) as Array<{ current_organization?: string }> | { current_organization?: string }
          const user = Array.isArray(data) ? data[0] : data
          if (user?.current_organization) {
            // Store for future use
            if (typeof window !== 'undefined') {
              window.localStorage.setItem('devOrgId', user.current_organization)
            }
            return { devOrgId: user.current_organization }
          }
        } catch (e) {
          console.warn('Failed to fetch user profile:', e)
        }
      }
    } catch (e) {
      console.warn('Failed to get organization context from user profile:', e)
    }
    return { orgSlug: null, devOrgId: null }
  }

  useEffect(() => {
    fetchData()
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const fetchData = async () => {
    await Promise.all([fetchPosters(), fetchScheduledPosts()])
  }

  const fetchPosters = async () => {
    try {
      const token = await getToken()
      const url = '/api/ai/ai-poster/posters/'
      
      console.log('Fetching posters from:', url)
      
      // Build custom headers for organization context
      const customHeaders: Record<string, string> = {}
      try {
        const orgSlug = (typeof window !== 'undefined' ? window.localStorage.getItem('organizationSlug') : null) 
          || process.env.NEXT_PUBLIC_ORGANIZATION_SLUG 
          || null
        if (orgSlug) {
          customHeaders['X-Organization'] = orgSlug
        }
        const devOrgId = (typeof window !== 'undefined' ? window.localStorage.getItem('devOrgId') : null)
          || process.env.NEXT_PUBLIC_DEV_ORG_ID 
          || null
        if (devOrgId) {
          customHeaders['X-Dev-Org-Id'] = devOrgId
        }
      } catch {}
      
      try {
        const data = await apiGet(url, { headers: customHeaders, credentials: 'include', mode: 'cors' }, token) as { success?: boolean; results?: GeneratedPoster[] } | GeneratedPoster[]
        
        let postersData: GeneratedPoster[] = []
        if (Array.isArray(data)) {
          postersData = data
        } else if (data.success && data.results && Array.isArray(data.results)) {
          postersData = data.results
        } else if ('results' in data && Array.isArray(data.results)) {
          postersData = data.results
        }

        // Ensure image URLs are absolute
        const postersWithFixedUrls = postersData.map((poster: GeneratedPoster) => {
          if (poster.image_url && !poster.image_url.startsWith('http')) {
            poster.image_url = getFullUrl(poster.image_url)
          }
          // Also fix public_url if it exists
          const posterWithUrl = poster as GeneratedPoster & { public_url?: string };
          if (posterWithUrl.public_url && !posterWithUrl.public_url.startsWith('http')) {
            posterWithUrl.public_url = getFullUrl(posterWithUrl.public_url)
          }
          return poster
        })

        setGeneratedPosters(postersWithFixedUrls)
      } catch (networkError) {
        // Handle network errors gracefully
        console.error('Network error fetching posters:', networkError)
        const errorMsg = networkError instanceof Error ? networkError.message : 'Network error'
        
        if (errorMsg.includes('CORS') || errorMsg.includes('Failed to fetch')) {
          console.error('CORS or network error - backend might not be accessible')
        }
        setGeneratedPosters([])
        return
      }
    } catch (error) {
      console.error('Error fetching posters:', error)
      const errorMessage = error instanceof Error ? error.message : 'Failed to load posters'
      
      // Only log errors that aren't network/CORS related (those are handled above)
      if (!errorMessage.includes('Network') && 
          !errorMessage.includes('Failed to fetch') && 
          !errorMessage.includes('Cannot connect')) {
        console.error('Poster fetch error:', errorMessage)
      }
      setGeneratedPosters([])
    } finally {
      setLoading(false)
    }
  }

  const fetchScheduledPosts = async () => {
    try {
      const token = await getToken()
      const url = '/api/ai/schedule/'
      
      // Build custom headers for organization context
      const customHeaders: Record<string, string> = {}
      try {
        const orgSlug = (typeof window !== 'undefined' ? window.localStorage.getItem('organizationSlug') : null) 
          || process.env.NEXT_PUBLIC_ORGANIZATION_SLUG 
          || null
        if (orgSlug) {
          customHeaders['X-Organization'] = orgSlug
        }
        const devOrgId = (typeof window !== 'undefined' ? window.localStorage.getItem('devOrgId') : null)
          || process.env.NEXT_PUBLIC_DEV_ORG_ID 
          || null
        if (devOrgId) {
          customHeaders['X-Dev-Org-Id'] = devOrgId
        }
      } catch {}
      
      try {
        const data = await apiGet(url, { headers: customHeaders, credentials: 'include', mode: 'cors' }, token) as ScheduledPost[] | { results?: ScheduledPost[] }
        
        let scheduledData: ScheduledPost[] = []
        if (Array.isArray(data)) {
          scheduledData = data
        } else if (data.results && Array.isArray(data.results)) {
          scheduledData = data.results
        }

        // Filter out cancelled posts (they're "deleted" from user's perspective)
        const activePosts = scheduledData.filter(post => post.status !== 'cancelled')
        setScheduledPosts(activePosts)
      } catch (networkError) {
        // Handle network errors gracefully
        console.error('Network error fetching scheduled posts:', networkError)
        const errorMsg = networkError instanceof Error ? networkError.message : 'Network error'
        
        if (errorMsg.includes('CORS') || errorMsg.includes('Failed to fetch')) {
          console.error('CORS or network error - backend might not be accessible')
        }
        setScheduledPosts([])
        return
      }
    } catch (error) {
      console.error('Error fetching scheduled posts:', error)
      const errorMessage = error instanceof Error ? error.message : 'Failed to load scheduled posts'
      
      // Only log errors that aren't network/CORS related (those are handled above)
      if (!errorMessage.includes('Network') && 
          !errorMessage.includes('Failed to fetch') && 
          !errorMessage.includes('Cannot connect')) {
        console.error('Scheduled posts fetch error:', errorMessage)
      }
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
      const url = '/api/ai/schedule/'
      
      // Build custom headers for organization context
      const customHeaders: Record<string, string> = {}
      try {
        const orgContext = await getOrganizationContext()
        const orgSlug = orgContext.orgSlug || process.env.NEXT_PUBLIC_ORGANIZATION_SLUG
        const devOrgId = orgContext.devOrgId || process.env.NEXT_PUBLIC_DEV_ORG_ID
        
        if (orgSlug) {
          customHeaders['X-Organization'] = orgSlug
        }
        if (devOrgId) {
          customHeaders['X-Dev-Org-Id'] = devOrgId
        }
      } catch (e) {
        console.error('Error setting organization headers:', e)
      }

      // Ensure asset_url is an absolute URL
      let assetUrl = selectedPoster.public_url || selectedPoster.image_url
      if (assetUrl && !assetUrl.startsWith('http')) {
        assetUrl = getFullUrl(assetUrl)
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
      
      await apiPost(url, requestBody, { headers: customHeaders, credentials: 'include' }, token)
      
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

  const handleEditPost = (post: ScheduledPost) => {
    setSelectedScheduledPost(post)
    // Convert scheduled_time to local datetime format for input
    const scheduledDate = new Date(post.scheduled_time)
    const localDateTime = new Date(scheduledDate.getTime() - scheduledDate.getTimezoneOffset() * 60000)
      .toISOString()
      .slice(0, 16)
    
    setScheduleData({
      platform: post.platform,
      scheduledTime: localDateTime,
      caption: post.caption
    })
    setShowEditModal(true)
  }

  const handleEditSubmit = async () => {
    if (!selectedScheduledPost) return
    
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

    setEditing(true)
    try {
      const token = await getToken()
      const url = `/api/ai/schedule/${selectedScheduledPost.id}/`
      
      // Build custom headers for organization context
      const customHeaders: Record<string, string> = {}
      try {
        const orgContext = await getOrganizationContext()
        const orgSlug = orgContext.orgSlug || process.env.NEXT_PUBLIC_ORGANIZATION_SLUG
        const devOrgId = orgContext.devOrgId || process.env.NEXT_PUBLIC_DEV_ORG_ID
        
        if (orgSlug) {
          customHeaders['X-Organization'] = orgSlug
        }
        if (devOrgId) {
          customHeaders['X-Dev-Org-Id'] = devOrgId
        }
      } catch (e) {
        console.error('Error setting organization headers:', e)
      }

      const requestBody = {
        platform: scheduleData.platform,
        asset_url: selectedScheduledPost.asset_url,
        caption: scheduleData.caption,
        scheduled_time: scheduledDate.toISOString(),
        metadata: selectedScheduledPost.metadata || {}
      }
      
      await apiPatch(url, requestBody, { headers: customHeaders, credentials: 'include' }, token)
      
      showSuccess("Post updated successfully!")
      setShowEditModal(false)
      setSelectedScheduledPost(null)
      setScheduleData({
        platform: 'instagram',
        scheduledTime: '',
        caption: ''
      })
      
      // Refresh scheduled posts
      await fetchScheduledPosts()
    } catch (error) {
      console.error('Error updating post:', error)
      const errorMessage = error instanceof Error ? error.message : 'Failed to update post'
      showError(errorMessage)
    } finally {
      setEditing(false)
    }
  }

  const handleDeleteClick = (post: ScheduledPost) => {
    setPostToDelete(post)
    setShowDeleteConfirm(true)
  }

  const handleDeleteConfirm = async () => {
    if (!postToDelete) return

    setDeleting(postToDelete.id)
    setShowDeleteConfirm(false)
    try {
      const token = await getToken()
      const url = `/api/ai/schedule/${postToDelete.id}/`
      
      // Build custom headers for organization context
      const customHeaders: Record<string, string> = {}
      try {
        const orgContext = await getOrganizationContext()
        const orgSlug = orgContext.orgSlug || process.env.NEXT_PUBLIC_ORGANIZATION_SLUG
        const devOrgId = orgContext.devOrgId || process.env.NEXT_PUBLIC_DEV_ORG_ID
        
        if (orgSlug) {
          customHeaders['X-Organization'] = orgSlug
        }
        if (devOrgId) {
          customHeaders['X-Dev-Org-Id'] = devOrgId
        }
      } catch (e) {
        console.error('Error setting organization headers:', e)
      }
      
      await apiDelete(url, { headers: customHeaders, credentials: 'include' }, token)
      
      showSuccess("Post deleted successfully!")
      
      // Refresh scheduled posts
      await fetchScheduledPosts()
    } catch (error) {
      console.error('Error deleting post:', error)
      const errorMessage = error instanceof Error ? error.message : 'Failed to delete post'
      showError(errorMessage)
    } finally {
      setDeleting(null)
      setPostToDelete(null)
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
    <div className="space-y-4 sm:space-y-6 md:space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-foreground">Social Media Scheduler</h1>
          <p className="text-sm sm:text-base text-muted-foreground mt-1">
            Plan and schedule your textile marketing posts across platforms.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:gap-6 md:gap-8">
        {/* Calendar View - Scheduled Posts */}
        <Card className="textile-hover textile-shadow">
          <CardHeader className="p-4 sm:p-6">
            <CardTitle className="flex items-center text-lg sm:text-xl">
              <Calendar className="mr-2 h-4 w-4 sm:h-5 sm:w-5 text-chart-1 shrink-0" />
              Scheduled Posts
            </CardTitle>
          </CardHeader>
          <CardContent className="p-4 sm:p-6">
            {scheduledPosts.length === 0 ? (
              <div className="text-center py-6 sm:py-8 text-muted-foreground px-4">
                <Calendar className="h-10 w-10 sm:h-12 sm:w-12 mx-auto mb-3 sm:mb-4 opacity-50" />
                <p className="text-sm sm:text-base">No scheduled posts yet</p>
                <p className="text-xs sm:text-sm mt-2">Schedule a post from your generated posters below</p>
              </div>
            ) : (
              <div className="space-y-3 sm:space-y-4">
                {scheduledPosts.map((post) => (
                  <div key={post.id} className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 sm:gap-4 p-3 sm:p-4 border border-border rounded-lg">
                    <div className="flex items-start sm:items-center space-x-3 sm:space-x-4 flex-1 min-w-0">
                      <div className="w-8 h-8 sm:w-10 sm:h-10 bg-chart-1 rounded-lg flex items-center justify-center flex-shrink-0">
                        <Calendar className="h-4 w-4 sm:h-5 sm:w-5 text-white" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-sm sm:text-base text-foreground line-clamp-2 sm:truncate">{post.caption.substring(0, 50)}...</p>
                        <p className="text-xs sm:text-sm text-muted-foreground mt-1">
                          {formatTime(post.scheduled_time)} • {post.platform_display || post.platform}
                        </p>
                        <p className="text-xs text-muted-foreground mt-1">
                          {formatDateTime(post.scheduled_time)}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 sm:gap-2 flex-shrink-0">
                      <Badge variant={getStatusBadgeVariant(post.status)} className="text-xs">
                        {post.status_display || post.status}
                      </Badge>
                      {/* Only show edit/delete for pending or scheduled posts */}
                      {(post.status === 'pending' || post.status === 'scheduled') && (
                        <>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleEditPost(post)}
                            className="h-7 w-7 sm:h-8 sm:w-8 p-0"
                            title="Edit post"
                          >
                            <Edit className="h-3.5 w-3.5 sm:h-4 sm:w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDeleteClick(post)}
                            disabled={deleting === post.id}
                            className="h-7 w-7 sm:h-8 sm:w-8 p-0 text-destructive hover:text-destructive"
                            title="Delete post"
                          >
                            {deleting === post.id ? (
                              <Loader2 className="h-3.5 w-3.5 sm:h-4 sm:w-4 animate-spin" />
                            ) : (
                              <Trash2 className="h-3.5 w-3.5 sm:h-4 sm:w-4" />
                            )}
                          </Button>
                        </>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Generated Posters */}
      <Card className="textile-hover textile-shadow">
        <CardHeader className="p-4 sm:p-6">
          <CardTitle className="flex items-center text-lg sm:text-xl">
            <ImageIcon className="mr-2 h-4 w-4 sm:h-5 sm:w-5 text-chart-1 shrink-0" />
            <span className="truncate">Generated Posters - Ready to Schedule</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="p-4 sm:p-6">
          {generatedPosters.length === 0 ? (
            <div className="text-center py-6 sm:py-8 text-muted-foreground px-4">
              <ImageIcon className="h-10 w-10 sm:h-12 sm:w-12 mx-auto mb-3 sm:mb-4 opacity-50" />
              <p className="text-sm sm:text-base">No generated posters yet</p>
              <p className="text-xs sm:text-sm mt-2">Generate posters first to schedule them</p>
            </div>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3 sm:gap-4">
              {generatedPosters.map((poster) => (
                <div key={poster.id} className="border border-border rounded-lg overflow-hidden hover:shadow-md transition-shadow">
                  <div className="aspect-square bg-muted relative">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
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
                  <div className="p-2 sm:p-3 md:p-4">
                    <p className="text-xs sm:text-sm font-medium text-foreground line-clamp-2 mb-2">
                      {poster.caption || poster.prompt.substring(0, 50)}
                    </p>
                    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                      <span className="text-xs text-muted-foreground">
                        {new Date(poster.created_at).toLocaleDateString()}
                      </span>
                      <Button
                        size="sm"
                        onClick={() => handleSchedulePoster(poster)}
                        className="bg-textile-accent hover:bg-textile-accent/90 text-xs sm:text-sm px-2 sm:px-3 py-1 sm:py-1.5 h-7 sm:h-8 w-full sm:w-auto"
                      >
                        <Clock className="mr-1 h-3 w-3 sm:h-3.5 sm:w-3.5 shrink-0" />
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
        <DialogContent className="max-w-2xl w-[95vw] sm:w-full max-h-[90vh] overflow-y-auto">
          <DialogClose onClose={() => setShowScheduleModal(false)} />
          <DialogHeader className="px-4 sm:px-6 pt-4 sm:pt-6">
            <DialogTitle className="text-lg sm:text-xl">Schedule Post</DialogTitle>
            <DialogDescription className="text-sm">
              Choose when and where to publish this post
            </DialogDescription>
          </DialogHeader>
          
          {selectedPoster && (
            <div className="space-y-3 sm:space-y-4 px-4 sm:px-6">
              {/* Poster Preview */}
              <div className="border border-border rounded-lg p-3 sm:p-4">
                <div className="aspect-square w-24 sm:w-32 mx-auto bg-muted rounded-lg overflow-hidden">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={selectedPoster.image_url}
                    alt={selectedPoster.caption}
                    className="w-full h-full object-cover"
                  />
                </div>
              </div>

              {/* Platform Selection */}
              <div>
                <label htmlFor="schedule-platform" className="block text-xs sm:text-sm font-medium text-foreground mb-2">
                  Platform
                </label>
                <select
                  id="schedule-platform"
                  value={scheduleData.platform}
                  onChange={(e) => setScheduleData({ ...scheduleData, platform: e.target.value })}
                  className="w-full px-3 py-2 text-sm sm:text-base border border-border rounded-lg bg-background text-foreground"
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
                <label htmlFor="schedule-time" className="block text-xs sm:text-sm font-medium text-foreground mb-2">
                  Scheduled Time *
                </label>
                <input
                  id="schedule-time"
                  type="datetime-local"
                  value={scheduleData.scheduledTime}
                  onChange={(e) => setScheduleData({ ...scheduleData, scheduledTime: e.target.value })}
                  className="w-full px-3 py-2 text-sm sm:text-base border border-border rounded-lg bg-background text-foreground"
                  min={new Date().toISOString().slice(0, 16)}
                  required
                />
              </div>

              {/* Caption */}
              <div>
                <label htmlFor="schedule-caption" className="block text-xs sm:text-sm font-medium text-foreground mb-2">
                  Caption *
                </label>
                <textarea
                  id="schedule-caption"
                  value={scheduleData.caption}
                  onChange={(e) => setScheduleData({ ...scheduleData, caption: e.target.value })}
                  className="w-full px-3 py-2 text-sm sm:text-base border border-border rounded-lg bg-background text-foreground min-h-[100px]"
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

          <DialogFooter className="px-4 sm:px-6 pb-4 sm:pb-6 flex-col sm:flex-row gap-2 sm:gap-0">
            <Button
              variant="outline"
              onClick={() => setShowScheduleModal(false)}
              disabled={scheduling}
              className="w-full sm:w-auto text-sm sm:text-base"
            >
              Cancel
            </Button>
            <Button
              onClick={handleScheduleSubmit}
              disabled={scheduling || !scheduleData.scheduledTime || !scheduleData.caption.trim()}
              className="bg-textile-accent hover:bg-textile-accent/90 w-full sm:w-auto text-sm sm:text-base"
            >
              {scheduling ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin shrink-0" />
                  Scheduling...
                </>
              ) : (
                <>
                  <Clock className="mr-2 h-4 w-4 shrink-0" />
                  Schedule Post
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Edit Modal */}
      <Dialog open={showEditModal} onOpenChange={setShowEditModal}>
        <DialogContent className="max-w-2xl w-[95vw] sm:w-full max-h-[90vh] overflow-y-auto">
          <DialogClose onClose={() => {
            setShowEditModal(false)
            setSelectedScheduledPost(null)
            setScheduleData({
              platform: 'instagram',
              scheduledTime: '',
              caption: ''
            })
          }} />
          <DialogHeader className="px-4 sm:px-6 pt-4 sm:pt-6">
            <DialogTitle className="text-lg sm:text-xl">Edit Scheduled Post</DialogTitle>
            <DialogDescription className="text-sm">
              Update the post details and scheduled time
            </DialogDescription>
          </DialogHeader>
          
          {selectedScheduledPost && (
            <div className="space-y-3 sm:space-y-4 px-4 sm:px-6">
              {/* Platform Selection */}
              <div>
                <label className="block text-xs sm:text-sm font-medium text-foreground mb-2">
                  Platform
                </label>
                <select
                  value={scheduleData.platform}
                  onChange={(e) => setScheduleData({ ...scheduleData, platform: e.target.value })}
                  className="w-full px-3 py-2 text-sm sm:text-base border border-border rounded-lg bg-background text-foreground"
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
                <label className="block text-xs sm:text-sm font-medium text-foreground mb-2">
                  Scheduled Time *
                </label>
                <input
                  type="datetime-local"
                  value={scheduleData.scheduledTime}
                  onChange={(e) => setScheduleData({ ...scheduleData, scheduledTime: e.target.value })}
                  className="w-full px-3 py-2 text-sm sm:text-base border border-border rounded-lg bg-background text-foreground"
                  min={new Date().toISOString().slice(0, 16)}
                  required
                />
              </div>

              {/* Caption */}
              <div>
                <label className="block text-xs sm:text-sm font-medium text-foreground mb-2">
                  Caption *
                </label>
                <textarea
                  value={scheduleData.caption}
                  onChange={(e) => setScheduleData({ ...scheduleData, caption: e.target.value })}
                  className="w-full px-3 py-2 text-sm sm:text-base border border-border rounded-lg bg-background text-foreground min-h-[100px]"
                  placeholder="Enter post caption..."
                  required
                />
              </div>
            </div>
          )}

          <DialogFooter className="px-4 sm:px-6 pb-4 sm:pb-6 flex-col sm:flex-row gap-2 sm:gap-0">
            <Button
              variant="outline"
              onClick={() => {
                setShowEditModal(false)
                setSelectedScheduledPost(null)
                setScheduleData({
                  platform: 'instagram',
                  scheduledTime: '',
                  caption: ''
                })
              }}
              disabled={editing}
              className="w-full sm:w-auto text-sm sm:text-base"
            >
              Cancel
            </Button>
            <Button
              onClick={handleEditSubmit}
              disabled={editing || !scheduleData.scheduledTime || !scheduleData.caption.trim()}
              className="bg-textile-accent hover:bg-textile-accent/90 w-full sm:w-auto text-sm sm:text-base"
            >
              {editing ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin shrink-0" />
                  Updating...
                </>
              ) : (
                <>
                  <Edit className="mr-2 h-4 w-4 shrink-0" />
                  Update Post
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Modal */}
      <ConfirmationModal
        isOpen={showDeleteConfirm}
        onClose={() => {
          setShowDeleteConfirm(false)
          setPostToDelete(null)
        }}
        onConfirm={handleDeleteConfirm}
        title="Delete Scheduled Post"
        message="Are you sure you want to delete this scheduled post? This action cannot be undone."
        confirmText="Delete"
        cancelText="Cancel"
        variant="destructive"
        isLoading={deleting !== null}
      />
    </div>
  )
}
