"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog"
import { Image, Calendar, Download, ExternalLink, Loader2, Trash2 } from "lucide-react"
import { useAuth } from "@/hooks/useAuth"
import { useToastHelpers } from "@/components/common"
import { useRouter } from "next/navigation"

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
}

interface SavedPostersProps {
  limit?: number
}

export function SavedPosters({ limit }: SavedPostersProps) {
  const [posters, setPosters] = useState<Poster[]>([])
  const [loading, setLoading] = useState(true)
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [posterToDelete, setPosterToDelete] = useState<Poster | null>(null)
  const [isDeleting, setIsDeleting] = useState(false)
  const router = useRouter()
  const { getToken } = useAuth()
  const { showError } = useToastHelpers()

  useEffect(() => {
    fetchPosters()
  }, [])

  const fetchPosters = async () => {
    try {
      setLoading(true)
      const token = await getToken()
      const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'
      
      // Ensure URL doesn't have double slashes
      const baseUrl = apiBase.replace(/\/$/, '')
      const url = limit 
        ? `${baseUrl}/api/ai/ai-poster/posters/?limit=${limit}`
        : `${baseUrl}/api/ai/ai-poster/posters/`
      
      console.log('Fetching posters from:', url)
      
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      }
      
      if (token) {
        headers['Authorization'] = `Bearer ${token}`
      }
      
      let response: Response
      try {
        response = await fetch(url, {
          method: 'GET',
          headers,
          credentials: 'include'
        })
      } catch (networkError) {
        // Handle network errors (CORS, connection refused, etc.)
        const networkErrorMessage = networkError instanceof Error 
          ? networkError.message 
          : 'Network error - check if backend is running'
        
        // If it's a network error, don't show error toast, just set empty array
        // This allows the UI to show "No posters" instead of an error
        if (networkErrorMessage.includes('Failed to fetch') || 
            networkErrorMessage.includes('NetworkError') ||
            networkErrorMessage.includes('CORS') ||
            networkErrorMessage.includes('network')) {
          // Only log as warning in development, not as error
          if (process.env.NODE_ENV === 'development') {
            console.warn('Backend may not be accessible, showing empty state:', networkErrorMessage)
          }
          setPosters([])
          setLoading(false)
          return
        }
        // For other errors, still handle gracefully
        console.warn('Error fetching posters:', networkErrorMessage)
        setPosters([])
        setLoading(false)
        return
      }

      console.log('Response status:', response.status, response.statusText)

      // Handle different response scenarios
      if (!response.ok) {
        // Try to get error message from response
        let errorMessage = `Failed to fetch posters (${response.status})`
        let errorData: any = null
        try {
          const text = await response.text()
          if (text) {
            errorData = JSON.parse(text)
            // Extract meaningful error message
            if (errorData.error) {
              errorMessage = errorData.error
            } else if (errorData.message) {
              errorMessage = errorData.message
            } else if (typeof errorData === 'string') {
              errorMessage = errorData
            }
            
            // Check for database errors
            if (errorMessage.includes("doesn't exist") || errorMessage.includes('Table') || errorMessage.includes('database')) {
              console.warn('Database table may not exist. Run migrations:', errorMessage)
              // Don't show error to user, just show empty state
              setPosters([])
              return
            }
            
            // Only log if there's actual error data
            if (Object.keys(errorData).length > 0 && errorData.error) {
              console.error('Error response data:', errorData)
            }
          }
        } catch (e) {
          // If response is not JSON, use status text
          errorMessage = response.statusText || errorMessage
        }
        
        // If it's a 404, 204, or 403 (forbidden but no posters), just set empty array
        if (response.status === 404 || response.status === 204) {
          console.log('No posters found (404/204), setting empty array')
          setPosters([])
          return
        }
        
        // For 403, might be auth issue but could also mean no access to posters
        if (response.status === 403) {
          console.log('Access forbidden (403), setting empty array')
          setPosters([])
          return
        }
        
        // For database errors (500 with table doesn't exist), show empty state
        if (response.status >= 500) {
          // Check if it's a database migration issue
          if (errorMessage.includes("doesn't exist") || errorMessage.includes('Table') || errorMessage.includes('database')) {
            console.warn('Database migration needed. Showing empty state:', errorMessage)
            setPosters([])
            return
          }
          // Only throw for other server errors
          throw new Error(errorMessage)
        } else {
          // For client errors (4xx), just set empty array
          console.warn('Client error (4xx), setting empty array:', errorMessage)
          setPosters([])
          return
        }
      }

      // Parse response
      let data: any
      try {
        const text = await response.text()
        if (!text) {
          console.log('Empty response, setting empty array')
          setPosters([])
          return
        }
        data = JSON.parse(text)
      } catch (parseError) {
        console.error('Failed to parse response as JSON:', parseError)
        setPosters([])
        return
      }
      
      console.log('Posters response data:', data)
      
      // Handle different response formats
      if (data.success && data.results) {
        // Ensure image URLs are absolute
        const postersWithFixedUrls = data.results.map((poster: Poster) => {
          if (poster.image_url && !poster.image_url.startsWith('http')) {
            const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'
            const baseUrl = apiBase.replace(/\/$/, '')
            poster.image_url = poster.image_url.startsWith('/') 
              ? `${baseUrl}${poster.image_url}`
              : `${baseUrl}/${poster.image_url}`
          }
          return poster
        })
        console.log('Posters with fixed URLs:', postersWithFixedUrls.map((p: Poster) => ({ id: p.id, image_url: p.image_url })))
        setPosters(postersWithFixedUrls)
      } else if (Array.isArray(data)) {
        // If response is directly an array
        const postersWithFixedUrls = data.map((poster: Poster) => {
          if (poster.image_url && !poster.image_url.startsWith('http')) {
            const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'
            const baseUrl = apiBase.replace(/\/$/, '')
            poster.image_url = poster.image_url.startsWith('/') 
              ? `${baseUrl}${poster.image_url}`
              : `${baseUrl}/${poster.image_url}`
          }
          return poster
        })
        setPosters(postersWithFixedUrls)
      } else if (data.results && Array.isArray(data.results)) {
        // If results exist but success flag might be missing
        const postersWithFixedUrls = data.results.map((poster: Poster) => {
          if (poster.image_url && !poster.image_url.startsWith('http')) {
            const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'
            const baseUrl = apiBase.replace(/\/$/, '')
            poster.image_url = poster.image_url.startsWith('/') 
              ? `${baseUrl}${poster.image_url}`
              : `${baseUrl}/${poster.image_url}`
          }
          return poster
        })
        setPosters(postersWithFixedUrls)
      } else if (data.success === false) {
        // If API explicitly returns success: false, check if there's an error
        if (data.error) {
          console.warn('API returned error:', data.error)
        }
        setPosters([])
      } else {
        console.warn('Unexpected response format:', data)
        setPosters([])
      }
    } catch (error) {
      console.error('Error fetching posters:', error)
      // Only show error toast for unexpected errors, not for empty results
      const errorMessage = error instanceof Error ? error.message : 'Failed to load saved posters'
      // Don't show error for network issues - they're handled above
      if (!errorMessage.includes('Network') && !errorMessage.includes('Failed to fetch')) {
        showError(errorMessage)
      }
      setPosters([])
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString)
      // Check if date is valid
      if (isNaN(date.getTime())) {
        return 'Invalid date'
      }
      const now = new Date()
      const diffTime = Math.abs(now.getTime() - date.getTime())
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
      
      // Show relative time for recent dates
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
        // For older dates, show full date
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
    } catch (error) {
      console.error('Error downloading poster:', error)
      showError('Failed to download poster')
    }
  }

  const handleDeleteClick = (poster: Poster) => {
    setPosterToDelete(poster)
    setDeleteDialogOpen(true)
  }

  const handleDeleteConfirm = async () => {
    if (!posterToDelete) return

    setIsDeleting(true)
    try {
      const token = await getToken()
      const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'
      const baseUrl = apiBase.replace(/\/$/, '')
      
      const response = await fetch(`${baseUrl}/api/ai/ai-poster/posters/${posterToDelete.id}/delete/`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        },
        credentials: 'include'
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: 'Failed to delete poster' }))
        throw new Error(errorData.error || 'Failed to delete poster')
      }

      // Remove the poster from the list
      setPosters(prev => prev.filter(p => p.id !== posterToDelete.id))
      setDeleteDialogOpen(false)
      setPosterToDelete(null)
    } catch (error) {
      console.error('Error deleting poster:', error)
      showError(error instanceof Error ? error.message : 'Failed to delete poster')
    } finally {
      setIsDeleting(false)
    }
  }

  const handleDeleteCancel = () => {
    setDeleteDialogOpen(false)
    setPosterToDelete(null)
  }

  const handlePosterClick = (poster: Poster) => {
    router.push(`/dashboard/posters/${poster.id}`)
  }

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Recent Posters</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-64">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        </CardContent>
      </Card>
    )
  }

  if (posters.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Recent Posters</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center h-64 text-center">
            <Image className="h-12 w-12 text-muted-foreground mb-4" />
            <p className="text-muted-foreground mb-2">No posters generated yet</p>
            <p className="text-sm text-muted-foreground">Create your first poster to see it here</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="textile-hover textile-shadow">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center">
            <Image className="mr-2 h-5 w-5 text-chart-1" />
            Generated Posters
          </div>
          <Badge variant="secondary" className="text-xs">
            {posters.length} {posters.length === 1 ? 'poster' : 'posters'}
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
          {posters.map((poster) => (
            <div
              key={poster.id}
              className="group relative bg-card rounded-lg overflow-hidden border border-border hover:border-primary hover:shadow-lg transition-all"
            >
              {/* Image Container - Clickable */}
              <div 
                className="aspect-square bg-muted overflow-hidden relative cursor-pointer"
                onClick={() => handlePosterClick(poster)}
              >
                {poster.image_url ? (
                  <img
                    src={poster.image_url}
                    alt={poster.caption || poster.prompt || 'Generated poster'}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    onError={(e) => {
                      const target = e.target as HTMLImageElement
                      // Try to fix relative URLs
                      if (poster.image_url && !poster.image_url.startsWith('http')) {
                        const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'
                        const baseUrl = apiBase.replace(/\/$/, '')
                        const fixedUrl = poster.image_url.startsWith('/') 
                          ? `${baseUrl}${poster.image_url}`
                          : `${baseUrl}/${poster.image_url}`
                        target.src = fixedUrl
                      } else {
                        // Fallback to placeholder
                        target.style.display = 'none'
                        const placeholder = target.parentElement?.querySelector('.image-placeholder')
                        if (placeholder) {
                          (placeholder as HTMLElement).style.display = 'flex'
                        }
                      }
                    }}
                    loading="lazy"
                  />
                ) : null}
                {/* Placeholder when image fails to load */}
                <div className="image-placeholder absolute inset-0 flex items-center justify-center bg-muted" style={{ display: poster.image_url ? 'none' : 'flex' }}>
                  <Image className="h-12 w-12 text-muted-foreground opacity-50" />
                </div>
              </div>
              
              {/* Info Overlay - Always Visible */}
              <div className="p-3 space-y-2" onClick={(e) => e.stopPropagation()}>
                {/* Caption */}
                <div>
                  <p className="text-xs font-medium text-foreground line-clamp-2 mb-1">
                    {poster.caption || poster.full_caption || poster.prompt || 'No caption'}
                  </p>
                  {poster.prompt && poster.prompt !== poster.caption && (
                    <p className="text-xs text-muted-foreground line-clamp-1">
                      Prompt: {poster.prompt}
                    </p>
                  )}
                </div>

                {/* Date */}
                <div className="flex items-center text-xs text-muted-foreground mb-2">
                  <Calendar className="h-3 w-3 mr-1" />
                  {formatDate(poster.created_at)}
                </div>

                {/* Action Buttons */}
                <div className="flex gap-1.5 pt-2 border-t border-border" onClick={(e) => e.stopPropagation()}>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleDownload(poster)}
                    className="flex-1 h-7 text-xs px-2"
                  >
                    <Download className="h-3 w-3 mr-1" />
                    Download
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => window.open(poster.image_url, '_blank')}
                    className="h-7 w-7 p-0 flex-shrink-0"
                    title="Open in new tab"
                  >
                    <ExternalLink className="h-3 w-3" />
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleDeleteClick(poster)}
                    className="h-7 w-7 p-0 flex-shrink-0 text-destructive hover:text-destructive hover:bg-destructive/10"
                    title="Delete"
                  >
                    <Trash2 className="h-3 w-3" />
                  </Button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent className="bg-card border-border">
          <DialogHeader>
            <DialogTitle>Delete Poster</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete this poster? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={handleDeleteCancel}
              disabled={isDeleting}
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleDeleteConfirm}
              disabled={isDeleting}
            >
              {isDeleting ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Deleting...
                </>
              ) : (
                'Delete'
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </Card>
  )
}

