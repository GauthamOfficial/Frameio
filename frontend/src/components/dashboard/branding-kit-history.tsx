"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Palette, Calendar, Download, Loader2, RefreshCw } from "lucide-react"
import { useAuth } from "@/hooks/useAuth"
import { useToastHelpers } from "@/components/common"

interface BrandingKit {
  id: string
  prompt: string
  style: string
  logo: {
    data: string
    format: string
    url?: string
  } | null
  color_palette: {
    data: string
    format: string
    url?: string
  } | null
  colors: string[]
  created_at: string
}

interface BrandingKitHistoryProps {
  limit?: number
}

export function BrandingKitHistory({ limit }: BrandingKitHistoryProps) {
  const [brandingKits, setBrandingKits] = useState<BrandingKit[]>([])
  const [loading, setLoading] = useState(true)
  const { getToken } = useAuth()
  const { showError } = useToastHelpers()

  useEffect(() => {
    fetchBrandingKits()
    
    // Listen for branding kit generation events to refresh the list
    const handleBrandingKitGenerated = () => {
      fetchBrandingKits()
    }
    
    window.addEventListener('branding-kit-generated', handleBrandingKitGenerated)
    
    return () => {
      window.removeEventListener('branding-kit-generated', handleBrandingKitGenerated)
    }
  }, [])

  const fetchBrandingKits = async () => {
    try {
      setLoading(true)
      const token = await getToken()
      const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'
      
      // Ensure URL doesn't have double slashes
      const baseUrl = apiBase.replace(/\/$/, '')
      const url = limit 
        ? `${baseUrl}/api/ai/branding-kit/history/?limit=${limit}`
        : `${baseUrl}/api/ai/branding-kit/history/`
      
      console.log('Fetching branding kits from:', url)
      
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
        console.warn('Backend may not be accessible, showing empty state')
        setBrandingKits([])
        return
      }

      console.log('Response status:', response.status, response.statusText)

      // Handle different response scenarios
      if (!response.ok) {
        if (response.status === 404 || response.status === 204 || response.status === 403) {
          console.log('No branding kits found, setting empty array')
          setBrandingKits([])
          return
        }
        
        if (response.status >= 500) {
          const text = await response.text()
          if (text && (text.includes("doesn't exist") || text.includes('Table') || text.includes('database'))) {
            console.warn('Database migration needed. Showing empty state')
            setBrandingKits([])
            return
          }
        }
        
        throw new Error(`Failed to fetch branding kits (${response.status})`)
      }

      // Parse response
      let data: any
      try {
        const text = await response.text()
        if (!text) {
          console.log('Empty response, setting empty array')
          setBrandingKits([])
          return
        }
        data = JSON.parse(text)
      } catch (parseError) {
        console.error('Failed to parse response as JSON:', parseError)
        setBrandingKits([])
        return
      }
      
      console.log('Branding kits response data:', data)
      console.log('Branding kits count:', data.count || data.results?.length || 0)
      
      // Handle different response formats
      if (data.success && data.results) {
        console.log(`Setting ${data.results.length} branding kits`)
        setBrandingKits(data.results)
      } else if (Array.isArray(data)) {
        console.log(`Setting ${data.length} branding kits (array format)`)
        setBrandingKits(data)
      } else if (data.results && Array.isArray(data.results)) {
        console.log(`Setting ${data.results.length} branding kits (results format)`)
        setBrandingKits(data.results)
      } else if (data.success === false) {
        console.warn('API returned success: false', data.error)
        setBrandingKits([])
      } else {
        console.warn('Unexpected response format:', data)
        setBrandingKits([])
      }
    } catch (error) {
      console.error('Error fetching branding kits:', error)
      const errorMessage = error instanceof Error ? error.message : 'Failed to load branding kit history'
      if (!errorMessage.includes('Network') && !errorMessage.includes('Failed to fetch')) {
        showError(errorMessage)
      }
      setBrandingKits([])
    } finally {
      setLoading(false)
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

  const downloadImage = (base64Data: string, filename: string, format: string) => {
    try {
      const byteCharacters = atob(base64Data)
      const byteNumbers = new Array(byteCharacters.length)
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i)
      }
      const byteArray = new Uint8Array(byteNumbers)
      const blob = new Blob([byteArray], { type: `image/${format.toLowerCase()}` })
      
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Error downloading image:', error)
      showError('Failed to download image')
    }
  }

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Branding Kit History</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-64">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        </CardContent>
      </Card>
    )
  }

  if (brandingKits.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Branding Kit History</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center h-64 text-center">
            <Palette className="h-12 w-12 text-muted-foreground mb-4" />
            <p className="text-muted-foreground mb-2">No branding kits generated yet</p>
            <p className="text-sm text-muted-foreground">Create your first branding kit to see it here</p>
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
            <Palette className="mr-2 h-5 w-5 text-chart-1" />
            Branding Kit History
          </div>
          <div className="flex items-center gap-2">
            <Button
              size="sm"
              variant="ghost"
              onClick={() => fetchBrandingKits()}
              className="h-6 w-6 p-0"
              title="Refresh"
            >
              <RefreshCw className="h-3 w-3" />
            </Button>
            <Badge variant="secondary" className="text-xs">
              {brandingKits.length} {brandingKits.length === 1 ? 'kit' : 'kits'}
            </Badge>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {brandingKits.map((kit) => (
            <div
              key={kit.id}
              className="group relative bg-card rounded-lg overflow-hidden border border-border hover:border-primary hover:shadow-lg transition-all"
            >
              {/* Preview Container */}
              <div className="aspect-square bg-muted overflow-hidden relative">
                {kit.logo ? (
                  <img
                    src={`data:image/${kit.logo.format.toLowerCase()};base64,${kit.logo.data}`}
                    alt={kit.prompt || 'Generated logo'}
                    className="w-full h-full object-contain p-4 group-hover:scale-105 transition-transform duration-300"
                    onError={(e) => {
                      const target = e.target as HTMLImageElement
                      target.src = '/placeholder-image.png'
                    }}
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center">
                    <Palette className="h-16 w-16 text-muted-foreground" />
                  </div>
                )}
                
                {/* Color Palette Overlay */}
                {kit.colors && kit.colors.length > 0 && (
                  <div className="absolute bottom-0 left-0 right-0 bg-black/50 p-2">
                    <div className="flex gap-1 justify-center">
                      {kit.colors.slice(0, 5).map((color, idx) => (
                        <div
                          key={idx}
                          className="w-6 h-6 rounded border border-white/30"
                          style={{ backgroundColor: color }}
                          title={color}
                        />
                      ))}
                      {kit.colors.length > 5 && (
                        <div className="w-6 h-6 rounded border border-white/30 bg-white/20 flex items-center justify-center text-xs text-white">
                          +{kit.colors.length - 5}
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
              
              {/* Info Section */}
              <div className="p-4 space-y-3">
                {/* Prompt */}
                <div>
                  <p className="text-sm font-medium text-foreground line-clamp-2 mb-1">
                    {kit.prompt || 'No prompt'}
                  </p>
                  {kit.style && (
                    <Badge variant="outline" className="text-xs">
                      {kit.style}
                    </Badge>
                  )}
                </div>

                {/* Date */}
                <div className="flex items-center text-xs text-muted-foreground">
                  <Calendar className="h-3 w-3 mr-1" />
                  {formatDate(kit.created_at)}
                </div>

                {/* Action Buttons */}
                <div className="flex gap-2 pt-2 border-t border-border">
                  {kit.logo && (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => downloadImage(
                        kit.logo!.data,
                        `logo-${kit.id}.${kit.logo!.format.toLowerCase()}`,
                        kit.logo!.format
                      )}
                      className="flex-1 h-8 text-xs"
                    >
                      <Download className="h-3 w-3 mr-1" />
                      Logo
                    </Button>
                  )}
                  {kit.color_palette && (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => downloadImage(
                        kit.color_palette!.data,
                        `palette-${kit.id}.${kit.color_palette!.format.toLowerCase()}`,
                        kit.color_palette!.format
                      )}
                      className="flex-1 h-8 text-xs"
                    >
                      <Download className="h-3 w-3 mr-1" />
                      Palette
                    </Button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

