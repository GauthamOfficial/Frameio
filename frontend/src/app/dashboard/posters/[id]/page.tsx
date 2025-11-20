"use client"

import { useState, useEffect } from "react"
import { useParams, useRouter } from "next/navigation"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog"
import { Image, Calendar, Download, ExternalLink, Loader2, Trash2, ArrowLeft } from "lucide-react"
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

export default function PosterPreviewPage() {
  const params = useParams()
  const router = useRouter()
  const posterId = params.id as string
  const [poster, setPoster] = useState<Poster | null>(null)
  const [loading, setLoading] = useState(true)
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [isDeleting, setIsDeleting] = useState(false)
  const { getToken } = useAuth()
  const { showError, showSuccess } = useToastHelpers()

  useEffect(() => {
    if (posterId) {
      fetchPoster()
    }
  }, [posterId])

  const fetchPoster = async () => {
    try {
      setLoading(true)
      const token = await getToken()
      const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'
      const baseUrl = apiBase.replace(/\/$/, '')
      
      const response = await fetch(`${baseUrl}/api/ai/ai-poster/posters/${posterId}/`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        },
        credentials: 'include'
      })

      if (!response.ok) {
        throw new Error('Failed to fetch poster')
      }

      const data = await response.json()
      if (data.success && data.poster) {
        // Ensure image_url is absolute
        const posterData = data.poster
        if (posterData.image_url && !posterData.image_url.startsWith('http')) {
          const fixedUrl = posterData.image_url.startsWith('/') 
            ? `${baseUrl}${posterData.image_url}`
            : `${baseUrl}/${posterData.image_url}`
          posterData.image_url = fixedUrl
        }
        setPoster(posterData)
      } else {
        throw new Error('Poster not found')
      }
    } catch (error) {
      console.error('Error fetching poster:', error)
      showError('Failed to load poster')
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
    } catch (error) {
      return 'Invalid date'
    }
  }

  const handleDownload = async () => {
    if (!poster) return
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

  const handleDeleteClick = () => {
    setDeleteDialogOpen(true)
  }

  const handleDeleteConfirm = async () => {
    if (!poster) return

    setIsDeleting(true)
    try {
      const token = await getToken()
      const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'
      const baseUrl = apiBase.replace(/\/$/, '')
      
      const response = await fetch(`${baseUrl}/api/ai/ai-poster/posters/${poster.id}/delete/`, {
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

      showSuccess('Poster deleted successfully')
      router.push('/dashboard')
    } catch (error) {
      console.error('Error deleting poster:', error)
      showError(error instanceof Error ? error.message : 'Failed to delete poster')
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

  if (!poster) {
    return (
      <div className="container mx-auto p-6">
        <Card>
          <CardContent className="flex flex-col items-center justify-center h-64">
            <p className="text-muted-foreground mb-4">Poster not found</p>
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
          <CardTitle>Poster Preview</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Full Poster Image */}
          <div className="w-full rounded-lg overflow-hidden border border-border bg-muted flex items-center justify-center">
            <img
              src={poster.image_url}
              alt={poster.caption || poster.prompt || 'Generated poster'}
              className="max-w-full max-h-[600px] w-auto h-auto object-contain"
              onError={(e) => {
                const target = e.target as HTMLImageElement
                if (poster.image_url && !poster.image_url.startsWith('http')) {
                  const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'
                  const baseUrl = apiBase.replace(/\/$/, '')
                  const fixedUrl = poster.image_url.startsWith('/') 
                    ? `${baseUrl}${poster.image_url}`
                    : `${baseUrl}/${poster.image_url}`
                  target.src = fixedUrl
                }
              }}
            />
          </div>

          {/* Caption Section */}
          <div className="space-y-4">
            <div>
              <h3 className="text-sm font-semibold text-foreground mb-2">Caption</h3>
              <p className="text-sm text-foreground bg-muted p-4 rounded-md border border-border">
                {poster.full_caption || poster.caption || 'No caption available'}
              </p>
            </div>

            {/* Prompt */}
            {poster.prompt && (
              <div>
                <h3 className="text-sm font-semibold text-foreground mb-2">Prompt</h3>
                <p className="text-sm text-muted-foreground bg-muted p-4 rounded-md border border-border">
                  {poster.prompt}
                </p>
              </div>
            )}

            {/* Metadata */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <h3 className="text-sm font-semibold text-foreground mb-2">Created</h3>
                <p className="text-sm text-muted-foreground flex items-center">
                  <Calendar className="h-4 w-4 mr-1" />
                  {formatDate(poster.created_at)}
                </p>
              </div>
              <div>
                <h3 className="text-sm font-semibold text-foreground mb-2">Aspect Ratio</h3>
                <p className="text-sm text-muted-foreground">
                  {poster.aspect_ratio || '1:1'}
                </p>
              </div>
            </div>

            {/* Hashtags */}
            {poster.hashtags && poster.hashtags.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold text-foreground mb-2">Hashtags</h3>
                <div className="flex flex-wrap gap-2">
                  {poster.hashtags.map((tag, idx) => (
                    <Badge key={idx} variant="outline" className="text-xs">
                      {tag.replace('#', '')}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex gap-2 pt-4 border-t border-border">
              <Button
                variant="outline"
                onClick={handleDownload}
                className="flex-1"
              >
                <Download className="h-4 w-4 mr-2" />
                Download
              </Button>
              <Button
                variant="outline"
                onClick={() => window.open(poster.image_url, '_blank')}
              >
                <ExternalLink className="h-4 w-4 mr-2" />
                Open in New Tab
              </Button>
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
            <DialogTitle>Delete Poster</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete this poster? This action cannot be undone.
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



