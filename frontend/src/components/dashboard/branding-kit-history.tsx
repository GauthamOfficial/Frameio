"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog"
import { Palette, Calendar, Download, Loader2, RefreshCw, Trash2 } from "lucide-react"
import { useAuth } from "@/hooks/useAuth"
import { useToastHelpers } from "@/components/common"
import { useRouter } from "next/navigation"
import { apiGet, apiDelete } from "@/utils/api"

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
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [kitToDelete, setKitToDelete] = useState<BrandingKit | null>(null)
  const [isDeleting, setIsDeleting] = useState(false)
  const router = useRouter()
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
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const fetchBrandingKits = async () => {
    try {
      setLoading(true)
      const token = await getToken()
      const url = limit 
        ? `/api/ai/branding-kit/history/?limit=${limit}`
        : `/api/ai/branding-kit/history/`
      
      console.log('Fetching branding kits from:', url)
      
      try {
        const data = await apiGet(url, {}, token) as { success?: boolean; results?: BrandingKit[]; count?: number; error?: string } | BrandingKit[]
        
        console.log('Branding kits response data:', data)
        
        // Handle different response formats
        if (Array.isArray(data)) {
          console.log(`Setting ${data.length} branding kits (array format)`)
          setBrandingKits(data)
        } else if ('success' in data && data.success && data.results) {
          console.log(`Setting ${data.results.length} branding kits`)
          setBrandingKits(data.results)
        } else if ('results' in data && Array.isArray(data.results)) {
          console.log(`Setting ${data.results.length} branding kits (results format)`)
          setBrandingKits(data.results)
        } else if ('success' in data && data.success === false) {
          console.warn('API returned success: false', data.error)
          setBrandingKits([])
        } else {
          console.warn('Unexpected response format:', data)
          setBrandingKits([])
        }
      } catch (error) {
        // Handle network errors gracefully
        const errorMessage = error instanceof Error ? error.message : 'Unknown error'
        if (errorMessage.includes('Failed to fetch') || errorMessage.includes('NetworkError') || errorMessage.includes('CORS')) {
          console.warn('Backend may not be accessible, showing empty state')
          setBrandingKits([])
          return
        }
        throw error
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
    } catch {
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

  const handleDeleteClick = (kit: BrandingKit) => {
    setKitToDelete(kit)
    setDeleteDialogOpen(true)
  }

  const handleDeleteConfirm = async () => {
    if (!kitToDelete) return

    setIsDeleting(true)
    try {
      const token = await getToken()
      
      await apiDelete(`/api/ai/branding-kit/${kitToDelete.id}/delete/`, {}, token)

      // Remove the branding kit from the list
      setBrandingKits(prev => prev.filter(k => k.id !== kitToDelete.id))
      setDeleteDialogOpen(false)
      setKitToDelete(null)
    } catch (error) {
      console.error('Error deleting branding kit:', error)
      showError(error instanceof Error ? error.message : 'Failed to delete branding kit')
    } finally {
      setIsDeleting(false)
    }
  }

  const handleDeleteCancel = () => {
    setDeleteDialogOpen(false)
    setKitToDelete(null)
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
        <div className="grid grid-cols-1 min-[475px]:grid-cols-2 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3 sm:gap-4">
          {brandingKits.map((kit) => (
            <div
              key={kit.id}
              className="group relative bg-card rounded-lg overflow-hidden border border-border hover:border-primary hover:shadow-lg transition-all"
            >
              {/* Preview Container - Clickable */}
              <div 
                className="aspect-square bg-muted overflow-hidden relative cursor-pointer"
                onClick={() => router.push(`/dashboard/branding-kits/${kit.id}`)}
              >
                {kit.logo ? (
                  /* eslint-disable-next-line @next/next/no-img-element */
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
              <div className="p-3 sm:p-4 space-y-2 sm:space-y-3" onClick={(e) => e.stopPropagation()}>
                {/* Prompt */}
                <div>
                  <p className="text-xs sm:text-sm font-medium text-foreground line-clamp-2 mb-1">
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
                  <Calendar className="h-3 w-3 mr-1 shrink-0" />
                  <span className="truncate">{formatDate(kit.created_at)}</span>
                </div>

                {/* Action Buttons */}
                <div className="flex gap-1.5 sm:gap-2 pt-2 border-t border-border" onClick={(e) => e.stopPropagation()}>
                  {kit.logo && (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => downloadImage(
                        kit.logo!.data,
                        `logo-${kit.id}.${kit.logo!.format.toLowerCase()}`,
                        kit.logo!.format
                      )}
                      className="flex-1 h-7 sm:h-8 text-xs px-1.5 sm:px-2"
                    >
                      <Download className="h-3 w-3 mr-1 shrink-0" />
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
                      className="flex-1 h-7 sm:h-8 text-xs px-1.5 sm:px-2"
                    >
                      <Download className="h-3 w-3 mr-1 shrink-0" />
                      Palette
                    </Button>
                  )}
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleDeleteClick(kit)}
                    className="h-7 sm:h-8 w-7 sm:w-8 px-0 text-destructive hover:text-destructive hover:bg-destructive/10"
                    title="Delete branding kit"
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
            <DialogTitle>Delete Branding Kit</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete this branding kit? This action cannot be undone.
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

