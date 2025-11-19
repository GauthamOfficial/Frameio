"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Image, Calendar, Download, ExternalLink, Loader2 } from "lucide-react"
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
}

interface SavedPostersProps {
  limit?: number
}

export function SavedPosters({ limit }: SavedPostersProps) {
  const [posters, setPosters] = useState<Poster[]>([])
  const [loading, setLoading] = useState(true)
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
        console.error('Network error fetching posters:', networkError)
        const networkErrorMessage = networkError instanceof Error 
          ? networkError.message 
          : 'Network error - check if backend is running'
        
        // If it's a network error, don't show error toast, just set empty array
        // This allows the UI to show "No posters" instead of an error
        if (networkErrorMessage.includes('Failed to fetch') || 
            networkErrorMessage.includes('NetworkError') ||
            networkErrorMessage.includes('CORS')) {
          console.warn('Backend may not be accessible, showing empty state')
          setPosters([])
          return
        }
        throw networkError
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
        setPosters(data.results)
      } else if (Array.isArray(data)) {
        // If response is directly an array
        setPosters(data)
      } else if (data.results && Array.isArray(data.results)) {
        // If results exist but success flag might be missing
        setPosters(data.results)
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
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {posters.map((poster) => (
            <div
              key={poster.id}
              className="group relative bg-card rounded-lg overflow-hidden border border-border hover:border-primary hover:shadow-lg transition-all"
            >
              {/* Image Container */}
              <div className="aspect-square bg-muted overflow-hidden">
                <img
                  src={poster.image_url}
                  alt={poster.caption || poster.prompt || 'Generated poster'}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  onError={(e) => {
                    const target = e.target as HTMLImageElement
                    target.src = '/placeholder-image.png'
                  }}
                />
              </div>
              
              {/* Info Overlay - Always Visible */}
              <div className="p-4 space-y-3">
                {/* Caption */}
                <div>
                  <p className="text-sm font-medium text-foreground line-clamp-2 mb-1">
                    {poster.caption || poster.full_caption || poster.prompt || 'No caption'}
                  </p>
                  {poster.prompt && poster.prompt !== poster.caption && (
                    <p className="text-xs text-muted-foreground line-clamp-1">
                      Prompt: {poster.prompt}
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

                {/* Action Buttons */}
                <div className="flex gap-2 pt-2 border-t border-border">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleDownload(poster)}
                    className="flex-1 h-8 text-xs"
                  >
                    <Download className="h-3 w-3 mr-1" />
                    Download
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => window.open(poster.image_url, '_blank')}
                    className="h-8 px-2"
                  >
                    <ExternalLink className="h-3 w-3" />
                  </Button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

