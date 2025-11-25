"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter, DialogClose } from "@/components/ui/dialog"
import { Calendar, Plus, Clock, Image as ImageIcon, Loader2, Edit, Trash2 } from "lucide-react"
import { useAuth } from "@/hooks/useAuth"
import { useToastHelpers, ConfirmationModal } from "@/components/common"

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
      
      console.log('Fetching posters from:', url)
      
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      }
      
      if (token) {
        headers['Authorization'] = `Bearer ${token}`
      }

      // Add organization context headers
      try {
        const orgSlug = (typeof window !== 'undefined' ? window.localStorage.getItem('organizationSlug') : null) 
          || process.env.NEXT_PUBLIC_ORGANIZATION_SLUG 
          || null
        if (orgSlug) {
          headers['X-Organization'] = orgSlug
        }
        const devOrgId = (typeof window !== 'undefined' ? window.localStorage.getItem('devOrgId') : null)
          || process.env.NEXT_PUBLIC_DEV_ORG_ID 
          || null
        if (devOrgId) {
          headers['X-Dev-Org-Id'] = devOrgId
        }
      } catch {}
      
      let response: Response
      try {
        response = await fetch(url, {
          method: 'GET',
          headers,
          credentials: 'include',
          mode: 'cors', // Explicitly set CORS mode
        })
      } catch (networkError) {
        // Handle network errors gracefully
        console.error('Network error fetching posters:', networkError)
        const errorMsg = networkError instanceof Error ? networkError.message : 'Network error'
        
        // Check if it's a CORS error
        if (errorMsg.includes('CORS') || errorMsg.includes('Failed to fetch')) {
          console.error('CORS or network error - backend might not be running on', baseUrl)
        }
        setGeneratedPosters([])
        return
      }

      if (!response.ok) {
        if (response.status === 404 || response.status === 204) {
          setGeneratedPosters([])
          return
        }
        
        // Try to get error message from response
        let errorMessage = `Failed to fetch posters (${response.status})`
        try {
          const errorData = await response.json()
          if (errorData.error) {
            errorMessage = errorData.error
          } else if (errorData.message) {
            errorMessage = errorData.message
          }
        } catch {
          // If response is not JSON, use status text
          errorMessage = response.statusText || errorMessage
        }
        
        throw new Error(errorMessage)
      }

      const text = await response.text()
      if (!text || text.trim() === '') {
        setGeneratedPosters([])
        return
      }

      let data: any
      try {
        data = JSON.parse(text)
      } catch (parseError) {
        console.error('Failed to parse response:', text)
        throw new Error('Invalid response from server')
      }
      
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
        // Also fix public_url if it exists
        if ((poster as any).public_url && !(poster as any).public_url.startsWith('http')) {
          (poster as any).public_url = (poster as any).public_url.startsWith('/') 
            ? `${baseUrl}${(poster as any).public_url}`
            : `${baseUrl}/${(poster as any).public_url}`
        }
        return poster
      })

      setGeneratedPosters(postersWithFixedUrls)
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
        const orgSlug = (typeof window !== 'undefined' ? window.localStorage.getItem('organizationSlug') : null) 
          || process.env.NEXT_PUBLIC_ORGANIZATION_SLUG 
          || null
        if (orgSlug) {
          headers['X-Organization'] = orgSlug
        }
        const devOrgId = (typeof window !== 'undefined' ? window.localStorage.getItem('devOrgId') : null)
          || process.env.NEXT_PUBLIC_DEV_ORG_ID 
          || null
        if (devOrgId) {
          headers['X-Dev-Org-Id'] = devOrgId
        }
      } catch {}
      
      let response: Response
      try {
        response = await fetch(url, {
          method: 'GET',
          headers,
          credentials: 'include',
          mode: 'cors', // Explicitly set CORS mode
        })
      } catch (networkError) {
        // Handle network errors gracefully
        console.error('Network error fetching scheduled posts:', networkError)
        const errorMsg = networkError instanceof Error ? networkError.message : 'Network error'
        
        // Check if it's a CORS error
        if (errorMsg.includes('CORS') || errorMsg.includes('Failed to fetch')) {
          console.error('CORS or network error - backend might not be running on', baseUrl)
        }
        setScheduledPosts([])
        return
      }

      if (!response.ok) {
        if (response.status === 404 || response.status === 204) {
          setScheduledPosts([])
          return
        }
        
        // Try to get error message from response
        let errorMessage = `Failed to fetch scheduled posts (${response.status})`
        try {
          const errorData = await response.json()
          if (errorData.error) {
            errorMessage = errorData.error
          } else if (errorData.message) {
            errorMessage = errorData.message
          }
        } catch {
          // If response is not JSON, use status text
          errorMessage = response.statusText || errorMessage
        }
        
        throw new Error(errorMessage)
      }

      const text = await response.text()
      if (!text || text.trim() === '') {
        setScheduledPosts([])
        return
      }

      let data: any
      try {
        data = JSON.parse(text)
      } catch (parseError) {
        console.error('Failed to parse response:', text)
        throw new Error('Invalid response from server')
      }
      
      let scheduledData: ScheduledPost[] = []
      if (Array.isArray(data)) {
        scheduledData = data
      } else if (data.results && Array.isArray(data.results)) {
        scheduledData = data.results
      }

      // Filter out cancelled posts (they're "deleted" from user's perspective)
      const activePosts = scheduledData.filter(post => post.status !== 'cancelled')
      setScheduledPosts(activePosts)
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
      const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'
      const baseUrl = apiBase.replace(/\/$/, '')
      const url = `${baseUrl}/api/ai/schedule/${selectedScheduledPost.id}/`
      
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
      
      let response: Response
      try {
        response = await fetch(url, {
          method: 'PATCH',
          headers,
          credentials: 'include',
          body: JSON.stringify(requestBody)
        })
      } catch (networkError) {
        console.error('Network error updating post:', networkError)
        const errorObj = networkError instanceof Error ? networkError : new Error(String(networkError))
        let errorMessage = 'Failed to update post'
        if (errorObj.message === 'Failed to fetch' || errorObj.name === 'TypeError') {
          errorMessage = 'Cannot connect to server. Please ensure the backend is running and accessible.'
        }
        showError(errorMessage)
        return
      }

      if (!response.ok) {
        let errorData: any = {}
        try {
          const text = await response.text()
          if (text) {
            errorData = JSON.parse(text)
          }
        } catch (e) {
          console.error('Failed to parse error response:', e)
        }
        
        let errorMessage = errorData.detail || errorData.error || errorData.message || `Failed to update post (${response.status})`
        if (typeof errorData.detail === 'object' && errorData.detail !== null && !Array.isArray(errorData.detail)) {
          const fieldErrors = Object.entries(errorData.detail)
            .map(([field, error]: [string, any]) => {
              const errorText = Array.isArray(error) ? error[0] : error
              return `${field}: ${errorText}`
            })
            .join(', ')
          errorMessage = fieldErrors || errorMessage
        }
        
        showError(errorMessage)
        return
      }

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
      const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'
      const baseUrl = apiBase.replace(/\/$/, '')
      const url = `${baseUrl}/api/ai/schedule/${postToDelete.id}/`
      
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
      } catch (e) {
        console.error('Error setting organization headers:', e)
      }
      
      let response: Response
      try {
        response = await fetch(url, {
          method: 'DELETE',
          headers,
          credentials: 'include'
        })
      } catch (networkError) {
        console.error('Network error deleting post:', networkError)
        const errorObj = networkError instanceof Error ? networkError : new Error(String(networkError))
        let errorMessage = 'Failed to delete post'
        if (errorObj.message === 'Failed to fetch' || errorObj.name === 'TypeError') {
          errorMessage = 'Cannot connect to server. Please ensure the backend is running and accessible.'
        }
        showError(errorMessage)
        return
      }

      if (!response.ok) {
        let errorData: any = {}
        try {
          const text = await response.text()
          if (text) {
            errorData = JSON.parse(text)
          }
        } catch (e) {
          console.error('Failed to parse error response:', e)
        }
        
        const errorMessage = errorData.detail || errorData.error || errorData.message || `Failed to delete post (${response.status})`
        showError(errorMessage)
        return
      }

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
                    <div className="flex items-center gap-2">
                      <Badge variant={getStatusBadgeVariant(post.status)}>
                        {post.status_display || post.status}
                      </Badge>
                      {/* Only show edit/delete for pending or scheduled posts */}
                      {(post.status === 'pending' || post.status === 'scheduled') && (
                        <>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleEditPost(post)}
                            className="h-8 w-8 p-0"
                            title="Edit post"
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDeleteClick(post)}
                            disabled={deleting === post.id}
                            className="h-8 w-8 p-0 text-destructive hover:text-destructive"
                            title="Delete post"
                          >
                            {deleting === post.id ? (
                              <Loader2 className="h-4 w-4 animate-spin" />
                            ) : (
                              <Trash2 className="h-4 w-4" />
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
                        className="bg-textile-accent hover:bg-textile-accent/90 text-[10px] px-1.5 py-0.5 h-6"
                      >
                        <Clock className="mr-1 h-2.5 w-2.5" />
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

      {/* Edit Modal */}
      <Dialog open={showEditModal} onOpenChange={setShowEditModal}>
        <DialogContent className="max-w-2xl">
          <DialogClose onClose={() => {
            setShowEditModal(false)
            setSelectedScheduledPost(null)
            setScheduleData({
              platform: 'instagram',
              scheduledTime: '',
              caption: ''
            })
          }} />
          <DialogHeader>
            <DialogTitle>Edit Scheduled Post</DialogTitle>
            <DialogDescription>
              Update the post details and scheduled time
            </DialogDescription>
          </DialogHeader>
          
          {selectedScheduledPost && (
            <div className="space-y-4">
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
              </div>
            </div>
          )}

          <DialogFooter>
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
            >
              Cancel
            </Button>
            <Button
              onClick={handleEditSubmit}
              disabled={editing || !scheduleData.scheduledTime || !scheduleData.caption.trim()}
              className="bg-textile-accent hover:bg-textile-accent/90"
            >
              {editing ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Updating...
                </>
              ) : (
                <>
                  <Edit className="mr-2 h-4 w-4" />
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
