"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { 
  Wand2, 
  Download, 
  RefreshCw,
  AlertCircle,
  CheckCircle,
  Loader2,
  Upload,
  Copy,
  Hash,
  MessageSquare,
  Sparkles,
  Share2,
  ExternalLink,
  Facebook,
  Twitter,
  Instagram,
  Mail
} from "lucide-react"
import React, { useState, useRef } from "react"
import { useUser, useAuth } from '@clerk/nextjs'

interface GenerationResult {
  success: boolean
  message?: string
  image_path?: string
  image_url?: string
  filename?: string
  error?: string
  text_added?: string
  style?: string
  caption?: string
  full_caption?: string
  hashtags?: string[]
  emoji?: string
  call_to_action?: string
}

export default function EnhancedPosterGenerator() {
  // Authentication
  const { user } = useUser()
  const { getToken } = useAuth()
  
  // State management
  const [isGenerating, setIsGenerating] = useState(false)
  const [prompt, setPrompt] = useState("")
  const [aspectRatio, setAspectRatio] = useState("4:5")
  const [result, setResult] = useState<GenerationResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  
  // Image upload functionality
  const [uploadedImage, setUploadedImage] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  
  // Caption and hashtag functionality
  const [showCaption, setShowCaption] = useState(false)
  const [copiedItem, setCopiedItem] = useState<string | null>(null)

  const generatePoster = async () => {
    if (!prompt.trim()) {
      setError('Please enter a prompt')
      return
    }

    setIsGenerating(true)
    setError(null)
    setResult(null)

    try {
      console.log('🚀 Starting poster generation...')
      console.log('Prompt:', prompt)
      console.log('Aspect Ratio:', aspectRatio)
      console.log('Has uploaded image:', !!uploadedImage)
      console.log('User authenticated:', !!user)

      // Get authentication token
      const token = await getToken()
      const authHeaders = token ? { 'Authorization': `Bearer ${token}` } : {}
      
      // Add user context for branding (development)
      if (user?.id) {
        authHeaders['X-Dev-User-ID'] = user.id
      }

      let response;

      if (uploadedImage) {
        // Generate poster with uploaded image
        const formData = new FormData()
        formData.append('image', uploadedImage)
        formData.append('prompt', prompt)
        formData.append('aspect_ratio', aspectRatio)

        response = await fetch('http://localhost:8000/api/ai/ai-poster/edit_poster/', {
          method: 'POST',
          headers: authHeaders,
          body: formData
        })
      } else {
        // Generate poster from text only
        response = await fetch('http://localhost:8000/api/ai/ai-poster/generate_poster/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...authHeaders
          },
          body: JSON.stringify({
            prompt: prompt,
            aspect_ratio: aspectRatio
          })
        })
      }

      console.log('Response status:', response.status)
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || `HTTP ${response.status}`)
      }

      const data = await response.json()
      console.log('Generation result:', data)
      console.log('Caption data available:', {
        caption: data.caption,
        full_caption: data.full_caption,
        hashtags: data.hashtags,
        emoji: data.emoji,
        call_to_action: data.call_to_action
      })

      if (data.success) {
        setResult(data)
        setError(null)
        console.log('✅ Poster generated successfully!')
        console.log('Image URL:', data.image_url)
        console.log('Image Path:', data.image_path)
        console.log('Full Image URL:', data.image_url.startsWith('http') ? data.image_url : `http://localhost:8000${data.image_url}`)
      } else {
        throw new Error(data.error || 'Generation failed')
      }
    } catch (err) {
      console.error('❌ Generation failed:', err)
      setError(err instanceof Error ? err.message : 'Generation failed')
      setResult(null)
    } finally {
      setIsGenerating(false)
    }
  }

  const downloadImage = async () => {
    if (result?.image_url) {
      try {
        // The backend now provides full URLs, but keep fallback for safety
        const downloadUrl = result.image_url.startsWith('http') 
          ? result.image_url 
          : `http://localhost:8000${result.image_url}`
        
        // Fetch the image as a blob to force download
        const response = await fetch(downloadUrl)
        const blob = await response.blob()
        
        // Create a blob URL and download
        const blobUrl = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = blobUrl
        link.download = result.filename || 'generated-poster.png'
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        
        // Clean up the blob URL
        window.URL.revokeObjectURL(blobUrl)
      } catch (error) {
        console.error('Download failed:', error)
        // Fallback to direct link
        const link = document.createElement('a')
        link.href = result.image_url.startsWith('http') 
          ? result.image_url 
          : `http://localhost:8000${result.image_url}`
        link.download = result.filename || 'generated-poster.png'
        link.target = '_blank'
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
      }
    }
  }

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      setUploadedImage(file)
      const url = URL.createObjectURL(file)
      setPreviewUrl(url)
      setError(null)
    }
  }

  const clearUploadedImage = () => {
    setUploadedImage(null)
    setPreviewUrl(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const copyToClipboard = async (text: string, type: string) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopiedItem(type)
      setTimeout(() => setCopiedItem(null), 2000)
    } catch (err) {
      console.error('Failed to copy text: ', err)
    }
  }

  const copyHashtags = async () => {
    if (result?.hashtags) {
      const hashtagText = result.hashtags.join(' ')
      await copyToClipboard(hashtagText, 'hashtags')
    }
  }

  const copyFullCaption = async () => {
    if (result?.full_caption) {
      await copyToClipboard(result.full_caption, 'caption')
    }
  }

  const shareToSocialMedia = (platform: string) => {
    if (!result?.image_url || !result?.full_caption) return

    const imageUrl = result.image_url.startsWith('http') 
      ? result.image_url 
      : `http://localhost:8000${result.image_url}`
    
    const shareText = result.full_caption
    const shareUrl = imageUrl

    let shareLink = ''
    
    switch (platform) {
      case 'facebook':
        shareLink = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(shareUrl)}&quote=${encodeURIComponent(shareText)}`
        break
      case 'twitter':
        shareLink = `https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}&url=${encodeURIComponent(shareUrl)}`
        break
      case 'instagram':
        // Instagram doesn't support direct sharing via URL, so we'll copy to clipboard
        const instagramText = `${shareText}\n\n${shareUrl}`
        copyToClipboard(instagramText, 'instagram')
        return
      case 'whatsapp':
        shareLink = `https://wa.me/?text=${encodeURIComponent(`${shareText}\n\n${shareUrl}`)}`
        break
      case 'email':
        shareLink = `mailto:?subject=${encodeURIComponent('Check out this AI-generated poster!')}&body=${encodeURIComponent(`${shareText}\n\n${shareUrl}`)}`
        break
      default:
        return
    }
    
    if (shareLink) {
      window.open(shareLink, '_blank', 'width=600,height=400')
    }
  }

  const shareToClipboard = async () => {
    if (!result?.image_url || !result?.full_caption) return

    const imageUrl = result.image_url.startsWith('http') 
      ? result.image_url 
      : `http://localhost:8000${result.image_url}`
    
    const shareText = `${result.full_caption}\n\n${imageUrl}`
    await copyToClipboard(shareText, 'share')
  }

  return (
    <div className="container mx-auto p-6 max-w-6xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-center mb-2">AI Poster Generator</h1>
        <p className="text-center text-gray-600">Generate beautiful textile posters from text prompts or upload an image to create posters based on your textile designs using Gemini 2.5 Flash</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input Section */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <span>Generate Poster</span>
              {isGenerating && <Loader2 className="h-4 w-4 animate-spin" />}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="prompt">Describe your poster</Label>
              <Input
                id="prompt"
                placeholder="e.g., Beautiful silk saree for Diwali celebrations with gold accents"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                disabled={isGenerating}
                className="mt-1"
              />
            </div>

            <div>
              <Label htmlFor="image-upload">Upload Reference Image (Optional)</Label>
              <div className="mt-1">
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleImageUpload}
                  disabled={isGenerating}
                  className="hidden"
                  id="image-upload"
                />
                <div className="flex gap-2">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => fileInputRef.current?.click()}
                    disabled={isGenerating}
                    className="flex-1"
                  >
                    <Upload className="mr-2 h-4 w-4" />
                    {uploadedImage ? 'Change Image' : 'Choose Image'}
                  </Button>
                  {uploadedImage && (
                    <Button
                      type="button"
                      variant="outline"
                      onClick={clearUploadedImage}
                      disabled={isGenerating}
                    >
                      Clear
                    </Button>
                  )}
                </div>
                {uploadedImage && (
                  <p className="text-sm text-gray-600 mt-2">
                    Selected: {uploadedImage.name}
                  </p>
                )}
              </div>
            </div>

            <div>
              <Label htmlFor="aspect-ratio">Aspect Ratio</Label>
              <select
                id="aspect-ratio"
                value={aspectRatio}
                onChange={(e) => setAspectRatio(e.target.value)}
                disabled={isGenerating}
                className="mt-1 w-full p-2 border border-gray-300 rounded-md"
              >
                <option value="1:1">Square (1:1)</option>
                <option value="4:5">Portrait (4:5)</option>
                <option value="5:4">Portrait Wide (5:4)</option>
                <option value="3:2">Classic (3:2)</option>
                <option value="2:3">Classic Tall (2:3)</option>
                <option value="16:9">Landscape (16:9)</option>
                <option value="9:16">Vertical (9:16)</option>
              </select>
            </div>

            <Button 
              onClick={generatePoster} 
              disabled={isGenerating || !prompt.trim()}
              className="w-full"
            >
              {isGenerating ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  {uploadedImage ? 'Generating from Image...' : 'Generating...'}
                </>
              ) : (
                <>
                  <RefreshCw className="mr-2 h-4 w-4" />
                  {uploadedImage ? 'Generate from Image' : 'Generate Poster'}
                </>
              )}
            </Button>

            {error && (
              <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-md text-red-700">
                <AlertCircle className="h-4 w-4" />
                <span className="text-sm">{error}</span>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Result Section */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              Generated Poster
              {result?.success && <CheckCircle className="h-4 w-4 text-green-500" />}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isGenerating && (
              <div className="flex flex-col items-center justify-center h-64 bg-gray-50 rounded-md">
                <Loader2 className="h-8 w-8 animate-spin text-blue-500 mb-4" />
                <p className="text-gray-600">Generating your poster...</p>
                <p className="text-sm text-gray-500 mt-2">This may take 60-120 seconds</p>
              </div>
            )}

            {result?.success && result.image_url && (
              <div className="space-y-4">
                <div className="relative w-full" style={{ aspectRatio: aspectRatio.replace(':', ' / ') }}>
                  <img
                    src={result.image_url.startsWith('http') ? result.image_url : `http://localhost:8000${result.image_url}`}
                    alt="Generated poster"
                    className="absolute inset-0 w-full h-full rounded-md border object-contain"
                    onError={(e) => {
                      console.error('Image load error:', e)
                      console.error('Image URL:', result.image_url)
                      setError('Failed to load generated image. Please try again.')
                    }}
                  />
                </div>
                

                <div className="space-y-2">
                  <Button onClick={downloadImage} className="w-full">
                    <Download className="mr-2 h-4 w-4" />
                    Download Image
                  </Button>
                  
                  {/* Share Button */}
                  <Button 
                    onClick={shareToClipboard} 
                    variant="outline" 
                    className="w-full"
                  >
                    <Share2 className="mr-2 h-4 w-4" />
                    {copiedItem === 'share' ? 'Copied to Clipboard!' : 'Share Poster & Caption'}
                  </Button>
                </div>

                {/* AI Generated Caption and Hashtags Section */}
                {result && (
                  <div className="mt-6 space-y-4">
                    <div className="flex items-center justify-between">
                      <h3 className="text-lg font-semibold flex items-center gap-2">
                        <Sparkles className="h-5 w-5 text-purple-500" />
                        AI Generated Content
                      </h3>
                      <div className="flex gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => {
                            const content = `${result.caption || result.full_caption || ''}\n\n${result.hashtags ? result.hashtags.join(' ') : ''}`
                            copyToClipboard(content, 'all')
                          }}
                          className="text-xs"
                        >
                          <Copy className="mr-1 h-3 w-3" />
                          {copiedItem === 'all' ? 'Copied!' : 'Copy All'}
                        </Button>
                      </div>
                    </div>

                    <div className="space-y-4">
                        {/* Caption Section */}
                        {(result.caption || result.full_caption) ? (
                          <Card className="border-l-4 border-l-blue-500">
                            <CardHeader className="pb-3">
                              <CardTitle className="text-sm flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                  <MessageSquare className="h-4 w-4 text-blue-500" />
                                  Caption
                                </div>
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={copyFullCaption}
                                  className="h-6 px-2"
                                >
                                  <Copy className="h-3 w-3" />
                                </Button>
                              </CardTitle>
                            </CardHeader>
                            <CardContent className="pt-0">
                              <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-4 rounded-lg border">
                                <p className="text-sm text-gray-800 leading-relaxed">{result.caption || result.full_caption}</p>
                                {result.full_caption && result.caption && result.full_caption !== result.caption && (
                                  <div className="mt-3 pt-3 border-t border-blue-200">
                                    <p className="text-xs text-blue-600 font-medium mb-2">Extended Caption:</p>
                                    <p className="text-sm text-gray-700">{result.full_caption}</p>
                                  </div>
                                )}
                              </div>
                              <div className="mt-3 flex gap-2">
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={copyFullCaption}
                                  className="flex-1"
                                >
                                  <Copy className="mr-2 h-3 w-3" />
                                  {copiedItem === 'caption' ? 'Copied!' : 'Copy Caption'}
                                </Button>
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => shareToClipboard()}
                                  className="flex-1"
                                >
                                  <Share2 className="mr-2 h-3 w-3" />
                                  Share
                                </Button>
                              </div>
                            </CardContent>
                          </Card>
                        ) : (
                          <Card className="bg-gray-50 border-gray-200">
                            <CardHeader className="pb-3">
                              <CardTitle className="text-sm flex items-center gap-2">
                                <MessageSquare className="h-4 w-4" />
                                Caption
                              </CardTitle>
                            </CardHeader>
                            <CardContent className="pt-0">
                              <p className="text-sm text-gray-600">
                                No caption generated. This might be due to caption service issues.
                              </p>
                            </CardContent>
                          </Card>
                        )}

                        {/* Hashtags Section */}
                        {result.hashtags && result.hashtags.length > 0 ? (
                          <Card className="border-l-4 border-l-green-500">
                            <CardHeader className="pb-3">
                              <CardTitle className="text-sm flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                  <Hash className="h-4 w-4 text-green-500" />
                                  Hashtags ({result.hashtags.length})
                                </div>
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={copyHashtags}
                                  className="h-6 px-2"
                                >
                                  <Copy className="h-3 w-3" />
                                </Button>
                              </CardTitle>
                            </CardHeader>
                            <CardContent className="pt-0">
                              <div className="bg-gradient-to-r from-green-50 to-emerald-50 p-4 rounded-lg border">
                                <div className="flex flex-wrap gap-2">
                                  {result.hashtags.map((hashtag, index) => (
                                    <span
                                      key={index}
                                      className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-xs font-medium hover:bg-green-200 transition-colors cursor-pointer"
                                      onClick={() => copyToClipboard(hashtag, 'hashtag')}
                                    >
                                      {hashtag}
                                    </span>
                                  ))}
                                </div>
                              </div>
                              <div className="mt-3 flex gap-2">
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={copyHashtags}
                                  className="flex-1"
                                >
                                  <Copy className="mr-2 h-3 w-3" />
                                  {copiedItem === 'hashtags' ? 'Copied!' : 'Copy All Hashtags'}
                                </Button>
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => {
                                    const hashtagText = result.hashtags.join(' ')
                                    copyToClipboard(hashtagText, 'hashtags')
                                  }}
                                  className="flex-1"
                                >
                                  <Share2 className="mr-2 h-3 w-3" />
                                  Share
                                </Button>
                              </div>
                            </CardContent>
                          </Card>
                        ) : (
                          <Card className="bg-gray-50 border-gray-200">
                            <CardHeader className="pb-3">
                              <CardTitle className="text-sm flex items-center gap-2">
                                <Hash className="h-4 w-4" />
                                Hashtags
                              </CardTitle>
                            </CardHeader>
                            <CardContent className="pt-0">
                              <p className="text-sm text-gray-600">
                                No hashtags generated.
                              </p>
                            </CardContent>
                          </Card>
                        )}

                        {/* Call to Action */}
                        {result.call_to_action && (
                          <Card>
                            <CardHeader className="pb-3">
                              <CardTitle className="text-sm">Call to Action</CardTitle>
                            </CardHeader>
                            <CardContent className="pt-0">
                              <p className="text-sm text-gray-700">{result.call_to_action}</p>
                            </CardContent>
                          </Card>
                        )}

                        {/* Social Media Sharing */}
                        <Card className="border-l-4 border-l-purple-500">
                          <CardHeader className="pb-3">
                            <CardTitle className="text-sm flex items-center gap-2">
                              <Share2 className="h-4 w-4 text-purple-500" />
                              Share to Social Media
                            </CardTitle>
                          </CardHeader>
                          <CardContent className="pt-0">
                            <div className="bg-gradient-to-r from-purple-50 to-pink-50 p-4 rounded-lg border mb-4">
                              <p className="text-xs text-gray-600 mb-3">Share your poster and AI-generated content:</p>
                              <div className="grid grid-cols-2 gap-2">
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => shareToSocialMedia('facebook')}
                                  className="flex items-center gap-2 hover:bg-blue-50 hover:border-blue-300"
                                >
                                  <Facebook className="h-4 w-4 text-blue-600" />
                                  Facebook
                                </Button>
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => shareToSocialMedia('twitter')}
                                  className="flex items-center gap-2 hover:bg-blue-50 hover:border-blue-300"
                                >
                                  <Twitter className="h-4 w-4 text-blue-400" />
                                  Twitter
                                </Button>
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => shareToSocialMedia('instagram')}
                                  className="flex items-center gap-2 hover:bg-pink-50 hover:border-pink-300"
                                >
                                  <Instagram className="h-4 w-4 text-pink-600" />
                                  {copiedItem === 'instagram' ? 'Copied!' : 'Instagram'}
                                </Button>
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => shareToSocialMedia('whatsapp')}
                                  className="flex items-center gap-2 hover:bg-green-50 hover:border-green-300"
                                >
                                  <ExternalLink className="h-4 w-4 text-green-600" />
                                  WhatsApp
                                </Button>
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => shareToSocialMedia('email')}
                                  className="flex items-center gap-2 col-span-2 hover:bg-gray-50 hover:border-gray-300"
                                >
                                  <Mail className="h-4 w-4 text-gray-600" />
                                  Email
                                </Button>
                              </div>
                            </div>
                            <div className="text-center">
                              <Button
                                variant="default"
                                size="sm"
                                onClick={shareToClipboard}
                                className="w-full"
                              >
                                <Share2 className="mr-2 h-4 w-4" />
                                {copiedItem === 'share' ? 'Copied to Clipboard!' : 'Copy All Content to Clipboard'}
                              </Button>
                            </div>
                          </CardContent>
                        </Card>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            {!isGenerating && !result && (
              <div className="flex flex-col items-center justify-center h-64 bg-gray-50 rounded-md">
                <div className="text-center">
                  <div className="text-4xl mb-4">🎨</div>
                  <p className="text-gray-600">Your generated poster will appear here</p>
                  <p className="text-sm text-gray-500 mt-2">Enter a prompt and click Generate Poster</p>
                </div>
              </div>
            )}

            {/* Preview uploaded image */}
            {previewUrl && !result && !isGenerating && (
              <div className="space-y-4">
                <div className="relative w-full" style={{ aspectRatio: aspectRatio.replace(':', ' / ') }}>
                  <img
                    src={previewUrl}
                    alt="Uploaded reference image"
                    className="absolute inset-0 w-full h-full rounded-md border object-contain"
                  />
                </div>
                <p className="text-sm text-gray-600 text-center">
                  Reference image - Will be used to generate your poster
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

    </div>
  )
}