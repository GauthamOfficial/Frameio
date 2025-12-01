"use client"

import { useState, useEffect } from "react"
import { useParams, useRouter } from "next/navigation"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog"
import { Calendar, Download, Loader2, Trash2, ArrowLeft } from "lucide-react"
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

export default function BrandingKitPreviewPage() {
  const params = useParams()
  const router = useRouter()
  const kitId = params.id as string
  const [kit, setKit] = useState<BrandingKit | null>(null)
  const [loading, setLoading] = useState(true)
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [isDeleting, setIsDeleting] = useState(false)
  const { getToken } = useAuth()
  const { showError, showSuccess } = useToastHelpers()

  useEffect(() => {
    if (kitId) {
      fetchBrandingKit()
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [kitId])

  const fetchBrandingKit = async () => {
    try {
      setLoading(true)
      const token = await getToken()
      const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'
      const baseUrl = apiBase.replace(/\/$/, '')
      
      const response = await fetch(`${baseUrl}/api/ai/branding-kit/${kitId}/`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        },
        credentials: 'include'
      })

      if (!response.ok) {
        throw new Error('Failed to fetch branding kit')
      }

      const data = await response.json()
      if (data.success && data.branding_kit) {
        setKit(data.branding_kit)
      } else {
        throw new Error('Branding kit not found')
      }
    } catch (error) {
      console.error('Error fetching branding kit:', error)
      showError('Failed to load branding kit')
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
        return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
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

  const handleDeleteClick = () => {
    setDeleteDialogOpen(true)
  }

  const handleDeleteConfirm = async () => {
    if (!kit) return

    setIsDeleting(true)
    try {
      const token = await getToken()
      const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'
      const baseUrl = apiBase.replace(/\/$/, '')
      
      const response = await fetch(`${baseUrl}/api/ai/branding-kit/${kit.id}/delete/`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        },
        credentials: 'include'
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: 'Failed to delete branding kit' }))
        throw new Error(errorData.error || 'Failed to delete branding kit')
      }

      showSuccess('Branding kit deleted successfully')
      router.push('/dashboard')
    } catch (error) {
      console.error('Error deleting branding kit:', error)
      showError(error instanceof Error ? error.message : 'Failed to delete branding kit')
    } finally {
      setIsDeleting(false)
      setDeleteDialogOpen(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (!kit) {
    return (
      <div className="container mx-auto p-6">
        <Card>
          <CardContent className="flex flex-col items-center justify-center h-64">
            <p className="text-muted-foreground mb-4">Branding kit not found</p>
            <Button onClick={() => router.push('/dashboard')} variant="outline">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Dashboard
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="container mx-auto p-6 max-w-4xl">
      <div className="mb-4">
        <Button
          variant="ghost"
          onClick={() => router.push('/dashboard')}
          className="mb-4"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Dashboard
        </Button>
      </div>

      <Card className="textile-hover textile-shadow">
        <CardHeader>
          <CardTitle>Branding Kit Preview</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Logo and Color Palette */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Logo */}
            {kit.logo && (
              <div className="space-y-3">
                <h3 className="text-sm font-semibold text-foreground">Logo</h3>
                <div className="w-full aspect-square bg-muted rounded-lg overflow-hidden border border-border flex items-center justify-center p-4">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={`data:image/${kit.logo.format.toLowerCase()};base64,${kit.logo.data}`}
                    alt={kit.prompt || 'Generated logo'}
                    className="max-w-full max-h-full w-auto h-auto object-contain"
                  />
                </div>
                <Button
                  variant="outline"
                  onClick={() => downloadImage(
                    kit.logo!.data,
                    `logo-${kit.id}.${kit.logo!.format.toLowerCase()}`,
                    kit.logo!.format
                  )}
                  className="w-full"
                >
                  <Download className="h-4 w-4 mr-2" />
                  Download Logo
                </Button>
              </div>
            )}

            {/* Color Palette */}
            {kit.color_palette && (
              <div className="space-y-3">
                <h3 className="text-sm font-semibold text-foreground">Color Palette</h3>
                <div className="w-full aspect-square bg-muted rounded-lg overflow-hidden border border-border flex items-center justify-center p-4">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={`data:image/${kit.color_palette.format.toLowerCase()};base64,${kit.color_palette.data}`}
                    alt="Color palette"
                    className="max-w-full max-h-full w-auto h-auto object-contain"
                  />
                </div>
                <Button
                  variant="outline"
                  onClick={() => downloadImage(
                    kit.color_palette!.data,
                    `palette-${kit.id}.${kit.color_palette!.format.toLowerCase()}`,
                    kit.color_palette!.format
                  )}
                  className="w-full"
                >
                  <Download className="h-4 w-4 mr-2" />
                  Download Palette
                </Button>
              </div>
            )}
          </div>

          {/* Details Section */}
          <div className="space-y-4">
            {/* Prompt */}
            {kit.prompt && (
              <div>
                <h3 className="text-sm font-semibold text-foreground mb-2">Prompt</h3>
                <p className="text-sm text-muted-foreground bg-muted p-4 rounded-md border border-border">
                  {kit.prompt}
                </p>
              </div>
            )}

            {/* Style */}
            {kit.style && (
              <div>
                <h3 className="text-sm font-semibold text-foreground mb-2">Style</h3>
                <p className="text-sm text-muted-foreground bg-muted p-4 rounded-md border border-border">
                  {kit.style}
                </p>
              </div>
            )}

            {/* Colors */}
            {kit.colors && kit.colors.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold text-foreground mb-2">Colors</h3>
                <div className="flex flex-wrap gap-2">
                  {kit.colors.map((color, idx) => (
                    <div
                      key={idx}
                      className="flex items-center gap-2 p-2 rounded-md border border-border bg-muted"
                    >
                      <div
                        className="w-8 h-8 rounded border border-border"
                        style={{ backgroundColor: color }}
                        title={color}
                      />
                      <span className="text-sm text-foreground">{color}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Metadata */}
            <div>
              <h3 className="text-sm font-semibold text-foreground mb-2">Created</h3>
              <p className="text-sm text-muted-foreground flex items-center">
                <Calendar className="h-4 w-4 mr-1" />
                {formatDate(kit.created_at)}
              </p>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-2 pt-4 border-t border-border">
              <Button
                variant="outline"
                onClick={handleDeleteClick}
                className="text-destructive hover:text-destructive hover:bg-destructive/10"
              >
                <Trash2 className="h-4 w-4 mr-2" />
                Delete
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

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
              onClick={() => setDeleteDialogOpen(false)}
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
    </div>
  )
}

